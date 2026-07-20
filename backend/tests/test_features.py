import pytest
from fastapi.testclient import TestClient
from main import app
from routers.features import feature_flags

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_feature_flags():
    """Clear feature flags before each test."""
    feature_flags.clear()
    yield

def test_get_features_empty():
    response = client.get("/api/features")
    assert response.status_code == 200
    assert response.json() == {}

def test_put_feature():
    response = client.put("/api/features/new-ui", json={"enabled": True})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["flag"] == "new-ui"
    assert data["enabled"] is True

    # Verify it's in the list
    response = client.get("/api/features")
    assert response.status_code == 200
    assert response.json() == {"new-ui": True}

def test_put_feature_update():
    # Set to true
    client.put("/api/features/beta-feature", json={"enabled": True})

    # Update to false
    response = client.put("/api/features/beta-feature", json={"enabled": False})
    assert response.status_code == 200

    # Verify
    response = client.get("/api/features")
    assert response.status_code == 200
    assert response.json() == {"beta-feature": False}

def test_delete_feature_success():
    client.put("/api/features/test-flag", json={"enabled": True})

    response = client.delete("/api/features/test-flag")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Flag 'test-flag' deleted."}

    # Verify it's gone
    response = client.get("/api/features")
    assert response.status_code == 200
    assert response.json() == {}

def test_delete_feature_not_found():
    response = client.delete("/api/features/non-existent-flag")
    assert response.status_code == 404
    assert response.json() == {"detail": "Flag not found"}
