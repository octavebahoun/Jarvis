def test_chat_returns_reply_for_session(client, session_id):
    response = client.post("/chat", json={"message": "Salut Jarvis", "session_id": session_id})

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["reply"] == "Réponse de test."


def test_chat_persists_exchange_in_short_term_memory(client, session_id):
    client.post("/chat", json={"message": "Salut Jarvis", "session_id": session_id})

    response = client.get("/memory", params={"type": "short_term", "session_id": session_id})

    assert response.status_code == 200
    items = response.json()["items"]
    assert [{"role": item["role"], "content": item["content"]} for item in items] == [
        {"role": "user", "content": "Salut Jarvis"},
        {"role": "assistant", "content": "Réponse de test."},
    ]
    assert all(isinstance(item["ts"], (int, float)) for item in items)


def test_chat_keeps_history_across_messages_in_same_session(client, session_id):
    client.post("/chat", json={"message": "Premier message", "session_id": session_id})
    client.post("/chat", json={"message": "Deuxième message", "session_id": session_id})

    response = client.get("/memory", params={"type": "short_term", "session_id": session_id})

    assert len(response.json()["items"]) == 4


def test_chat_rejects_empty_message(client, session_id):
    response = client.post("/chat", json={"message": "", "session_id": session_id})

    assert response.status_code == 422


def test_chat_returns_502_when_llm_unavailable(client, session_id, monkeypatch):
    from agent import controller

    def _boom(messages):
        raise RuntimeError("clé API OpenAI invalide")

    monkeypatch.setattr(controller.reasoning, "generate_reply", _boom)

    response = client.post("/chat", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 502


def test_chat_degrades_gracefully_when_vector_search_fails(client, session_id, monkeypatch):
    from agent import controller

    def _boom(query, user_id, n_results=5):
        raise TimeoutError("téléchargement du modèle d'embedding local expiré")

    monkeypatch.setattr(controller.vector_store, "search_memory", _boom)

    response = client.post("/chat", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    assert response.json()["reply"] == "Réponse de test."


def test_chat_degrades_gracefully_when_vector_add_fails(client, session_id, monkeypatch):
    from agent import controller

    def _boom(memory_id, text, metadata):
        raise TimeoutError("téléchargement du modèle d'embedding local expiré")

    monkeypatch.setattr(controller.vector_store, "add_memory", _boom)

    response = client.post("/chat", json={"message": "Salut", "session_id": session_id})

    assert response.status_code == 200
    assert response.json()["reply"] == "Réponse de test."
