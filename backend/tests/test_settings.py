from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "light"
    assert data["notifications_enabled"] is True
    assert data["language"] == "en"
    assert data["timezone"] == "UTC"

def test_update_settings():
    # Update theme and timezone
    update_data = {
        "theme": "dark",
        "timezone": "PST"
    }
    response = client.put("/api/settings", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"
    assert data["notifications_enabled"] is True # Unchanged
    assert data["language"] == "en" # Unchanged
    assert data["timezone"] == "PST"

    # Verify that a subsequent GET returns the updated settings
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"
    assert data["timezone"] == "PST"
