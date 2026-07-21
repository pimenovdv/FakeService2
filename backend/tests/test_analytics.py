from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_analytics_default():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "metric" in data
    assert data["metric"] == "visitors"
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 7
    for point in data["data"]:
        assert "timestamp" in point
        assert "value" in point

def test_get_analytics_with_params():
    response = client.get("/api/analytics?start_date=2023-01-01&end_date=2023-01-10&metric=revenue")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "revenue"
    assert len(data["data"]) == 10
    assert data["data"][0]["timestamp"] == "2023-01-01"
    assert data["data"][9]["timestamp"] == "2023-01-10"

def test_get_analytics_invalid_dates():
    # Should fallback gracefully
    response = client.get("/api/analytics?start_date=invalid&end_date=invalid")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 7 # Fallback to 7 days

def test_get_analytics_large_date_range():
    # Should limit to 30 days or fallback based on logic
    response = client.get("/api/analytics?start_date=2023-01-01&end_date=2023-03-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 7 # Delta > 30, so falls back to 7
