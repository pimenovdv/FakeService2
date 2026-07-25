from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/user-tasks", tags=["user_tasks"])

class UserTask(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime

class UserTaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    completed: bool = False

class UserTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    completed: Optional[bool] = None

# In-memory store for user tasks
MOCK_USER_TASKS = {}

@router.post("", response_model=UserTask)
async def create_user_task(task: UserTaskCreate):
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    new_task = UserTask(
        id=task_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=now,
        updated_at=now
    )
    MOCK_USER_TASKS[task_id] = new_task
    return new_task

@router.get("", response_model=List[UserTask])
async def list_user_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status")
):
    tasks = list(MOCK_USER_TASKS.values())
    if completed is not None:
        tasks = [task for task in tasks if task.completed == completed]
    # Sort by created_at descending
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    return tasks

@router.get("/{task_id}", response_model=UserTask)
async def get_user_task(task_id: str):
    task = MOCK_USER_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=UserTask)
async def update_user_task(task_id: str, task_update: UserTaskUpdate):
    task = MOCK_USER_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    if update_data:
        updated_task = task.model_copy(update=update_data)
        updated_task.updated_at = datetime.utcnow()
        MOCK_USER_TASKS[task_id] = updated_task
        return updated_task
    return task

@router.delete("/{task_id}")
async def delete_user_task(task_id: str):
    if task_id not in MOCK_USER_TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    del MOCK_USER_TASKS[task_id]
    return {"status": "deleted", "id": task_id}
