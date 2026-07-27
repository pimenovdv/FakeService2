from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_calculate_shipping():
    payload = {
        "destination_country": "US",
        "destination_zip": "10001",
        "items": [
            {"product_id": "prod_1", "weight_kg": 1.5, "dimensions_cm": [10, 10, 10]},
            {"product_id": "prod_2", "weight_kg": 0.5}
        ]
    }

    response = client.post("/api/shipping/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "options" in data
    assert len(data["options"]) > 0

    # Check that standard and express are returned
    service_names = [opt["service_name"] for opt in data["options"]]
    assert "Standard Shipping" in service_names
    assert "Express Shipping" in service_names

    # Check basic cost calculation logic (total weight = 2.0)
    # Standard: max(5.0, 2.0 * 2.5) = 5.0
    # Express: max(15.0, 2.0 * 5.0) = 15.0 (actually 10.0, but max is 15.0)
    standard_opt = next(opt for opt in data["options"] if opt["service_id"] == "standard_1")
    assert standard_opt["cost"] == 5.0
    express_opt = next(opt for opt in data["options"] if opt["service_id"] == "express_1")
    assert express_opt["cost"] == 15.0

def test_track_shipment_success():
    tracking_number = "1Z9999999999999999"
    response = client.get(f"/api/shipping/track/{tracking_number}")
    assert response.status_code == 200
    data = response.json()
    assert data["tracking_number"] == tracking_number
    assert "status" in data
    assert "events" in data
    assert len(data["events"]) > 0

def test_track_shipment_not_found():
    tracking_number = "ERR12345"
    response = client.get(f"/api/shipping/track/{tracking_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tracking number not found"
