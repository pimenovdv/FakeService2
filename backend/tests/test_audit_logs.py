import pytest
from fastapi.testclient import TestClient
from main import app
from routers.audit_logs import MOCK_LOGS

client = TestClient(app)

def test_get_audit_logs_default_pagination():
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == min(10, len(MOCK_LOGS))
    assert data["total"] == len(MOCK_LOGS)

def test_get_audit_logs_custom_pagination():
    response = client.get("/api/audit-logs?skip=5&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 5
    assert data["limit"] == 20
    assert len(data["items"]) == min(20, len(MOCK_LOGS) - 5)

def test_get_audit_logs_filter_by_user_id():
    # Find a user_id that exists in the mock data, if any
    if MOCK_LOGS:
        test_user_id = MOCK_LOGS[0]["user_id"]
        response = client.get(f"/api/audit-logs?user_id={test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert all(log["user_id"] == test_user_id for log in data["items"])
        assert data["total"] == sum(1 for log in MOCK_LOGS if log["user_id"] == test_user_id)

def test_get_audit_logs_filter_by_action():
    # Find an action that exists in the mock data, if any
    if MOCK_LOGS:
        test_action = MOCK_LOGS[0]["action"]
        response = client.get(f"/api/audit-logs?action={test_action}")
        assert response.status_code == 200
        data = response.json()
        assert all(log["action"] == test_action for log in data["items"])
        assert data["total"] == sum(1 for log in MOCK_LOGS if log["action"] == test_action)

def test_get_audit_logs_combined_filters():
    if MOCK_LOGS:
        test_user_id = MOCK_LOGS[0]["user_id"]
        test_action = MOCK_LOGS[0]["action"]
        response = client.get(f"/api/audit-logs?user_id={test_user_id}&action={test_action}")
        assert response.status_code == 200
        data = response.json()
        assert all(log["user_id"] == test_user_id and log["action"] == test_action for log in data["items"])
        assert data["total"] == sum(1 for log in MOCK_LOGS if log["user_id"] == test_user_id and log["action"] == test_action)
