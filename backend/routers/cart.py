from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

router = APIRouter(prefix="/api/cart", tags=["cart"])

# Mock database for cart items
# The structure will just be a single shopping cart for simplicity.
# { item_id: CartItem }
cart_db = {}

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int
    name: Optional[str] = None
    price: Optional[float] = None

class CartItem(BaseModel):
    id: str
    product_id: str
    quantity: int
    name: Optional[str] = None
    price: Optional[float] = None

class CartSummary(BaseModel):
    items: List[CartItem]
    total_items: int
    total_price: float

@router.get("", response_model=CartSummary)
async def get_cart():
    """Retrieve the current shopping cart."""
    items = list(cart_db.values())
    total_items = sum(item.quantity for item in items)
    total_price = sum((item.price or 0.0) * item.quantity for item in items)
    return CartSummary(items=items, total_items=total_items, total_price=total_price)

@router.post("/items", response_model=CartItem)
async def add_item_to_cart(item: CartItemCreate):
    """Add a new item to the shopping cart."""
    # Check if product is already in cart, if so, just increase quantity
    for existing_item in cart_db.values():
        if existing_item.product_id == item.product_id:
            existing_item.quantity += item.quantity
            # optionally update name and price if provided
            if item.name is not None:
                existing_item.name = item.name
            if item.price is not None:
                existing_item.price = item.price
            return existing_item

    item_id = str(uuid.uuid4())
    new_item = CartItem(id=item_id, **item.model_dump())
    cart_db[item_id] = new_item
    return new_item

@router.delete("/items/{item_id}")
async def remove_item_from_cart(item_id: str = Path(...)):
    """Remove an item from the shopping cart."""
    if item_id not in cart_db:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    del cart_db[item_id]
    return {"detail": "Item removed from cart"}

@router.delete("")
async def clear_cart():
    """Clear all items from the shopping cart."""
    cart_db.clear()
    return {"detail": "Cart cleared"}
