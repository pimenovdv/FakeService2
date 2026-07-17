from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_stream_endpoint():
    response = client.get("/api/stream")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Check that events are in the stream
    content = response.content.decode("utf-8")
    assert "data: {\"message\": \"Connected\"}" in content
    assert "data: {\"event\": \"update\", \"data\": 1}" in content
    assert "data: {\"event\": \"update\", \"data\": 2}" in content
    assert "data: {\"event\": \"done\"}" in content
