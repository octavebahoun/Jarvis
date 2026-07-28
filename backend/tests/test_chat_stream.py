from agent.controller import STREAM_ERROR_MARKER


def test_chat_stream_returns_full_reply_as_text(client, session_id):
    response = client.post("/chat/stream", json={"message": "Salut Jarvis", "session_id": session_id})

    assert response.status_code == 200
    assert response.text == "Réponse de test."


def test_chat_stream_persists_exchange_in_short_term_memory(client, session_id):
    client.post("/chat/stream", json={"message": "Salut Jarvis", "session_id": session_id})

    response = client.get("/memory", params={"type": "short_term", "session_id": session_id})

    assert response.status_code == 200
    items = response.json()["items"]
    assert [{"role": item["role"], "content": item["content"]} for item in items] == [
        {"role": "user", "content": "Salut Jarvis"},
        {"role": "assistant", "content": "Réponse de test."},
    ]


def test_chat_stream_reports_error_marker_when_llm_fails(client, session_id, monkeypatch):
    from agent import controller

    def _boom(messages):
        raise RuntimeError("clé API OpenAI invalide")
        yield  # pragma: no cover - fait de _boom un générateur, jamais atteint

    monkeypatch.setattr(controller.reasoning, "stream_reply", _boom)

    response = client.post("/chat/stream", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    assert STREAM_ERROR_MARKER in response.text


def test_chat_stream_rejects_empty_message(client, session_id):
    response = client.post("/chat/stream", json={"message": "", "session_id": session_id})

    assert response.status_code == 422
