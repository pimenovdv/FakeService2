from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "services" in data
    assert data["services"]["database"] == "connected"
    assert data["services"]["cache"] == "connected"
    assert data["services"]["message_queue"] == "connected"
