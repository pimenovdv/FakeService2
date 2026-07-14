from fastapi.testclient import TestClient
from main import app
import json
import os
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_mock_data():
    mock_data_dir = "mock_data"
    os.makedirs(mock_data_dir, exist_ok=True)
    filepath = os.path.join(mock_data_dir, "pagination_test.json")
    data = [{"id": i, "name": f"Item {i}"} for i in range(1, 11)]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)
    yield
    os.remove(filepath)

def test_pagination_default():
    response = client.get("/api/data/pagination_test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

def test_pagination_limit():
    response = client.get("/api/data/pagination_test?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["id"] == 1
    assert data[2]["id"] == 3

def test_pagination_page_and_limit():
    response = client.get("/api/data/pagination_test?page=2&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["id"] == 4
    assert data[2]["id"] == 6

def test_pagination_out_of_bounds():
    response = client.get("/api/data/pagination_test?page=5&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_pagination_last_page():
    response = client.get("/api/data/pagination_test?page=4&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 10

def test_pagination_non_list_data():
    # Setup mock data that is not a list
    mock_data_dir = "mock_data"
    filepath = os.path.join(mock_data_dir, "dict_test.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"key": "value"}, f)

    response = client.get("/api/data/dict_test?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data == {"key": "value"}

    os.remove(filepath)
