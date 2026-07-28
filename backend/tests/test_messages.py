import pytest
from fastapi.testclient import TestClient
from main import app
from routers.messages import messages_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_messages_db():
    messages_db.clear()
    yield
    messages_db.clear()

def test_get_messages_empty():
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.json() == []

def test_send_message():
    message_data = {
        "content": "Hello World!",
        "recipient_id": "user123"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "Hello World!"
    assert data["recipient_id"] == "user123"
    assert data["sender_id"] == "system"
    assert "timestamp" in data

    # Verify it was added
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_delete_message():
    # Create a message first
    message_data = {
        "content": "Message to delete",
        "recipient_id": "user456"
    }
    create_response = client.post("/api/messages", json=message_data)
    message_id = create_response.json()["id"]

    # Delete the message
    delete_response = client.delete(f"/api/messages/{message_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "Message deleted"}

    # Verify it was deleted
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.json() == []

def test_delete_message_not_found():
    response = client.delete("/api/messages/nonexistent-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}
