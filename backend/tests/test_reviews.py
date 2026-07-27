import pytest
from fastapi.testclient import TestClient
from main import app
from routers.reviews import reviews_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_reviews_db():
    reviews_db.clear()
    yield

def test_add_review():
    response = client.post(
        "/api/reviews/product-123",
        json={"user_id": "user-1", "rating": 5, "comment": "Great product!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["product_id"] == "product-123"
    assert data["user_id"] == "user-1"
    assert data["rating"] == 5
    assert data["comment"] == "Great product!"

def test_add_review_invalid_rating():
    response = client.post(
        "/api/reviews/product-123",
        json={"user_id": "user-1", "rating": 6, "comment": "Invalid rating"}
    )
    assert response.status_code == 400
    assert "Rating must be between 1 and 5" in response.json()["detail"]

def test_get_product_reviews():
    # Add a few reviews
    client.post("/api/reviews/product-123", json={"user_id": "user-1", "rating": 5})
    client.post("/api/reviews/product-123", json={"user_id": "user-2", "rating": 4})
    client.post("/api/reviews/product-456", json={"user_id": "user-3", "rating": 3})

    response = client.get("/api/reviews/product-123")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for review in data:
        assert review["product_id"] == "product-123"

def test_delete_review():
    # Add a review
    post_response = client.post(
        "/api/reviews/product-123",
        json={"user_id": "user-1", "rating": 5, "comment": "Great product!"}
    )
    review_id = post_response.json()["id"]

    # Delete the review
    delete_response = client.delete(f"/api/reviews/{review_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Review deleted"

    # Verify deletion
    assert review_id not in reviews_db

def test_delete_review_not_found():
    response = client.delete("/api/reviews/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"
