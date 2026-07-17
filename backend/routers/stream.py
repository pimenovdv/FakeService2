import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

async def mock_event_generator():
    events = [
        "data: {\"message\": \"Connected\"}\n\n",
        "data: {\"event\": \"update\", \"data\": 1}\n\n",
        "data: {\"event\": \"update\", \"data\": 2}\n\n",
        "data: {\"event\": \"done\"}\n\n"
    ]
    for event in events:
        yield event
        await asyncio.sleep(0.1)

@router.get("/api/stream")
async def stream_events():
    return StreamingResponse(mock_event_generator(), media_type="text/event-stream")
