from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_translate_endpoint():
    request_data = {
        "text": "Hello world",
        "target_language": "es"
    }

    response = client.post("/api/translate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["translated_text"] == "[ES] Hello world"
    assert data["source_language"] == "auto"
    assert data["target_language"] == "es"

def test_translate_endpoint_with_source_language():
    request_data = {
        "text": "Hello world",
        "target_language": "fr",
        "source_language": "en"
    }

    response = client.post("/api/translate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["translated_text"] == "[FR] Hello world"
    assert data["source_language"] == "en"
    assert data["target_language"] == "fr"

def test_translate_endpoint_missing_fields():
    request_data = {
        "text": "Hello world"
    }

    response = client.post("/api/translate", json=request_data)
    assert response.status_code == 422  # Unprocessable Entity
