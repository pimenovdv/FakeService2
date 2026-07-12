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

def test_next_step_success():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_1",
        "answers": {"name_input": "John Doe", "country_input": "usa"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == False
    assert data["next_screen"]["id"] == "screen_2"
    assert data["next_screen"]["header"] == "Confirm Details"

def test_next_step_completed():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_2",
        "answers": {"confirmation_checkbox": True}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == True
    assert "next_screen" in data
    assert data["next_screen"] is None

def test_next_step_not_found():
    response = client.post("/api/screens/next_step", json={
        "service_id": "nonexistent_service",
        "current_screen_id": "screen_1",
        "answers": {}
    })
    assert response.status_code == 404

def test_missing_routing_file():
    # Setup a service without routing file but with screen_1 file
    import json
    import os
    # Assuming tests run from backend/ directory
    with open("mock_data/service_missing_routing_screen_1.json", "w") as f:
        json.dump({
            "id": "screen_1",
            "components": [],
            "buttons": []
        }, f)

    response = client.post("/api/screens/next_step", json={
        "service_id": "service_missing_routing",
        "current_screen_id": "screen_1",
        "answers": {}
    })

    assert response.status_code == 404
    assert response.json() == {"detail": "Routing configuration for service_id 'service_missing_routing' not found."}

    # Cleanup
    os.remove("mock_data/service_missing_routing_screen_1.json")

def test_missing_next_step_in_routing():
    import json
    import os
    with open("mock_data/service_invalid_routing_screen_1.json", "w") as f:
        json.dump({
            "id": "screen_1",
            "components": [],
            "buttons": []
        }, f)
    with open("mock_data/service_invalid_routing_routing.json", "w") as f:
        json.dump({
            "other_screen": "completed"
        }, f)

    response = client.post("/api/screens/next_step", json={
        "service_id": "service_invalid_routing",
        "current_screen_id": "screen_1",
        "answers": {}
    })

    assert response.status_code == 404
    assert response.json() == {"detail": "No next step defined for service_id 'service_invalid_routing', screen 'screen_1'."}

    # Cleanup
    os.remove("mock_data/service_invalid_routing_screen_1.json")
    os.remove("mock_data/service_invalid_routing_routing.json")

def test_prev_step_success():
    response = client.post("/api/screens/prev_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_2"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "screen_1"

def test_prev_step_no_previous_defined():
    response = client.post("/api/screens/prev_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_1"
    })
    assert response.status_code == 404
    assert response.json() == {"detail": "No previous step defined for service_id 'service_1', screen 'screen_1'."}

def test_prev_step_routing_not_found():
    response = client.post("/api/screens/prev_step", json={
        "service_id": "nonexistent_service",
        "current_screen_id": "screen_2"
    })
    assert response.status_code == 404
