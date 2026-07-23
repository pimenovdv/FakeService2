from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_weather_london():
    response = client.get("/api/weather?city=london")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "London"
    assert data["temperature"] == 15.0
    assert data["condition"] == "Rainy"

def test_get_weather_tokyo():
    response = client.get("/api/weather?city=tokyo")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Tokyo"
    assert data["temperature"] == 22.5
    assert data["condition"] == "Sunny"

def test_get_weather_default():
    response = client.get("/api/weather?city=paris")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert data["temperature"] == 20.0
    assert data["condition"] == "Partly Cloudy"

def test_get_weather_missing_city():
    response = client.get("/api/weather")
    assert response.status_code == 422
