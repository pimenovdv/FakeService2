from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

# Mock database for reviews
# The structure will be a dictionary where the key is review_id and the value is a Review
reviews_db = {}

class ReviewCreate(BaseModel):
    user_id: str
    rating: int # 1 to 5
    comment: Optional[str] = None

class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: int
    comment: Optional[str] = None

@router.get("/{product_id}", response_model=List[Review])
async def get_product_reviews(product_id: str = Path(...)):
    """Retrieve all reviews for a specific product."""
    product_reviews = [review for review in reviews_db.values() if review.product_id == product_id]
    return product_reviews

@router.post("/{product_id}", response_model=Review)
async def add_review(review: ReviewCreate, product_id: str = Path(...)):
    """Add a new review for a product."""
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    review_id = str(uuid.uuid4())
    new_review = Review(id=review_id, product_id=product_id, **review.model_dump())
    reviews_db[review_id] = new_review
    return new_review

@router.delete("/{review_id}")
async def delete_review(review_id: str = Path(...)):
    """Delete a review."""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    del reviews_db[review_id]
    return {"detail": "Review deleted"}
