from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_outbox():
    # Make sure we start with a clean state for each test
    client.delete("/api/email/outbox")

def test_send_email():
    payload = {
        "to": "test@example.com",
        "subject": "Test Subject",
        "body": "Test Body"
    }
    response = client.post("/api/email/send", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["to"] == payload["to"]
    assert data["subject"] == payload["subject"]
    assert data["body"] == payload["body"]
    assert "sent_at" in data

    # Verify outbox has the email
    get_response = client.get("/api/email/outbox")
    assert get_response.status_code == 200
    outbox_data = get_response.json()
    assert len(outbox_data) == 1
    assert outbox_data[0]["id"] == data["id"]

def test_get_empty_outbox():
    response = client.get("/api/email/outbox")
    assert response.status_code == 200
    assert response.json() == []

def test_clear_outbox():
    # Send an email first
    payload = {
        "to": "test2@example.com",
        "subject": "Test Subject 2",
        "body": "Test Body 2"
    }
    client.post("/api/email/send", json=payload)

    # Verify it is in outbox
    response = client.get("/api/email/outbox")
    assert len(response.json()) == 1

    # Clear outbox
    del_response = client.delete("/api/email/outbox")
    assert del_response.status_code == 204

    # Verify it is empty
    response = client.get("/api/email/outbox")
    assert len(response.json()) == 0

def test_invalid_email():
    payload = {
        "to": "not-an-email",
        "subject": "Test Subject",
        "body": "Test Body"
    }
    response = client.post("/api/email/send", json=payload)
    assert response.status_code == 422
