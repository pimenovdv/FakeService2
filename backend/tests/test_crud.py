import pytest
from fastapi.testclient import TestClient
from main import app
from routers.crud import resources_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Clear the in-memory database before each test."""
    resources_db.clear()
    yield

def test_create_resource():
    payload = {"name": "Test Item", "value": 42}
    response = client.post("/api/resource/test_items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["value"] == 42
    assert "id" in data

def test_create_resource_with_id():
    payload = {"id": "custom-id-123", "name": "Test Item"}
    response = client.post("/api/resource/test_items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "custom-id-123"

def test_get_resources_empty():
    response = client.get("/api/resource/test_items")
    assert response.status_code == 200
    assert response.json() == []

def test_get_resources():
    client.post("/api/resource/test_items", json={"name": "Item 1"})
    client.post("/api/resource/test_items", json={"name": "Item 2"})

    response = client.get("/api/resource/test_items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [item["name"] for item in data]
    assert "Item 1" in names
    assert "Item 2" in names

def test_get_resource_by_id():
    post_res = client.post("/api/resource/test_items", json={"name": "Item to fetch"})
    item_id = post_res.json()["id"]

    get_res = client.get(f"/api/resource/test_items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Item to fetch"

def test_get_resource_not_found():
    response = client.get("/api/resource/test_items/non-existent")
    assert response.status_code == 404

def test_update_resource():
    post_res = client.post("/api/resource/test_items", json={"name": "Initial", "old_val": 1})
    item_id = post_res.json()["id"]

    put_res = client.put(f"/api/resource/test_items/{item_id}", json={"name": "Updated", "new_val": 2})
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["name"] == "Updated"
    assert data["new_val"] == 2
    assert data["id"] == item_id

    get_res = client.get(f"/api/resource/test_items/{item_id}")
    assert get_res.json()["name"] == "Updated"

def test_update_resource_not_found():
    response = client.put("/api/resource/test_items/non-existent", json={"name": "Updated"})
    assert response.status_code == 404

def test_delete_resource():
    post_res = client.post("/api/resource/test_items", json={"name": "To delete"})
    item_id = post_res.json()["id"]

    del_res = client.delete(f"/api/resource/test_items/{item_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/resource/test_items/{item_id}")
    assert get_res.status_code == 404

def test_delete_resource_not_found():
    response = client.delete("/api/resource/test_items/non-existent")
    assert response.status_code == 404
