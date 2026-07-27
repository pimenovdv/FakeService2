import pytest
from fastapi.testclient import TestClient
from main import app
from routers.cart import cart_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_cart_db():
    cart_db.clear()
    yield

def test_get_cart_empty():
    response = client.get("/api/cart")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_items"] == 0
    assert data["total_price"] == 0.0

def test_add_item_to_cart():
    item_data = {
        "product_id": "prod_1",
        "quantity": 2,
        "name": "Test Product",
        "price": 10.5
    }
    response = client.post("/api/cart/items", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["product_id"] == "prod_1"
    assert data["quantity"] == 2
    assert data["name"] == "Test Product"
    assert data["price"] == 10.5

    # Check cart summary
    summary_resp = client.get("/api/cart")
    summary = summary_resp.json()
    assert summary["total_items"] == 2
    assert summary["total_price"] == 21.0
    assert len(summary["items"]) == 1

def test_add_item_to_cart_increase_quantity():
    # Add first time
    item_data = {
        "product_id": "prod_1",
        "quantity": 1,
        "name": "Test Product",
        "price": 10.0
    }
    client.post("/api/cart/items", json=item_data)

    # Add second time (same product_id)
    item_data_2 = {
        "product_id": "prod_1",
        "quantity": 2,
        "name": "Test Product Updated", # Optional update
        "price": 15.0 # Optional update
    }
    response = client.post("/api/cart/items", json=item_data_2)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 3
    assert data["name"] == "Test Product Updated"
    assert data["price"] == 15.0

    # Check cart summary
    summary_resp = client.get("/api/cart")
    summary = summary_resp.json()
    assert summary["total_items"] == 3
    assert summary["total_price"] == 45.0
    assert len(summary["items"]) == 1

def test_remove_item_from_cart():
    # Add item
    item_data = {
        "product_id": "prod_1",
        "quantity": 1,
        "name": "Test Product",
        "price": 10.0
    }
    add_response = client.post("/api/cart/items", json=item_data)
    item_id = add_response.json()["id"]

    # Remove item
    remove_response = client.delete(f"/api/cart/items/{item_id}")
    assert remove_response.status_code == 200

    # Check cart is empty
    summary_resp = client.get("/api/cart")
    summary = summary_resp.json()
    assert summary["total_items"] == 0
    assert len(summary["items"]) == 0

def test_remove_item_not_found():
    response = client.delete("/api/cart/items/non_existent_id")
    assert response.status_code == 404

def test_clear_cart():
    # Add some items
    client.post("/api/cart/items", json={"product_id": "prod_1", "quantity": 1, "price": 10.0})
    client.post("/api/cart/items", json={"product_id": "prod_2", "quantity": 2, "price": 5.0})

    # Clear cart
    clear_response = client.delete("/api/cart")
    assert clear_response.status_code == 200

    # Check cart is empty
    summary_resp = client.get("/api/cart")
    summary = summary_resp.json()
    assert summary["total_items"] == 0
    assert len(summary["items"]) == 0
