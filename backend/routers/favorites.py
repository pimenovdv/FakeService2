from fastapi import APIRouter, HTTPException, Path
from typing import List

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

# Mock database for favorites (using a set to store unique product_ids)
favorites_db = set()

@router.get("", response_model=List[str])
async def get_favorites():
    """Retrieve all favorite product IDs."""
    return list(favorites_db)

@router.post("/{product_id}", response_model=dict)
async def add_favorite(product_id: str = Path(...)):
    """Add a product to favorites."""
    if product_id in favorites_db:
        return {"detail": "Product is already in favorites"}

    favorites_db.add(product_id)
    return {"detail": "Product added to favorites"}

@router.delete("/{product_id}", response_model=dict)
async def remove_favorite(product_id: str = Path(...)):
    """Remove a product from favorites."""
    if product_id not in favorites_db:
        raise HTTPException(status_code=404, detail="Product not found in favorites")

    favorites_db.remove(product_id)
    return {"detail": "Product removed from favorites"}
