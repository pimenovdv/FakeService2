import uuid
import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

# In-memory storage for tickets
tickets_db: Dict[str, dict] = {}

class TicketCreate(BaseModel):
    subject: str = Field(..., description="Subject of the ticket")
    description: str = Field(..., description="Description of the issue")
    user_id: str = Field(..., description="ID of the user creating the ticket")

class TicketUpdate(BaseModel):
    status: str = Field(..., description="New status for the ticket")

class TicketResponse(BaseModel):
    ticket_id: str
    subject: str
    description: str
    user_id: str
    status: str
    created_at: str

@router.get("", response_model=List[TicketResponse])
async def get_tickets():
    """Retrieves all support tickets."""
    return list(tickets_db.values())

@router.post("", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    """Creates a new support ticket."""
    ticket_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat() + "Z"
    ticket_data = {
        "ticket_id": ticket_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "user_id": ticket.user_id,
        "status": "open",
        "created_at": now
    }
    tickets_db[ticket_id] = ticket_data
    return ticket_data

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket_status(ticket_id: str, update: TicketUpdate):
    """Updates the status of a support ticket by ID."""
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    tickets_db[ticket_id]["status"] = update.status
    return tickets_db[ticket_id]
