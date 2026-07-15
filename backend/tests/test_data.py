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

def test_get_dynamic_data_search():
    # Searching for "can" which should match Canada
    response = client.get("/api/data/countries?search=can")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Canada"

def test_get_dynamic_data_search_and_pagination():
    # Search for "a" - will match Canada and United States, but we use pagination to get only the first one
    response = client.get("/api/data/countries?search=a&page=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    # Both Canada and United States have "a".
    assert data[0]["name"] in ["Canada", "United States"]

def test_get_dynamic_data_sort_asc():
    response = client.get("/api/data/countries?sort_by=name&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    assert data[0]["name"] == "Canada"
    assert data[1]["name"] == "United Kingdom"
    assert data[2]["name"] == "United States"

def test_get_dynamic_data_sort_desc():
    response = client.get("/api/data/countries?sort_by=name&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    assert data[0]["name"] == "United States"
    assert data[1]["name"] == "United Kingdom"
    assert data[2]["name"] == "Canada"

def test_get_dynamic_data_sort_invalid_field():
    # Sorting by a non-existent field shouldn't break, it should just push these items to the end or keep their original relative order.
    response = client.get("/api/data/countries?sort_by=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_get_dynamic_data_filter_field():
    response = client.get("/api/data/countries?filter_field=name&filter_value=canada")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Canada"

def test_get_dynamic_data_filter_pagination():
    response = client.get("/api/data/countries?filter_field=name&filter_value=Canada&page=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Canada"

def test_get_dynamic_data_filter_no_match():
    response = client.get("/api/data/countries?filter_field=name&filter_value=not_a_country")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
