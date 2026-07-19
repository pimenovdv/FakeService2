import pytest
from fastapi.testclient import TestClient
from main import app
from routers.webhooks import webhook_store

client = TestClient(app)

def test_webhook_lifecycle():
    # Clear store before test
    webhook_store.clear()

    webhook_id = "test_webhook_123"

    # Get initially should be empty
    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["payloads"] == []

    # Post JSON payload
    payload1 = {"event": "user.created", "user_id": 1}
    response = client.post(f"/api/webhooks/{webhook_id}", json=payload1)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Post plain text payload
    payload2 = "Plain text event"
    response = client.post(f"/api/webhooks/{webhook_id}", content=payload2)
    assert response.status_code == 200

    # Get payloads and check
    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["webhook_id"] == webhook_id
    assert len(data["payloads"]) == 2
    assert data["payloads"][0] == payload1
    assert data["payloads"][1] == payload2

    # Clear payloads
    response = client.delete(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Get payloads again, should be empty
    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200
    assert response.json()["payloads"] == []
