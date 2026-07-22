from fastapi.testclient import TestClient
from main import app
from routers.comments import mock_comments_store

client = TestClient(app)

def test_post_comment():
    entity_id = "test-entity-123"
    response = client.post(
        f"/api/comments/{entity_id}",
        json={"user_id": "user-456", "text": "This is a test comment"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["entity_id"] == entity_id
    assert data["user_id"] == "user-456"
    assert data["text"] == "This is a test comment"
    assert "created_at" in data

def test_get_comments():
    entity_id = "test-entity-456"
    # Create a couple of comments
    client.post(f"/api/comments/{entity_id}", json={"user_id": "user-1", "text": "Comment 1"})
    client.post(f"/api/comments/{entity_id}", json={"user_id": "user-2", "text": "Comment 2"})

    response = client.get(f"/api/comments/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert data[0]["text"] == "Comment 1"
    assert data[1]["text"] == "Comment 2"

def test_delete_comment():
    entity_id = "test-entity-789"
    # Create a comment
    post_resp = client.post(f"/api/comments/{entity_id}", json={"user_id": "user-x", "text": "To be deleted"})
    assert post_resp.status_code == 200
    comment_id = post_resp.json()["id"]

    # Delete the comment
    del_resp = client.delete(f"/api/comments/{comment_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"status": "success", "id": comment_id}

    # Verify it is deleted
    get_resp = client.get(f"/api/comments/{entity_id}")
    assert get_resp.status_code == 200
    comments = get_resp.json()
    assert all(c["id"] != comment_id for c in comments)

def test_delete_nonexistent_comment():
    response = client.delete("/api/comments/nonexistent-id")
    assert response.status_code == 404
