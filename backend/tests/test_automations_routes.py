def test_create_automation_returns_created_automation(client):
    response = client.post(
        "/automations",
        json={"name": "Veille tech", "schedule": "0 9 * * 1-5", "task": "cherche les news IA"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Veille tech"
    assert body["schedule"] == "0 9 * * 1-5"
    assert body["active"] is True
    assert body["last_run_status"] is None


def test_create_automation_rejects_invalid_cron(client):
    response = client.post(
        "/automations",
        json={"name": "invalide", "schedule": "pas un cron", "task": "t"},
    )

    assert response.status_code == 422


def test_list_automations_returns_created_automations(client):
    client.post("/automations", json={"name": "a", "schedule": "0 9 * * *", "task": "t"})
    client.post("/automations", json={"name": "b", "schedule": "0 10 * * *", "task": "t"})

    response = client.get("/automations")

    assert response.status_code == 200
    names = [automation["name"] for automation in response.json()]
    assert "a" in names
    assert "b" in names


def test_toggle_automation_flips_active_state(client):
    created = client.post("/automations", json={"name": "a", "schedule": "0 9 * * *", "task": "t"}).json()
    assert created["active"] is True

    response = client.put(f"/automations/{created['id']}/toggle")

    assert response.status_code == 200
    assert response.json()["active"] is False


def test_toggle_automation_returns_404_for_unknown_id(client):
    response = client.put("/automations/does-not-exist/toggle")

    assert response.status_code == 404
