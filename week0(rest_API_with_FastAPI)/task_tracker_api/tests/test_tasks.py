def test_create_task(client):
    response = client.post("/tasks", json={"title": "Buy milk", "completed": False})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy milk"
    assert "id" in data


def test_create_task_invalid_data(client):
    response = client.post("/tasks", json={"completed": True})  # missing required "title"
    assert response.status_code == 422


def test_get_task(client):
    created = client.post("/tasks", json={"title": "Walk dog", "completed": False}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Walk dog"


def test_get_task_not_found(client):
    response = client.get("/tasks/999999")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Draft", "completed": False}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": "Final", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Final"


def test_update_task_not_found(client):
    response = client.put("/tasks/999999", json={"title": "Ghost", "completed": False})
    assert response.status_code == 404


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temp", "completed": False}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 200

    follow_up = client.get(f"/tasks/{created['id']}")
    assert follow_up.status_code == 404