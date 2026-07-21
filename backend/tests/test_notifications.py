from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_notifications():
    response = client.get("/api/notifications?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_id"] == "test_user"

def test_mark_notification_as_read():
    # Fetch notifications to get a valid ID
    response = client.get("/api/notifications?user_id=test_user")
    data = response.json()
    assert len(data) > 0
    notification_id = data[0]["id"]

    # Mark as read
    response = client.put(f"/api/notifications/{notification_id}/read")
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["id"] == notification_id
    assert updated_data["is_read"] is True

def test_get_unread_notifications():
    # Make sure we have some unread notifications
    client.get("/api/notifications?user_id=test_user2")

    # Filter by unread
    response = client.get("/api/notifications?user_id=test_user2&unread_only=true")
    assert response.status_code == 200
    data = response.json()
    assert all(not n["is_read"] for n in data)

def test_mark_notification_not_found():
    response = client.put("/api/notifications/invalid-id/read")
    assert response.status_code == 404
