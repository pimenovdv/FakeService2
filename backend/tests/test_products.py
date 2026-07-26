from fastapi.testclient import TestClient
from main import app
from routers.products import MOCK_PRODUCTS

client = TestClient(app)

def setup_function():
    # Clear the mock data before each test
    MOCK_PRODUCTS.clear()

def test_create_product():
    payload = {
        "name": "Smartphone",
        "description": "Latest model",
        "price": 999.99,
        "stock": 50
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["name"] == "Smartphone"
    assert data["description"] == "Latest model"
    assert data["price"] == 999.99
    assert data["stock"] == 50

def test_list_products():
    client.post("/api/products", json={"name": "Product 1", "price": 10.0, "stock": 5})
    client.post("/api/products", json={"name": "Product 2", "price": 20.0, "stock": 10})

    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_product():
    create_resp = client.post("/api/products", json={"name": "Product A", "price": 15.0, "stock": 2})
    product_id = create_resp.json()["id"]

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Product A"

def test_get_product_not_found():
    response = client.get("/api/products/nonexistent-id")
    assert response.status_code == 404

def test_update_product():
    create_resp = client.post("/api/products", json={"name": "Old Name", "price": 10.0, "stock": 5})
    product_id = create_resp.json()["id"]

    update_payload = {
        "name": "New Name",
        "price": 15.0
    }
    response = client.put(f"/api/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == 15.0
    assert data["stock"] == 5 # Unchanged

    # Verify in DB
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.json()["name"] == "New Name"

def test_update_product_not_found():
    response = client.put("/api/products/nonexistent-id", json={"name": "Test"})
    assert response.status_code == 404

def test_delete_product():
    create_resp = client.post("/api/products", json={"name": "To Delete", "price": 5.0, "stock": 1})
    product_id = create_resp.json()["id"]

    del_response = client.delete(f"/api/products/{product_id}")
    assert del_response.status_code == 200

    # Verify deleted
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 404

def test_delete_product_not_found():
    response = client.delete("/api/products/nonexistent-id")
    assert response.status_code == 404
