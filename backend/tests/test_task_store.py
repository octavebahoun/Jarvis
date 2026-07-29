import pytest

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


def test_create_plan_persists_steps_in_order(db_session):
    user = get_or_create_user(db_session)
    plan = task_store.create_plan(
        db_session,
        user_id=user.id,
        session_id="session-1",
        goal="Analyse ce fichier",
        steps=[
            {"tool": "file_reader", "description": "Lire le fichier", "args": {"path": "a.txt"}},
            {"tool": "web_search", "description": "Chercher un contexte", "args": {"query": "x"}},
        ],
    )

    assert plan.status == "pending"
    assert [s.tool for s in plan.steps] == ["file_reader", "web_search"]
    assert plan.steps[0].step_order == 0
    assert plan.steps[1].step_order == 1


def test_get_plan_returns_none_for_unknown_id(db_session):
    assert task_store.get_plan(db_session, "does-not-exist") is None


def test_set_plan_status_updates_and_persists(db_session):
    user = get_or_create_user(db_session)
    plan = task_store.create_plan(db_session, user_id=user.id, session_id="s", goal="g", steps=[])

    task_store.set_plan_status(db_session, plan, "approved")

    reloaded = task_store.get_plan(db_session, plan.id)
    assert reloaded.status == "approved"


def test_set_step_result_updates_status_and_result(db_session):
    user = get_or_create_user(db_session)
    plan = task_store.create_plan(
        db_session,
        user_id=user.id,
        session_id="s",
        goal="g",
        steps=[{"tool": "file_reader", "description": "lire", "args": {"path": "a.txt"}}],
    )
    step = plan.steps[0]

    task_store.set_step_result(db_session, step, status="done", result="contenu lu")

    reloaded = task_store.get_plan(db_session, plan.id)
    assert reloaded.steps[0].status == "done"
    assert reloaded.steps[0].result == "contenu lu"
