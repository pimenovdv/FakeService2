from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_dynamic_data_success():
    response = client.get("/api/data/countries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]

def test_get_dynamic_data_not_found():
    response = client.get("/api/data/invalid_source_123")
    assert response.status_code == 404
    assert response.json() == {"detail": "Data source 'invalid_source_123' not found."}
