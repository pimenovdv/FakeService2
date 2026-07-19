from fastapi import APIRouter, HTTPException, Request, Body
from typing import Dict, Any, Optional
import time

router = APIRouter(prefix="/api/cache", tags=["cache"])

# In-memory store for cache
# Structure: { "key": {"value": value, "expires_at": timestamp_or_none} }
cache_store: Dict[str, Dict[str, Any]] = {}

@router.post("/{key}")
async def set_cache(key: str, request: Request, ttl: Optional[int] = None):
    """
    Store a value in the cache with an optional TTL (in seconds).
    Expects a JSON body containing the value to store.
    """
    try:
        value = await request.json()
    except Exception:
        # Fallback to plain text if not JSON
        body = await request.body()
        value = body.decode("utf-8") if body else ""

    expires_at = time.time() + ttl if ttl is not None else None

    cache_store[key] = {
        "value": value,
        "expires_at": expires_at
    }

    return {"status": "success", "message": f"Key '{key}' set.", "ttl": ttl}

@router.get("/{key}")
async def get_cache(key: str):
    """
    Retrieve a value from the cache.
    Returns 404 if the key does not exist or has expired.
    """
    if key not in cache_store:
        raise HTTPException(status_code=404, detail="Key not found")

    entry = cache_store[key]

    # Check if expired
    if entry["expires_at"] is not None and time.time() > entry["expires_at"]:
        del cache_store[key]
        raise HTTPException(status_code=404, detail="Key expired")

    return {"key": key, "value": entry["value"]}

@router.delete("/{key}")
async def delete_cache(key: str):
    """
    Delete a key from the cache.
    """
    if key in cache_store:
        del cache_store[key]
        return {"status": "success", "message": f"Key '{key}' deleted."}

    raise HTTPException(status_code=404, detail="Key not found")
