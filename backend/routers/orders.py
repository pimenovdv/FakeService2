from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItem] = Field(..., min_length=1)
    customer_id: str

class Order(BaseModel):
    id: str
    items: List[OrderItem]
    customer_id: str
    total_amount: float
    status: str
    created_at: datetime

# In-memory store for orders
MOCK_ORDERS = {}

@router.post("", response_model=Order)
async def create_order(order: OrderCreate):
    order_id = str(uuid.uuid4())
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    total_amount = sum(item.price * item.quantity for item in order.items)

    new_order = Order(
        id=order_id,
        items=order.items,
        customer_id=order.customer_id,
        total_amount=total_amount,
        status="pending",
        created_at=now
    )
    MOCK_ORDERS[order_id] = new_order
    return new_order

@router.get("", response_model=List[Order])
async def list_orders():
    orders = list(MOCK_ORDERS.values())
    # Sort by created_at descending
    orders.sort(key=lambda x: x.created_at, reverse=True)
    return orders

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    if order_id not in MOCK_ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    return MOCK_ORDERS[order_id]
