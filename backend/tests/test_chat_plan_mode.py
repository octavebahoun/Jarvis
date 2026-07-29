def _make_plan_with_one_step(controller):
    return controller.planner.ProposedPlan(
        steps=[
            controller.planner.PlannedStep(
                tool="file_reader",
                description="Lire x.txt",
                args={"path": "x.txt"},
            )
        ]
    )


def test_chat_returns_plan_when_planner_proposes_steps(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(controller.planner, "build_plan", lambda goal: _make_plan_with_one_step(controller))

    response = client.post("/chat", json={"message": "Analyse x.txt", "session_id": session_id})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "plan"
    assert body["plan"]["status"] == "pending"
    assert body["plan"]["goal"] == "Analyse x.txt"
    assert body["plan"]["steps"][0]["tool"] == "file_reader"


def test_chat_returns_reply_type_for_simple_message(client, session_id):
    response = client.post("/chat", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "reply"
    assert body["reply"] == "Réponse de test."


def test_chat_stream_yields_plan_marker_when_planner_proposes_steps(client, session_id, monkeypatch):
    from agent import controller

    monkeypatch.setattr(controller.planner, "build_plan", lambda goal: _make_plan_with_one_step(controller))

    response = client.post("/chat/stream", json={"message": "Analyse x.txt", "session_id": session_id})

    assert response.status_code == 200
    assert response.text.startswith(controller.PLAN_MARKER)
    plan_id = response.text[len(controller.PLAN_MARKER) :]
    assert len(plan_id) > 0


def test_chat_stream_still_streams_text_for_simple_message(client, session_id):
    response = client.post("/chat/stream", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    assert response.text == "Réponse de test."


def test_chat_falls_back_to_reply_when_planner_fails(client, session_id, monkeypatch):
    from agent import controller

    def _boom(goal):
        raise RuntimeError("réponse du planner non conforme")

    monkeypatch.setattr(controller.planner, "build_plan", _boom)

    response = client.post("/chat", json={"message": "Fais quelque chose", "session_id": session_id})

    assert response.status_code == 200
    assert response.json()["type"] == "reply"
