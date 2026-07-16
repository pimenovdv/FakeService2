import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from routers.tasks import tasks_db

client = TestClient(app)

def test_start_task():
    response = client.post("/api/tasks")
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    assert data["task_id"] in tasks_db

def test_get_task_status_lifecycle():
    # Start task
    response = client.post("/api/tasks")
    assert response.status_code == 202
    task_id = response.json()["task_id"]

    # In FastAPI's TestClient, BackgroundTasks are executed inline synchronously
    # after the response is returned. So the task will already be completed.
    status_response = client.get(f"/api/tasks/{task_id}")
    assert status_response.status_code == 200
    assert status_response.json() == {"task_id": task_id, "status": "completed"}

    # We can also test the pending state by manually setting it
    tasks_db[task_id] = "pending"
    status_response = client.get(f"/api/tasks/{task_id}")
    assert status_response.status_code == 200
    assert status_response.json() == {"task_id": task_id, "status": "pending"}

def test_get_task_status_not_found():
    response = client.get("/api/tasks/nonexistent-task-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
