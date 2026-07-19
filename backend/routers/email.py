from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/email", tags=["Email"])

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str

class EmailOutboxItem(BaseModel):
    id: str
    to: EmailStr
    subject: str
    body: str
    sent_at: datetime

# In-memory storage for the email outbox
outbox: List[EmailOutboxItem] = []

@router.post("/send", response_model=EmailOutboxItem, status_code=201)
async def send_email(payload: EmailPayload):
    item = EmailOutboxItem(
        id=str(uuid.uuid4()),
        to=payload.to,
        subject=payload.subject,
        body=payload.body,
        sent_at=datetime.utcnow()
    )
    outbox.append(item)
    return item

@router.get("/outbox", response_model=List[EmailOutboxItem])
async def get_outbox():
    return outbox

@router.delete("/outbox", status_code=204)
async def clear_outbox():
    outbox.clear()
