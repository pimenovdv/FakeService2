from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

router = APIRouter(prefix="/api/profile", tags=["profile"])

class UserProfile(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

# In-memory store for mock profile
# Simulate a single user for simplicity
MOCK_PROFILE_ID = str(uuid.uuid4())
mock_profile = UserProfile(
    id=MOCK_PROFILE_ID,
    username="mockuser",
    email="mockuser@example.com",
    first_name="Mock",
    last_name="User",
    bio="I am a mock user."
)

@router.get("", response_model=UserProfile)
async def get_profile():
    return mock_profile

@router.put("", response_model=UserProfile)
async def update_profile(profile_update: UserProfileUpdate):
    global mock_profile
    update_data = profile_update.model_dump(exclude_unset=True)

    updated_profile_data = mock_profile.model_dump()
    updated_profile_data.update(update_data)

    mock_profile = UserProfile(**updated_profile_data)

    return mock_profile
