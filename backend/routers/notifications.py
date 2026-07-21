from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class Notification(BaseModel):
    id: str
    user_id: str
    message: str
    type: str
    is_read: bool
    created_at: str

# In-memory mock store for notifications
mock_notifications_db: List[Notification] = []

def generate_mock_notifications(user_id: str):
    return [
        Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            message=f"Welcome, user {user_id}!",
            type="info",
            is_read=False,
            created_at=datetime.utcnow().isoformat() + "Z"
        ),
        Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            message="Your profile has been updated.",
            type="success",
            is_read=True,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
    ]

@router.get("", response_model=List[Notification])
def get_notifications(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    unread_only: bool = Query(False, description="Filter to show only unread notifications")
):
    # If a user_id is provided, auto-generate mock notifications if the DB is empty
    global mock_notifications_db
    if user_id and not any(n.user_id == user_id for n in mock_notifications_db):
        mock_notifications_db.extend(generate_mock_notifications(user_id))

    filtered_notifications = mock_notifications_db

    if user_id:
        filtered_notifications = [n for n in filtered_notifications if n.user_id == user_id]

    if unread_only:
        filtered_notifications = [n for n in filtered_notifications if not n.is_read]

    return filtered_notifications

@router.put("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(notification_id: str):
    global mock_notifications_db
    for notification in mock_notifications_db:
        if notification.id == notification_id:
            notification.is_read = True
            return notification

    raise HTTPException(status_code=404, detail="Notification not found")
