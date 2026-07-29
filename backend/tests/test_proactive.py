import pytest

from agent import planner, proactive
from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from tasks import automation_store


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


def _make_automation(db_session, task="résume le fichier a.txt", schedule="0 9 * * *"):
    user = get_or_create_user(db_session)
    return automation_store.create_automation(db_session, user_id=user.id, name="test", schedule=schedule, task=task)


def test_run_automation_executes_plan_and_records_success(db_session, sandbox, monkeypatch):
    (sandbox / "a.txt").write_text("contenu a", encoding="utf-8")
    monkeypatch.setattr(
        proactive.planner,
        "build_plan",
        lambda goal: planner.ProposedPlan(
            steps=[planner.PlannedStep(tool="file_reader", description="lire a", args={"path": "a.txt"})]
        ),
    )

    automation = _make_automation(db_session)
    plan = proactive.run_automation(db_session, automation)

    assert plan is not None
    assert plan.status == "done"
    reloaded = automation_store.get_automation(db_session, automation.id)
    assert reloaded.last_run_status == "done"
    assert reloaded.last_run_plan_id == plan.id
    assert reloaded.last_run_at is not None


def test_run_automation_blocks_tool_requiring_validation(db_session, monkeypatch):
    """Garde-fou sécurité (phase3.md) : une automatisation proactive ne peut
    jamais auto-approuver un tool nécessitant une validation humaine."""
    monkeypatch.setattr(
        proactive.planner,
        "build_plan",
        lambda goal: planner.ProposedPlan(
            steps=[planner.PlannedStep(tool="code_executor", description="exécute", args={"code": "print(1)"})]
        ),
    )

    automation = _make_automation(db_session, task="exécute du code")
    plan = proactive.run_automation(db_session, automation)

    assert plan is None
    reloaded = automation_store.get_automation(db_session, automation.id)
    assert reloaded.last_run_status == "failed"
    assert reloaded.last_run_plan_id is None


def test_run_automation_records_failure_when_planner_errors(db_session, monkeypatch):
    def _boom(goal):
        raise planner.PlannerError("réponse LLM non conforme")

    monkeypatch.setattr(proactive.planner, "build_plan", _boom)

    automation = _make_automation(db_session)
    plan = proactive.run_automation(db_session, automation)

    assert plan is None
    reloaded = automation_store.get_automation(db_session, automation.id)
    assert reloaded.last_run_status == "failed"
