import pytest
from fastapi.testclient import TestClient
from main import app
from routers.favorites import favorites_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_favorites_db():
    favorites_db.clear()
    yield

def test_add_favorite():
    response = client.post("/api/favorites/prod-1")
    assert response.status_code == 200
    assert response.json()["detail"] == "Product added to favorites"
    assert "prod-1" in favorites_db

def test_add_favorite_already_exists():
    favorites_db.add("prod-1")
    response = client.post("/api/favorites/prod-1")
    assert response.status_code == 200
    assert response.json()["detail"] == "Product is already in favorites"

def test_get_favorites():
    favorites_db.add("prod-1")
    favorites_db.add("prod-2")
    response = client.get("/api/favorites")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "prod-1" in data
    assert "prod-2" in data

def test_remove_favorite():
    favorites_db.add("prod-1")
    response = client.delete("/api/favorites/prod-1")
    assert response.status_code == 200
    assert response.json()["detail"] == "Product removed from favorites"
    assert "prod-1" not in favorites_db

def test_remove_favorite_not_found():
    response = client.delete("/api/favorites/non-existent-prod")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found in favorites"
