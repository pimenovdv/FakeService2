from fastapi import APIRouter
from models.request import StartRequest
from models.screen import ScreenDef
from services.scenario_manager import ScenarioManager

router = APIRouter(prefix="/api/screens", tags=["screens"])

@router.post("/start", response_model=ScreenDef)
def start_scenario(request: StartRequest):
    screen_data = ScenarioManager.get_initial_screen(request.service_id)
    return screen_data
