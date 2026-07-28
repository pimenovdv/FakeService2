from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/api/messages", tags=["messages"])

class MessageCreate(BaseModel):
    content: str
    recipient_id: str

class Message(BaseModel):
    id: str
    content: str
    recipient_id: str
    sender_id: str = "system"
    timestamp: str

messages_db = []

@router.get("", response_model=List[Message])
async def get_messages():
    """Retrieve all messages."""
    return messages_db

@router.post("", response_model=Message)
async def send_message(message_in: MessageCreate):
    """Send a new message."""
    new_message = Message(
        id=str(uuid4()),
        content=message_in.content,
        recipient_id=message_in.recipient_id,
        timestamp=datetime.utcnow().isoformat()
    )
    messages_db.append(new_message)
    return new_message

@router.delete("/{message_id}", response_model=dict)
async def delete_message(message_id: str = Path(...)):
    """Delete a specific message."""
    global messages_db
    for msg in messages_db:
        if msg.id == message_id:
            messages_db.remove(msg)
            return {"detail": "Message deleted"}

    raise HTTPException(status_code=404, detail="Message not found")
