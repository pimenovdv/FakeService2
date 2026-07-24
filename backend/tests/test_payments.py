from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_process_payment_success():
    payload = {
        "amount": 100.50,
        "currency": "USD",
        "payment_method": "credit_card",
        "description": "Test payment"
    }
    response = client.post("/api/payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "payment_id" in data
    assert data["status"] == "success"
    assert data["amount"] == 100.50
    assert data["currency"] == "USD"
    assert "timestamp" in data

def test_process_payment_invalid_amount():
    payload = {
        "amount": -10.0,
        "currency": "USD",
        "payment_method": "credit_card"
    }
    response = client.post("/api/payments", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Amount must be greater than 0"

def test_get_payment_status_success():
    # First, create a payment
    payload = {
        "amount": 50.0,
        "currency": "EUR",
        "payment_method": "paypal"
    }
    post_response = client.post("/api/payments", json=payload)
    payment_id = post_response.json()["payment_id"]

    # Then, retrieve its status
    get_response = client.get(f"/api/payments/{payment_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["payment_id"] == payment_id
    assert data["status"] == "success"
    assert data["amount"] == 50.0
    assert data["currency"] == "EUR"

def test_get_payment_status_not_found():
    response = client.get("/api/payments/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"
