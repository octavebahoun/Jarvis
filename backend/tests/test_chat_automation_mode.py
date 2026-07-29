def _scheduled_intent(controller, recurring=False):
    return controller.schedule_intent.ScheduleIntent(
        scheduled=True,
        recurring=recurring,
        cron="0 9 * * *" if recurring else "32 14 29 7 *",
        name="Recherche IA",
        task="cherche les dernières nouvelles sur l'IA",
    )


def test_chat_creates_automation_when_scheduling_intent_detected(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(
        controller.schedule_intent, "detect_schedule_intent", lambda goal, now: _scheduled_intent(controller)
    )

    response = client.post(
        "/chat", json={"message": "cherche les news IA dans 2 minutes", "session_id": session_id}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "automation"
    assert body["automation"]["name"] == "Recherche IA"
    assert body["automation"]["task"] == "cherche les dernières nouvelles sur l'IA"
    assert body["automation"]["active"] is True


def test_chat_takes_priority_over_plan_when_both_would_apply(client, session_id, monkeypatch):
    """Une intention de planification prime sur un plan immédiat — cf.
    agent/controller.py : _maybe_create_automation est appelé avant
    _maybe_create_plan."""
    from agent import controller

    monkeypatch.setattr(
        controller.schedule_intent, "detect_schedule_intent", lambda goal, now: _scheduled_intent(controller)
    )
    monkeypatch.setattr(
        controller.planner,
        "build_plan",
        lambda goal: controller.planner.ProposedPlan(
            steps=[controller.planner.PlannedStep(tool="web_search", description="x", args={})]
        ),
    )

    response = client.post(
        "/chat", json={"message": "cherche les news IA dans 2 minutes", "session_id": session_id}
    )

    assert response.json()["type"] == "automation"


def test_chat_falls_back_to_plan_when_no_scheduling_intent(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(
        controller.planner,
        "build_plan",
        lambda goal: controller.planner.ProposedPlan(
            steps=[controller.planner.PlannedStep(tool="web_search", description="x", args={})]
        ),
    )

    response = client.post("/chat", json={"message": "cherche les news IA", "session_id": session_id})

    assert response.json()["type"] == "plan"


def test_chat_falls_back_to_reply_when_schedule_intent_detection_fails(client, session_id, monkeypatch):
    from agent import controller

    def _boom(goal, now):
        raise RuntimeError("réponse LLM non conforme")

    monkeypatch.setattr(controller.schedule_intent, "detect_schedule_intent", _boom)

    response = client.post("/chat", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    assert response.json()["type"] == "reply"


def test_chat_stream_yields_automation_marker(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(
        controller.schedule_intent, "detect_schedule_intent", lambda goal, now: _scheduled_intent(controller)
    )

    response = client.post(
        "/chat/stream", json={"message": "cherche les news IA dans 2 minutes", "session_id": session_id}
    )

    assert response.status_code == 200
    assert response.text.startswith(controller.AUTOMATION_MARKER)
    automation_id = response.text[len(controller.AUTOMATION_MARKER) :]
    assert len(automation_id) > 0


def test_get_automation_returns_created_automation(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(
        controller.schedule_intent, "detect_schedule_intent", lambda goal, now: _scheduled_intent(controller)
    )

    created = client.post(
        "/chat", json={"message": "cherche les news IA dans 2 minutes", "session_id": session_id}
    ).json()

    response = client.get(f"/automations/{created['automation']['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Recherche IA"


def test_get_automation_returns_404_for_unknown_id(client):
    response = client.get("/automations/does-not-exist")

    assert response.status_code == 404
