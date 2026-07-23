from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_search_endpoint_with_results():
    response = client.get("/api/search?q=Settings")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # We know "Settings" is in the mock data, let's verify
    found_settings = any(item["title"] == "Settings" for item in data)
    assert found_settings, "Settings should be found in the results"

def test_search_endpoint_case_insensitive():
    response = client.get("/api/search?q=settings")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    found_settings = any(item["title"] == "Settings" for item in data)
    assert found_settings, "Search should be case insensitive"

def test_search_endpoint_empty_query():
    response = client.get("/api/search")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_search_endpoint_no_results():
    response = client.get("/api/search?q=NonExistentQuery123")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
