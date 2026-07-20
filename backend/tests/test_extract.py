from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_extract_id_card_by_type():
    file_content = b"fake image content"
    files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}
    data = {"document_type": "id_card"}
    response = client.post("/api/extract", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["document_type"] == "id_card"
    assert "first_name" in res_data["extracted_data"]

def test_extract_invoice_by_filename():
    file_content = b"fake pdf content"
    files = {"file": ("invoice_123.pdf", io.BytesIO(file_content), "application/pdf")}
    response = client.post("/api/extract", files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["document_type"] == "invoice"
    assert "total_amount" in res_data["extracted_data"]

def test_extract_generic():
    file_content = b"fake txt content"
    files = {"file": ("document.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/api/extract", files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["document_type"] == "generic"
    assert "text" in res_data["extracted_data"]
