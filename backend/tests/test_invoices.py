from fastapi.testclient import TestClient
from main import app
from routers.invoices import MOCK_INVOICES

client = TestClient(app)

def setup_function():
    # Clear the mock data before each test
    MOCK_INVOICES.clear()

def test_create_invoice():
    payload = {
        "items": [
            {"description": "Web Development", "amount": 1000.00},
            {"description": "Hosting", "amount": 50.00}
        ],
        "customer_id": "cust-123"
    }
    response = client.post("/api/invoices", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["customer_id"] == "cust-123"
    assert data["total_amount"] == 1050.00
    assert data["status"] == "unpaid"
    assert "created_at" in data
    assert data["paid_at"] is None

    assert len(data["items"]) == 2
    assert data["items"][0]["description"] == "Web Development"
    assert data["items"][0]["amount"] == 1000.00

def test_create_invoice_validation_error():
    # Missing items
    payload = {
        "customer_id": "cust-123"
    }
    response = client.post("/api/invoices", json=payload)
    assert response.status_code == 422

    # Empty items list
    payload = {
        "items": [],
        "customer_id": "cust-123"
    }
    response = client.post("/api/invoices", json=payload)
    assert response.status_code == 422

def test_list_invoices():
    # Create a couple of invoices
    client.post("/api/invoices", json={
        "items": [{"description": "Item 1", "amount": 10.0}],
        "customer_id": "cust-1"
    })
    client.post("/api/invoices", json={
        "items": [{"description": "Item 2", "amount": 20.0}],
        "customer_id": "cust-2"
    })

    response = client.get("/api/invoices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Ensure descending order by created_at (most recent first)
    assert data[0]["customer_id"] == "cust-2"
    assert data[1]["customer_id"] == "cust-1"

def test_get_invoice():
    # Create an invoice
    create_resp = client.post("/api/invoices", json={
        "items": [{"description": "Item", "amount": 100.0}],
        "customer_id": "cust-1"
    })
    invoice_id = create_resp.json()["id"]

    # Get it
    response = client.get(f"/api/invoices/{invoice_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == invoice_id
    assert data["customer_id"] == "cust-1"

def test_get_invoice_not_found():
    response = client.get("/api/invoices/nonexistent-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}

def test_pay_invoice():
    # Create an invoice
    create_resp = client.post("/api/invoices", json={
        "items": [{"description": "Item", "amount": 100.0}],
        "customer_id": "cust-1"
    })
    invoice_id = create_resp.json()["id"]

    # Pay it
    response = client.patch(f"/api/invoices/{invoice_id}/pay")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == invoice_id
    assert data["status"] == "paid"
    assert data["paid_at"] is not None

    # Try paying it again
    response_again = client.patch(f"/api/invoices/{invoice_id}/pay")
    assert response_again.status_code == 400
    assert response_again.json() == {"detail": "Invoice already paid"}

def test_pay_invoice_not_found():
    response = client.patch("/api/invoices/nonexistent-id/pay")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}
