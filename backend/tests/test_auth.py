import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] == "mock_token_12345"
    assert data["token_type"] == "bearer"

def test_login_failure():
    response = client.post(
        "/api/auth/login",
        json={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_me_success():
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer mock_token_12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "admin"
    assert data["email"] == "admin@example.com"

def test_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_me_invalid_token():
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
