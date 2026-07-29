import pytest

from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from tasks import task_store
from tasks.worker import _run_plan


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    import tools.file_reader as file_reader_module

    monkeypatch.setattr(file_reader_module.settings, "sandbox_path", str(tmp_path))
    return tmp_path


def test_run_plan_executes_and_returns_final_status(sandbox):
    init_db()
    (sandbox / "a.txt").write_text("contenu", encoding="utf-8")

    db = SessionLocal()
    try:
        user = get_or_create_user(db)
        plan = task_store.create_plan(
            db,
            user_id=user.id,
            session_id="s",
            goal="g",
            steps=[{"tool": "file_reader", "description": "lire a", "args": {"path": "a.txt"}}],
        )
        task_store.set_plan_status(db, plan, "approved")
        plan_id = plan.id
    finally:
        db.close()

    status = _run_plan(plan_id)

    assert status == "done"


def test_run_plan_raises_for_unknown_plan():
    with pytest.raises(ValueError):
        _run_plan("does-not-exist")
