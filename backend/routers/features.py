from fastapi import APIRouter, HTTPException
from typing import Dict
from pydantic import BaseModel

router = APIRouter(prefix="/api/features", tags=["features"])

# In-memory store for feature flags
# Structure: { "flag_name": bool }
feature_flags: Dict[str, bool] = {}

class FeatureFlagUpdate(BaseModel):
    enabled: bool

@router.get("")
async def get_features():
    """
    Retrieve all active feature flags.
    """
    return feature_flags

@router.put("/{flag}")
async def update_feature(flag: str, update: FeatureFlagUpdate):
    """
    Modify a feature flag state.
    """
    feature_flags[flag] = update.enabled
    return {"status": "success", "flag": flag, "enabled": update.enabled}

@router.delete("/{flag}")
async def delete_feature(flag: str):
    """
    Delete a feature flag.
    """
    if flag in feature_flags:
        del feature_flags[flag]
        return {"status": "success", "message": f"Flag '{flag}' deleted."}

    raise HTTPException(status_code=404, detail="Flag not found")
