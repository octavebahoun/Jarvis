def test_get_profile_creates_default_user(client):
    response = client.get("/profile")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "default"
    assert isinstance(body["tech_stack"], list)
    assert isinstance(body["preferences"], dict)


def test_update_profile_persists_changes(client):
    response = client.put(
        "/profile",
        json={"tech_stack": ["Python", "FastAPI", "Next.js"], "preferences": {"tone": "direct"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tech_stack"] == ["Python", "FastAPI", "Next.js"]
    assert body["preferences"]["tone"] == "direct"

    # Le profil relu doit refléter la mise à jour (persistance PostgreSQL).
    reread = client.get("/profile")
    assert reread.json()["tech_stack"] == ["Python", "FastAPI", "Next.js"]
