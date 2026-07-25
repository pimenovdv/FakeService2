import pytest
from fastapi.testclient import TestClient
from main import app
from routers.user_tasks import MOCK_USER_TASKS

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_tasks():
    MOCK_USER_TASKS.clear()
    yield
    MOCK_USER_TASKS.clear()

def test_create_user_task():
    response = client.post("/api/user-tasks", json={"title": "Test Task", "description": "This is a test task"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Check if it was added to store
    assert len(MOCK_USER_TASKS) == 1
    assert list(MOCK_USER_TASKS.keys())[0] == data["id"]

def test_create_user_task_validation():
    # Empty title should fail
    response = client.post("/api/user-tasks", json={"title": ""})
    assert response.status_code == 422

    # Missing title should fail
    response = client.post("/api/user-tasks", json={"description": "No title"})
    assert response.status_code == 422

def test_list_user_tasks():
    client.post("/api/user-tasks", json={"title": "Task 1", "completed": True})
    client.post("/api/user-tasks", json={"title": "Task 2", "completed": False})

    response = client.get("/api/user-tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Check default sorting (newest first)
    assert data[0]["title"] == "Task 2"
    assert data[1]["title"] == "Task 1"

def test_list_user_tasks_filtered():
    client.post("/api/user-tasks", json={"title": "Task 1", "completed": True})
    client.post("/api/user-tasks", json={"title": "Task 2", "completed": False})
    client.post("/api/user-tasks", json={"title": "Task 3", "completed": True})

    response = client.get("/api/user-tasks?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["completed"] for task in data)

    response = client.get("/api/user-tasks?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is False
    assert data[0]["title"] == "Task 2"

def test_get_user_task():
    create_response = client.post("/api/user-tasks", json={"title": "Task to get"})
    task_id = create_response.json()["id"]

    response = client.get(f"/api/user-tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Task to get"

def test_get_nonexistent_user_task():
    response = client.get("/api/user-tasks/nonexistent-id")
    assert response.status_code == 404

def test_update_user_task():
    create_response = client.post("/api/user-tasks", json={"title": "Original Title"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/api/user-tasks/{task_id}", json={
        "title": "Updated Title",
        "completed": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True

    # Check get reflects the update
    get_response = client.get(f"/api/user-tasks/{task_id}")
    assert get_response.json()["title"] == "Updated Title"
    assert get_response.json()["completed"] is True

def test_update_nonexistent_user_task():
    response = client.patch("/api/user-tasks/nonexistent-id", json={"title": "New Title"})
    assert response.status_code == 404

def test_update_user_task_validation():
    create_response = client.post("/api/user-tasks", json={"title": "Original Title"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/api/user-tasks/{task_id}", json={"title": ""})
    assert response.status_code == 422

def test_delete_user_task():
    create_response = client.post("/api/user-tasks", json={"title": "Task to delete"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/api/user-tasks/{task_id}")
    assert response.status_code == 200

    # Should not exist anymore
    get_response = client.get(f"/api/user-tasks/{task_id}")
    assert get_response.status_code == 404
    assert len(MOCK_USER_TASKS) == 0

def test_delete_nonexistent_user_task():
    response = client.delete("/api/user-tasks/nonexistent-id")
    assert response.status_code == 404
