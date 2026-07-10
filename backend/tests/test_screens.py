from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_start_scenario_success():
    response = client.post("/api/screens/start", json={"service_id": "service_1"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "screen_1"
    assert "header" in data
    assert "components" in data
    assert "buttons" in data

def test_start_scenario_not_found():
    response = client.post("/api/screens/start", json={"service_id": "nonexistent_service"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Initial screen for service_id 'nonexistent_service' not found."}
