import uuid
from datetime import datetime, timezone

import pytest

from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from tasks import automation_store, task_store


@pytest.fixture
def db_session():
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_automation_defaults_to_active(db_session):
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="Veille tech", schedule="0 9 * * 1-5", task="cherche les news IA"
    )

    assert automation.active is True
    assert automation.last_run_at is None
    assert automation.last_run_status is None


def test_list_automations_scoped_to_user(db_session):
    # Noms uniques : la base est partagée entre tous les tests de la session
    # (comme le reste du projet, cf. tests/conftest.py), pas de reset entre tests.
    name_a, name_b = f"a-{uuid.uuid4()}", f"b-{uuid.uuid4()}"
    user = get_or_create_user(db_session)
    automation_store.create_automation(db_session, user_id=user.id, name=name_a, schedule="0 9 * * *", task="t")
    automation_store.create_automation(db_session, user_id=user.id, name=name_b, schedule="0 10 * * *", task="t")

    names = [a.name for a in automation_store.list_automations(db_session, user.id) if a.name in {name_a, name_b}]

    assert names == [name_a, name_b]


def test_get_automation_returns_none_for_unknown_id(db_session):
    assert automation_store.get_automation(db_session, "does-not-exist") is None


def test_set_automation_active_toggles_and_persists(db_session):
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="a", schedule="0 9 * * *", task="t"
    )

    automation_store.set_automation_active(db_session, automation, False)

    reloaded = automation_store.get_automation(db_session, automation.id)
    assert reloaded.active is False


def test_record_automation_run_updates_last_run_fields(db_session):
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="a", schedule="0 9 * * *", task="t"
    )
    plan = task_store.create_plan(db_session, user_id=user.id, session_id="s", goal="g", steps=[])
    ran_at = datetime.now(timezone.utc)

    automation_store.record_automation_run(db_session, automation, "done", plan.id, ran_at)

    reloaded = automation_store.get_automation(db_session, automation.id)
    assert reloaded.last_run_status == "done"
    assert reloaded.last_run_plan_id == plan.id
    assert reloaded.last_run_at is not None
