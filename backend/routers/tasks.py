import asyncio
import uuid
from typing import Dict
from fastapi import APIRouter, BackgroundTasks, HTTPException, Path

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# In-memory storage for task statuses.
# Structure: { task_id: "pending" | "completed" | "failed" }
tasks_db: Dict[str, str] = {}

async def mock_background_task(task_id: str):
    """Simulates a background task that takes a few seconds to complete."""
    try:
        await asyncio.sleep(2)  # Simulate some work
        tasks_db[task_id] = "completed"
    except Exception:
        tasks_db[task_id] = "failed"

@router.post("", response_model=Dict[str, str], status_code=202)
async def start_task(background_tasks: BackgroundTasks):
    """Starts a mock background task and returns its ID."""
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = "pending"
    background_tasks.add_task(mock_background_task, task_id)
    return {"task_id": task_id, "status": "pending"}

@router.get("/{task_id}", response_model=Dict[str, str])
async def get_task_status(task_id: str = Path(...)):
    """Retrieves the status of a background task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"task_id": task_id, "status": tasks_db[task_id]}
