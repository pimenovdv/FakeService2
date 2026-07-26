from fastapi.testclient import TestClient
from main import app
from routers.orders import MOCK_ORDERS

client = TestClient(app)

def setup_function():
    # Clear MOCK_ORDERS before each test
    MOCK_ORDERS.clear()

def test_create_order():
    payload = {
        "customer_id": "cust-123",
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 10.5},
            {"product_id": "prod-2", "quantity": 1, "price": 5.0}
        ]
    }
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["customer_id"] == "cust-123"
    assert data["total_amount"] == 26.0
    assert data["status"] == "pending"
    assert len(data["items"]) == 2
    assert "created_at" in data

    # Verify it was added to the mock store
    assert len(MOCK_ORDERS) == 1
    assert data["id"] in MOCK_ORDERS

def test_create_order_invalid():
    # Missing customer_id
    payload = {
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 10.5}
        ]
    }
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 422

    # Empty items list
    payload2 = {
        "customer_id": "cust-123",
        "items": []
    }
    response2 = client.post("/api/orders", json=payload2)
    assert response2.status_code == 422

def test_list_orders():
    # Create two orders
    payload1 = {
        "customer_id": "cust-1",
        "items": [{"product_id": "prod-1", "quantity": 1, "price": 10.0}]
    }
    client.post("/api/orders", json=payload1)

    payload2 = {
        "customer_id": "cust-2",
        "items": [{"product_id": "prod-2", "quantity": 2, "price": 20.0}]
    }
    client.post("/api/orders", json=payload2)

    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Should be sorted by created_at descending (latest first)
    # The second one we created will be first in the list
    assert data[0]["customer_id"] == "cust-2"
    assert data[1]["customer_id"] == "cust-1"

def test_get_order():
    # Create an order
    payload = {
        "customer_id": "cust-999",
        "items": [{"product_id": "prod-9", "quantity": 3, "price": 30.0}]
    }
    create_response = client.post("/api/orders", json=payload)
    order_id = create_response.json()["id"]

    # Get the order
    response = client.get(f"/api/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == "cust-999"
    assert data["total_amount"] == 90.0
    assert data["status"] == "pending"

def test_get_order_not_found():
    response = client.get("/api/orders/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
