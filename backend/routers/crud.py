from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, List
import uuid

router = APIRouter(prefix="/api/resource", tags=["crud"])

# In-memory storage for resources.
# Structure: { resource_name: { item_id: { ...item_data... } } }
resources_db: Dict[str, Dict[str, Any]] = {}


@router.get("/{resource_name}", response_model=List[Dict[str, Any]])
async def get_resources(resource_name: str = Path(...)):
    """Retrieve all items for a given resource."""
    items = resources_db.get(resource_name, {})
    return list(items.values())


@router.get("/{resource_name}/{item_id}", response_model=Dict[str, Any])
async def get_resource(resource_name: str = Path(...), item_id: str = Path(...)):
    """Retrieve a specific item by ID."""
    items = resources_db.get(resource_name, {})
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@router.post("/{resource_name}", response_model=Dict[str, Any], status_code=201)
async def create_resource(resource_name: str = Path(...), item_data: Dict[str, Any] = Body(default_factory=dict)):
    """Create a new item for a given resource."""
    if resource_name not in resources_db:
        resources_db[resource_name] = {}

    # Generate an ID if not provided
    item_id = item_data.get("id") or str(uuid.uuid4())
    item_data["id"] = item_id

    resources_db[resource_name][item_id] = item_data
    return item_data


@router.put("/{resource_name}/{item_id}", response_model=Dict[str, Any])
async def update_resource(resource_name: str = Path(...), item_id: str = Path(...), item_data: Dict[str, Any] = Body(default_factory=dict)):
    """Update an existing item by ID."""
    items = resources_db.get(resource_name, {})
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    # Ensure the ID in the data matches the path
    item_data["id"] = item_id
    items[item_id].update(item_data)
    return items[item_id]


@router.delete("/{resource_name}/{item_id}", status_code=204)
async def delete_resource(resource_name: str = Path(...), item_id: str = Path(...)):
    """Delete an item by ID."""
    items = resources_db.get(resource_name, {})
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    del items[item_id]
    return None
