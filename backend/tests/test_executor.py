import pytest

from agent import executor
from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from tasks import task_store


@pytest.fixture
def db_session():
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    import tools.file_reader as file_reader_module

    monkeypatch.setattr(file_reader_module.settings, "sandbox_path", str(tmp_path))
    return tmp_path


def _make_plan(db_session, steps):
    user = get_or_create_user(db_session)
    return task_store.create_plan(db_session, user_id=user.id, session_id="s", goal="g", steps=steps)


def test_execute_plan_raises_if_not_approved(db_session, sandbox):
    plan = _make_plan(db_session, steps=[])

    with pytest.raises(executor.PlanNotApprovedError):
        executor.execute_plan(db_session, plan)


def test_execute_plan_runs_all_steps_and_marks_plan_done(db_session, sandbox):
    (sandbox / "a.txt").write_text("contenu a", encoding="utf-8")
    (sandbox / "b.txt").write_text("contenu b", encoding="utf-8")

    plan = _make_plan(
        db_session,
        steps=[
            {"tool": "file_reader", "description": "lire a", "args": {"path": "a.txt"}},
            {"tool": "file_reader", "description": "lire b", "args": {"path": "b.txt"}},
        ],
    )
    task_store.set_plan_status(db_session, plan, "approved")

    result = executor.execute_plan(db_session, plan)

    assert result.status == "done"
    assert [s.status for s in result.steps] == ["done", "done"]
    assert result.steps[0].result == "contenu a"
    assert result.steps[1].result == "contenu b"


def test_execute_plan_generates_summary_from_step_results(db_session, sandbox, monkeypatch):
    monkeypatch.setattr(executor.reasoning, "generate_reply", lambda messages: "Voici le résumé du fichier a.")

    (sandbox / "a.txt").write_text("contenu a", encoding="utf-8")
    plan = _make_plan(
        db_session,
        steps=[{"tool": "file_reader", "description": "lire a", "args": {"path": "a.txt"}}],
    )
    task_store.set_plan_status(db_session, plan, "approved")

    result = executor.execute_plan(db_session, plan)

    assert result.status == "done"
    assert result.summary == "Voici le résumé du fichier a."


def test_execute_plan_stays_done_when_summary_generation_fails(db_session, sandbox, monkeypatch):
    def _boom(messages):
        raise RuntimeError("LLM indisponible")

    monkeypatch.setattr(executor.reasoning, "generate_reply", _boom)

    (sandbox / "a.txt").write_text("contenu a", encoding="utf-8")
    plan = _make_plan(
        db_session,
        steps=[{"tool": "file_reader", "description": "lire a", "args": {"path": "a.txt"}}],
    )
    task_store.set_plan_status(db_session, plan, "approved")

    result = executor.execute_plan(db_session, plan)

    assert result.status == "done"  # les résultats bruts par étape restent disponibles
    assert result.summary is None


def test_execute_plan_stops_on_first_failure(db_session, sandbox):
    (sandbox / "a.txt").write_text("contenu a", encoding="utf-8")

    plan = _make_plan(
        db_session,
        steps=[
            {"tool": "file_reader", "description": "fichier manquant", "args": {"path": "manquant.txt"}},
            {"tool": "file_reader", "description": "lire a", "args": {"path": "a.txt"}},
        ],
    )
    task_store.set_plan_status(db_session, plan, "approved")

    result = executor.execute_plan(db_session, plan)

    assert result.status == "failed"
    assert result.steps[0].status == "failed"
    assert result.steps[0].error is not None
    assert result.steps[1].status == "pending"  # jamais exécutée
