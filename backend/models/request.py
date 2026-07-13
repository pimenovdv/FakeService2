from typing import Dict, Any, Optional
from pydantic import BaseModel
from .screen import ScreenDef

class StartRequest(BaseModel):
    service_id: str

class NextStepRequest(BaseModel):
    service_id: str
    current_screen_id: str
    answers: Dict[str, Any]

class NextStepResponse(BaseModel):
    next_screen: Optional[ScreenDef] = None
    completed: bool = False

class PreviousStepRequest(BaseModel):
    service_id: str
    current_screen_id: str
