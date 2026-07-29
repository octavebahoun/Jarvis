from datetime import datetime, timezone

import pytest

from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from scheduler import registry
from tasks import automation_store


@pytest.fixture
def db_session():
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _due_ids(db_session, now):
    return [a.id for a in registry.due_automations(db_session, now)]


def test_due_automations_matches_cron_expression(db_session):
    # Vérifie par ID, pas par comptage global : la base est partagée entre
    # tous les tests de la session (cf. tests/conftest.py), d'autres
    # automatisations actives peuvent déjà exister.
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="tous les jours à 9h", schedule="0 9 * * *", task="t"
    )

    now_match = datetime(2026, 7, 29, 9, 0, tzinfo=timezone.utc)
    now_miss = datetime(2026, 7, 29, 9, 1, tzinfo=timezone.utc)

    assert automation.id in _due_ids(db_session, now_match)
    assert automation.id not in _due_ids(db_session, now_miss)


def test_due_automations_ignores_seconds(db_session):
    """Le tick tourne une fois par minute, jamais pile à la seconde 0 —
    seule la minute compte (secondes/microsecondes ignorées)."""
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="a", schedule="0 9 * * *", task="t"
    )

    now = datetime(2026, 7, 29, 9, 0, 42, tzinfo=timezone.utc)

    assert automation.id in _due_ids(db_session, now)


def test_due_automations_ignores_inactive(db_session):
    user = get_or_create_user(db_session)
    automation = automation_store.create_automation(
        db_session, user_id=user.id, name="a", schedule="0 9 * * *", task="t"
    )
    automation_store.set_automation_active(db_session, automation, False)

    now = datetime(2026, 7, 29, 9, 0, tzinfo=timezone.utc)

    assert automation.id not in _due_ids(db_session, now)
