from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/api/events",
    tags=["events"]
)

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None

class Event(EventBase):
    id: str

# In-memory storage for mock events
mock_events: List[Event] = [
    Event(
        id=str(uuid.uuid4()),
        title="Team Sync",
        description="Weekly team synchronization meeting.",
        start_time=datetime(2024, 1, 1, 10, 0),
        end_time=datetime(2024, 1, 1, 11, 0),
        location="Meeting Room 1"
    ),
    Event(
        id=str(uuid.uuid4()),
        title="Lunch with Client",
        description="Discussing the new project proposal.",
        start_time=datetime(2024, 1, 2, 12, 30),
        end_time=datetime(2024, 1, 2, 14, 0),
        location="Downtown Cafe"
    )
]

@router.get("", response_model=List[Event])
async def get_events():
    """
    List all mock calendar events.
    """
    return mock_events

@router.post("", response_model=Event, status_code=201)
async def create_event(event_data: EventBase):
    """
    Create a new mock calendar event.
    """
    new_event = Event(id=str(uuid.uuid4()), **event_data.model_dump())
    mock_events.append(new_event)
    return new_event
