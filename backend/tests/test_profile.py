from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_profile():
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "mockuser"
    assert data["email"] == "mockuser@example.com"
    assert data["first_name"] == "Mock"
    assert data["last_name"] == "User"
    assert data["bio"] == "I am a mock user."

def test_update_profile():
    # Update parts of the profile
    update_data = {
        "first_name": "Updated",
        "bio": "I am an updated mock user."
    }
    response = client.put("/api/profile", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "mockuser"  # unchanged
    assert data["email"] == "mockuser@example.com"  # unchanged
    assert data["first_name"] == "Updated"  # changed
    assert data["last_name"] == "User"  # unchanged
    assert data["bio"] == "I am an updated mock user."  # changed

    # Verify that the changes were saved
    response2 = client.get("/api/profile")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["first_name"] == "Updated"
    assert data2["bio"] == "I am an updated mock user."

    # Update other parts to reset state
    update_data2 = {
        "first_name": "Mock",
        "bio": "I am a mock user."
    }
    client.put("/api/profile", json=update_data2)
