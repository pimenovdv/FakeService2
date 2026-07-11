from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_next_step_validation_error():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_1",
        "answers": {}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Name is required"}
