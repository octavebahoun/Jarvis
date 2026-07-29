from db.session import SessionLocal, init_db
from identity.profile import get_or_create_user
from tasks import task_store


def _create_test_plan(status="pending"):
    init_db()
    db = SessionLocal()
    try:
        user = get_or_create_user(db)
        plan = task_store.create_plan(
            db,
            user_id=user.id,
            session_id="s",
            goal="g",
            steps=[{"tool": "file_reader", "description": "lire", "args": {"path": "a.txt"}}],
        )
        if status != "pending":
            task_store.set_plan_status(db, plan, status)
        return plan.id
    finally:
        db.close()


def test_get_task_returns_plan(client):
    plan_id = _create_test_plan()

    response = client.get(f"/tasks/{plan_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == plan_id
    assert body["status"] == "pending"
    assert body["steps"][0]["tool"] == "file_reader"


def test_get_task_returns_404_for_unknown_plan(client):
    response = client.get("/tasks/does-not-exist")

    assert response.status_code == 404


def test_approve_task_triggers_execution(client, monkeypatch):
    from api.routes import tasks as tasks_route_module

    captured = {}
    monkeypatch.setattr(
        tasks_route_module.execute_plan_task,
        "delay",
        lambda plan_id: captured.setdefault("plan_id", plan_id),
    )

    plan_id = _create_test_plan()

    response = client.post(f"/tasks/{plan_id}/approve")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert captured["plan_id"] == plan_id


def test_approve_task_rejects_already_approved_plan(client, monkeypatch):
    from api.routes import tasks as tasks_route_module

    monkeypatch.setattr(tasks_route_module.execute_plan_task, "delay", lambda plan_id: None)

    plan_id = _create_test_plan(status="approved")

    response = client.post(f"/tasks/{plan_id}/approve")

    assert response.status_code == 409


def test_approve_task_returns_404_for_unknown_plan(client, monkeypatch):
    from api.routes import tasks as tasks_route_module

    monkeypatch.setattr(tasks_route_module.execute_plan_task, "delay", lambda plan_id: None)

    response = client.post("/tasks/does-not-exist/approve")

    assert response.status_code == 404
