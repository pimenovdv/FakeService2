import uuid
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/api/comments", tags=["comments"])

class CommentCreate(BaseModel):
    user_id: str
    text: str

class Comment(BaseModel):
    id: str
    entity_id: str
    user_id: str
    text: str
    created_at: str

# In-memory store: { entity_id: [Comment, ...] }
mock_comments_store: Dict[str, List[Comment]] = {}

@router.get("/{entity_id}", response_model=List[Comment])
async def get_comments(entity_id: str):
    """
    Get all comments for a specific entity.
    """
    return mock_comments_store.get(entity_id, [])

@router.post("/{entity_id}", response_model=Comment)
async def create_comment(entity_id: str, comment: CommentCreate):
    """
    Create a new comment for a specific entity.
    """
    new_comment = Comment(
        id=str(uuid.uuid4()),
        entity_id=entity_id,
        user_id=comment.user_id,
        text=comment.text,
        created_at=datetime.utcnow().isoformat() + "Z"
    )
    if entity_id not in mock_comments_store:
        mock_comments_store[entity_id] = []
    mock_comments_store[entity_id].append(new_comment)
    return new_comment

@router.delete("/{comment_id}")
async def delete_comment(comment_id: str):
    """
    Delete a specific comment by ID.
    """
    for entity_id, comments in mock_comments_store.items():
        for i, c in enumerate(comments):
            if c.id == comment_id:
                deleted_comment = comments.pop(i)
                return {"status": "success", "id": deleted_comment.id}
    raise HTTPException(status_code=404, detail="Comment not found")
