import pytest
from fastapi.testclient import TestClient
from main import app
from routers.addresses import addresses_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_addresses_db():
    addresses_db.clear()
    yield
    addresses_db.clear()

def test_get_addresses_empty():
    response = client.get("/api/addresses")
    assert response.status_code == 200
    assert response.json() == []

def test_create_address():
    address_data = {
        "user_id": "user1",
        "name": "Home",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA",
        "is_default": True
    }
    response = client.post("/api/addresses", json=address_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Home"
    assert data["user_id"] == "user1"
    assert data["is_default"] is True
    assert "created_at" in data

    # Verify it was added
    response = client.get("/api/addresses")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_create_address_default_logic():
    addr1 = {
        "user_id": "user1",
        "name": "Home",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA",
        "is_default": True
    }
    client.post("/api/addresses", json=addr1)

    addr2 = {
        "user_id": "user1",
        "name": "Work",
        "street": "456 Office Blvd",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA",
        "is_default": True
    }
    client.post("/api/addresses", json=addr2)

    response = client.get("/api/addresses")
    addresses = response.json()
    assert len(addresses) == 2

    # The second one should be default, first one should have been updated to not default
    home_addr = next(a for a in addresses if a["name"] == "Home")
    work_addr = next(a for a in addresses if a["name"] == "Work")

    assert home_addr["is_default"] is False
    assert work_addr["is_default"] is True

def test_update_address():
    # Create first
    address_data = {
        "user_id": "user1",
        "name": "Home",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA"
    }
    create_response = client.post("/api/addresses", json=address_data)
    address_id = create_response.json()["id"]

    # Update
    update_data = {
        "user_id": "user1",
        "name": "Home Updated",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA",
        "is_default": True
    }
    update_response = client.put(f"/api/addresses/{address_id}", json=update_data)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Home Updated"
    assert data["is_default"] is True

def test_update_address_not_found():
    update_data = {
        "user_id": "user1",
        "name": "Home",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA"
    }
    response = client.put("/api/addresses/nonexistent", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Address not found"}

def test_delete_address():
    # Create first
    address_data = {
        "user_id": "user1",
        "name": "Home",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "USA"
    }
    create_response = client.post("/api/addresses", json=address_data)
    address_id = create_response.json()["id"]

    # Delete
    delete_response = client.delete(f"/api/addresses/{address_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "Address deleted"}

    # Verify deleted
    response = client.get("/api/addresses")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_delete_address_not_found():
    response = client.delete("/api/addresses/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Address not found"}
