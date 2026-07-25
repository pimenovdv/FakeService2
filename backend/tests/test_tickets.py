from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_tickets_flow():
    # 1. Create a new ticket
    payload = {
        "subject": "Help with login",
        "description": "I cannot login with my new password.",
        "user_id": "user-456"
    }
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    assert data["subject"] == "Help with login"
    assert data["description"] == "I cannot login with my new password."
    assert data["user_id"] == "user-456"
    assert data["status"] == "open"
    assert "created_at" in data

    ticket_id = data["ticket_id"]

    # 2. Get tickets and verify it's in the list
    response = client.get("/api/tickets")
    assert response.status_code == 200
    tickets_list = response.json()
    assert isinstance(tickets_list, list)
    assert any(t["ticket_id"] == ticket_id for t in tickets_list)

    # 3. Update the ticket status
    update_payload = {"status": "in_progress"}
    response = client.patch(f"/api/tickets/{ticket_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket_id
    assert data["status"] == "in_progress"

    # 4. Verify 404 for non-existent ticket update
    response = client.patch("/api/tickets/invalid-id-123", json={"status": "closed"})
    assert response.status_code == 404
