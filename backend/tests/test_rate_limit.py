from fastapi.testclient import TestClient
import pytest
from main import app, rate_limiter

client = TestClient(app)

def test_rate_limiting_middleware_below_limit():
    # Clear the state before testing
    rate_limiter.clients.clear()

    # Send 2 requests with a limit of 3
    for _ in range(2):
        response = client.get("/api/health", headers={"x-mock-rate-limit": "3"})
        assert response.status_code == 200

def test_rate_limiting_middleware_exceeds_limit():
    # Clear the state before testing
    rate_limiter.clients.clear()

    # Send 3 requests with a limit of 3
    for _ in range(3):
        response = client.get("/api/health", headers={"x-mock-rate-limit": "3"})
        assert response.status_code == 200

    # The 4th request should be rate limited
    response = client.get("/api/health", headers={"x-mock-rate-limit": "3"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}

def test_rate_limiting_middleware_no_header():
    # Clear the state before testing
    rate_limiter.clients.clear()

    # Should not rate limit if header is missing
    for _ in range(5):
        response = client.get("/api/health")
        assert response.status_code == 200

def test_rate_limiting_middleware_invalid_header():
    # Clear the state before testing
    rate_limiter.clients.clear()

    # Should not rate limit if header is invalid
    for _ in range(5):
        response = client.get("/api/health", headers={"x-mock-rate-limit": "abc"})
        assert response.status_code == 200
