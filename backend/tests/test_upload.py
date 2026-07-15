import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_file():
    # Create a mock file content
    file_content = b"This is a test file content."
    files = {"file": ("test_file.txt", file_content, "text/plain")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["filename"] == "test_file.txt"
    assert data["content_type"] == "text/plain"
    assert "file_id" in data
    assert "url" in data
    assert data["url"].startswith(f"/mock-uploads/{data['file_id']}/test_file.txt")
