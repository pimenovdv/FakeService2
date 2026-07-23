from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/search", tags=["Search"])

class SearchResult(BaseModel):
    id: int
    title: str
    description: str
    type: str

@router.get("", response_model=List[SearchResult])
async def search(q: Optional[str] = Query(None, description="Search query")):
    if not q:
        return []

    # Mock data to search through
    mock_data = [
        SearchResult(id=1, title="User Profile", description="Manage your account settings and profile information", type="page"),
        SearchResult(id=2, title="Dashboard", description="Overview of your system activity and metrics", type="page"),
        SearchResult(id=3, title="Settings", description="Configure application preferences and behavior", type="page"),
        SearchResult(id=4, title="Documentation", description="Read the system documentation and API guides", type="document"),
        SearchResult(id=5, title="Billing", description="View invoices and manage payment methods", type="page"),
        SearchResult(id=6, title="John Doe", description="Senior Software Engineer", type="user"),
        SearchResult(id=7, title="Jane Smith", description="Product Manager", type="user"),
    ]

    q_lower = q.lower()

    # Simple search simulation (matching title or description)
    results = [
        item for item in mock_data
        if q_lower in item.title.lower() or q_lower in item.description.lower()
    ]

    return results
