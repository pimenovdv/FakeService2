from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_events():
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The in-memory storage starts with 2 events
    assert len(data) >= 2

    first_event = data[0]
    assert "id" in first_event
    assert "title" in first_event
    assert "start_time" in first_event
    assert "end_time" in first_event

def test_create_event():
    new_event_data = {
        "title": "New Meeting",
        "description": "Discuss quarterly goals.",
        "start_time": "2024-03-15T10:00:00",
        "end_time": "2024-03-15T11:00:00",
        "location": "Online"
    }

    response = client.post("/api/events", json=new_event_data)
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["title"] == new_event_data["title"]
    assert data["description"] == new_event_data["description"]
    assert data["start_time"] == new_event_data["start_time"]
    assert data["end_time"] == new_event_data["end_time"]
    assert data["location"] == new_event_data["location"]

    # Verify the event is now in the list
    get_response = client.get("/api/events")
    events = get_response.json()
    assert any(event["id"] == data["id"] for event in events)
