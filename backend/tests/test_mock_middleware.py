import time
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_mock_middleware_no_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_mock_middleware_delay():
    start_time = time.time()
    response = client.get("/", headers={"X-Mock-Delay-Ms": "100"})
    end_time = time.time()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    # The elapsed time should be at least 0.1 seconds (100ms)
    assert (end_time - start_time) >= 0.1

def test_mock_middleware_error_500():
    response = client.get("/", headers={"X-Mock-Error-Code": "500"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Mock error: 500"}

def test_mock_middleware_error_503():
    response = client.get("/", headers={"X-Mock-Error-Code": "503"})
    assert response.status_code == 503
    assert response.json() == {"detail": "Mock error: 503"}

def test_mock_middleware_invalid_delay_header():
    start_time = time.time()
    # "abc" cannot be parsed as int, middleware should ignore it
    response = client.get("/", headers={"X-Mock-Delay-Ms": "abc"})
    end_time = time.time()

    assert response.status_code == 200
    # Should not delay, so it should be very fast (definitely less than 0.1s for a simple endpoint)
    assert (end_time - start_time) < 0.1

def test_mock_middleware_invalid_error_header():
    # "abc" cannot be parsed as int, middleware should ignore it
    response = client.get("/", headers={"X-Mock-Error-Code": "abc"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
