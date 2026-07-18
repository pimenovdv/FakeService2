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
    assert data["access_token"] == "mock_token_admin"
    assert data["token_type"] == "bearer"

def test_login_user_success():
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "mock_token_user"

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
    assert "admin" in data["roles"]

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

def test_authorize_redirect():
    response = client.get(
        "/api/auth/authorize?response_type=code&client_id=123&redirect_uri=http://localhost/callback&state=mystate",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert "http://localhost/callback?code=mock_auth_code_98765&state=mystate" in response.headers["location"]

def test_authorize_invalid_response_type():
    response = client.get(
        "/api/auth/authorize?response_type=token&client_id=123&redirect_uri=http://localhost/callback"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported response_type"

def test_token_auth_code_success():
    response = client.post(
        "/api/auth/token",
        data={"grant_type": "authorization_code", "code": "mock_auth_code_98765"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "mock_token_admin"

def test_token_auth_code_invalid():
    response = client.post(
        "/api/auth/token",
        data={"grant_type": "authorization_code", "code": "invalid_code"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid code"

def test_token_password_success():
    response = client.post(
        "/api/auth/token",
        data={"grant_type": "password", "username": "user", "password": "user"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "mock_token_user"

def test_token_invalid_grant_type():
    response = client.post(
        "/api/auth/token",
        data={"grant_type": "client_credentials"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported grant_type"

def test_admin_data_access_success():
    response = client.get(
        "/api/auth/admin-data",
        headers={"Authorization": "Bearer mock_token_admin"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is sensitive admin data"

def test_admin_data_access_forbidden():
    response = client.get(
        "/api/auth/admin-data",
        headers={"Authorization": "Bearer mock_token_user"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
