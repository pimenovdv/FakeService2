import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_download_txt_format():
    response = client.get("/api/download/file123")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "File ID: file123" in response.text
    assert "mock text file" in response.text

def test_download_csv_format():
    response = client.get("/api/download/file456?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "id,message" in response.text
    assert "file456,This is a mock CSV file." in response.text

def test_download_json_format():
    response = client.get("/api/download/file789?format=json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["id"] == "file789"
    assert "mock JSON file" in data["message"]

def test_download_unknown_format():
    response = client.get("/api/download/fileabc?format=unknown")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "File ID: fileabc" in response.text
