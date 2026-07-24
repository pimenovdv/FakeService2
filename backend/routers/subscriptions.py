import uuid
import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# In-memory storage for subscriptions
subscriptions_db: Dict[str, dict] = {}

class SubscriptionCreate(BaseModel):
    plan_id: str = Field(..., description="ID of the subscription plan")
    user_id: str = Field(..., description="ID of the user subscribing")

class SubscriptionResponse(BaseModel):
    subscription_id: str
    plan_id: str
    user_id: str
    status: str
    created_at: str

@router.post("", response_model=SubscriptionResponse)
async def create_subscription(sub: SubscriptionCreate):
    """Creates a new mock subscription."""
    sub_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat() + "Z"
    subscription_data = {
        "subscription_id": sub_id,
        "plan_id": sub.plan_id,
        "user_id": sub.user_id,
        "status": "active",
        "created_at": now
    }
    subscriptions_db[sub_id] = subscription_data
    return subscription_data

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: str):
    """Retrieves a subscription by ID."""
    if subscription_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscriptions_db[subscription_id]

@router.delete("/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """Cancels a subscription by ID."""
    if subscription_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # In a real app we might just change status to "canceled"
    subscriptions_db[subscription_id]["status"] = "canceled"
    return {"detail": "Subscription canceled successfully", "subscription_id": subscription_id}
