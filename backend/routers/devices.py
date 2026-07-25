from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/devices", tags=["devices"])

class Device(BaseModel):
    id: str
    name: str
    type: str
    os_version: Optional[str] = None
    created_at: datetime

class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    os_version: Optional[str] = None

# In-memory store for devices
MOCK_DEVICES = {}

@router.post("", response_model=Device)
async def register_device(device: DeviceCreate):
    device_id = str(uuid.uuid4())
    now = datetime.utcnow()
    new_device = Device(
        id=device_id,
        name=device.name,
        type=device.type,
        os_version=device.os_version,
        created_at=now
    )
    MOCK_DEVICES[device_id] = new_device
    return new_device

@router.get("", response_model=List[Device])
async def list_devices():
    devices = list(MOCK_DEVICES.values())
    # Sort by created_at descending
    devices.sort(key=lambda x: x.created_at, reverse=True)
    return devices

@router.delete("/{device_id}")
async def remove_device(device_id: str):
    if device_id not in MOCK_DEVICES:
        raise HTTPException(status_code=404, detail="Device not found")
    del MOCK_DEVICES[device_id]
    return {"status": "deleted", "id": device_id}
