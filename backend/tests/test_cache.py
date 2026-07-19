import pytest
from fastapi.testclient import TestClient
from main import app
from routers.cache import cache_store
import time

client = TestClient(app)

def test_cache_lifecycle():
    # Clear store before test
    cache_store.clear()

    key = "test_key_1"

    # Get non-existent
    response = client.get(f"/api/cache/{key}")
    assert response.status_code == 404

    # Set value
    value = {"name": "Alice", "age": 30}
    response = client.post(f"/api/cache/{key}", json=value)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Get value
    response = client.get(f"/api/cache/{key}")
    assert response.status_code == 200
    assert response.json()["value"] == value

    # Delete value
    response = client.delete(f"/api/cache/{key}")
    assert response.status_code == 200

    # Get deleted
    response = client.get(f"/api/cache/{key}")
    assert response.status_code == 404

    # Delete non-existent
    response = client.delete(f"/api/cache/{key}")
    assert response.status_code == 404

def test_cache_ttl():
    # Clear store before test
    cache_store.clear()

    key = "test_key_ttl"
    value = "temporary"

    # Set value with TTL = 1 second
    response = client.post(f"/api/cache/{key}?ttl=1", content=value)
    assert response.status_code == 200

    # Get immediately should succeed
    response = client.get(f"/api/cache/{key}")
    assert response.status_code == 200
    assert response.json()["value"] == value

    # Wait for TTL to expire
    time.sleep(1.1)

    # Get should now fail
    response = client.get(f"/api/cache/{key}")
    assert response.status_code == 404
