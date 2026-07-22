from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["settings"])

class AppSettings(BaseModel):
    theme: str
    notifications_enabled: bool
    language: str
    timezone: str

class AppSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

# In-memory store for mock settings
mock_settings = AppSettings(
    theme="light",
    notifications_enabled=True,
    language="en",
    timezone="UTC"
)

@router.get("", response_model=AppSettings)
async def get_settings():
    return mock_settings

@router.put("", response_model=AppSettings)
async def update_settings(settings_update: AppSettingsUpdate):
    global mock_settings
    update_data = settings_update.model_dump(exclude_unset=True)

    updated_settings_data = mock_settings.model_dump()
    updated_settings_data.update(update_data)

    mock_settings = AppSettings(**updated_settings_data)

    return mock_settings
