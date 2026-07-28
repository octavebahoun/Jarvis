def test_short_term_memory_without_session_id_returns_empty(client):
    response = client.get("/memory", params={"type": "short_term"})

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_short_term_memory_unknown_session_returns_empty(client, session_id):
    response = client.get("/memory", params={"type": "short_term", "session_id": session_id})

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_long_term_memory_default_type(client):
    response = client.get("/memory")

    assert response.status_code == 200
    assert "items" in response.json()
