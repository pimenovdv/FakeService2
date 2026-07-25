import pytest
from fastapi.testclient import TestClient
from main import app
from routers.devices import MOCK_DEVICES

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_mock_devices():
    """Clear the mock devices dictionary before each test."""
    MOCK_DEVICES.clear()
    yield

def test_register_device():
    response = client.post("/api/devices", json={
        "name": "My iPhone",
        "type": "mobile",
        "os_version": "iOS 16"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "My iPhone"
    assert data["type"] == "mobile"
    assert data["os_version"] == "iOS 16"
    assert "created_at" in data

    assert data["id"] in MOCK_DEVICES

def test_register_device_missing_fields():
    response = client.post("/api/devices", json={
        "name": "My iPhone",
    })
    assert response.status_code == 422 # type is required

def test_list_devices():
    # Register 2 devices
    client.post("/api/devices", json={"name": "Device 1", "type": "desktop"})
    client.post("/api/devices", json={"name": "Device 2", "type": "mobile", "os_version": "Android 13"})

    response = client.get("/api/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Check that they are sorted by created_at descending
    assert data[0]["name"] == "Device 2"
    assert data[1]["name"] == "Device 1"

def test_remove_device():
    # Register a device
    res = client.post("/api/devices", json={"name": "To be removed", "type": "tablet"})
    assert res.status_code == 200
    device_id = res.json()["id"]

    # Remove the device
    response = client.delete(f"/api/devices/{device_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted", "id": device_id}

    # List devices should be empty
    list_response = client.get("/api/devices")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 0

def test_remove_nonexistent_device():
    response = client.delete("/api/devices/invalid-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Device not found"}
