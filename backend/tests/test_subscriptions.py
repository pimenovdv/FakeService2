from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_subscription():
    payload = {
        "plan_id": "premium_plan",
        "user_id": "user123"
    }
    response = client.post("/api/subscriptions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "subscription_id" in data
    assert data["plan_id"] == "premium_plan"
    assert data["user_id"] == "user123"
    assert data["status"] == "active"
    assert "created_at" in data

def test_get_subscription_success():
    # First, create a subscription
    payload = {
        "plan_id": "basic_plan",
        "user_id": "user456"
    }
    post_response = client.post("/api/subscriptions", json=payload)
    sub_id = post_response.json()["subscription_id"]

    # Then, retrieve it
    get_response = client.get(f"/api/subscriptions/{sub_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["subscription_id"] == sub_id
    assert data["plan_id"] == "basic_plan"
    assert data["status"] == "active"

def test_get_subscription_not_found():
    response = client.get("/api/subscriptions/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Subscription not found"

def test_cancel_subscription_success():
    # First, create a subscription
    payload = {
        "plan_id": "pro_plan",
        "user_id": "user789"
    }
    post_response = client.post("/api/subscriptions", json=payload)
    sub_id = post_response.json()["subscription_id"]

    # Cancel it
    del_response = client.delete(f"/api/subscriptions/{sub_id}")
    assert del_response.status_code == 200
    assert del_response.json()["detail"] == "Subscription canceled successfully"

    # Verify status changed to canceled
    get_response = client.get(f"/api/subscriptions/{sub_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "canceled"

def test_cancel_subscription_not_found():
    response = client.delete("/api/subscriptions/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Subscription not found"
