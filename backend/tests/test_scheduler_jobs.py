from datetime import datetime, timezone

import pytest

from agent import planner, proactive
from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from scheduler.jobs import _run_tick
from tasks import automation_store


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    import tools.file_reader as file_reader_module

    monkeypatch.setattr(file_reader_module.settings, "sandbox_path", str(tmp_path))
    return tmp_path


def test_run_tick_executes_due_automations_and_returns_count(sandbox, monkeypatch):
    monkeypatch.setattr(
        proactive.planner,
        "build_plan",
        lambda goal: planner.ProposedPlan(
            steps=[planner.PlannedStep(tool="file_reader", description="lire a", args={"path": "a.txt"})]
        ),
    )

    init_db()
    (sandbox / "a.txt").write_text("contenu", encoding="utf-8")

    db = SessionLocal()
    try:
        user = get_or_create_user(db)
        automation = automation_store.create_automation(
            db, user_id=user.id, name="a", schedule="0 9 * * *", task="lis a.txt"
        )
        automation_id = automation.id
    finally:
        db.close()

    # >= 1 et pas ==1 : la base est partagée entre tous les tests de la
    # session (cf. tests/conftest.py), d'autres automatisations actives à
    # "0 9 * * *" peuvent déjà exister — ce qui compte ici est que la nôtre a
    # bien été exécutée (vérifié ci-dessous).
    due_count = _run_tick(datetime(2026, 7, 29, 9, 0, tzinfo=timezone.utc))

    assert due_count >= 1
    db = SessionLocal()
    try:
        reloaded = automation_store.get_automation(db, automation_id)
        assert reloaded.last_run_status == "done"
    finally:
        db.close()


def test_run_tick_returns_zero_when_nothing_due():
    init_db()
    assert _run_tick(datetime(2026, 7, 29, 9, 1, tzinfo=timezone.utc)) == 0
