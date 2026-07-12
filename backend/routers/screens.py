from fastapi import APIRouter
from models.request import StartRequest, NextStepRequest, NextStepResponse, PrevStepRequest, PrevStepResponse
from models.screen import ScreenDef
from services.scenario_manager import ScenarioManager

router = APIRouter(prefix="/api/screens", tags=["screens"])

@router.post("/start", response_model=ScreenDef)
def start_scenario(request: StartRequest):
    screen_data = ScenarioManager.get_initial_screen(request.service_id)
    return screen_data

@router.post("/next_step", response_model=NextStepResponse)
def next_step(request: NextStepRequest):
    return ScenarioManager.get_next_screen(request.service_id, request.current_screen_id, request.answers)

@router.post("/prev_step", response_model=PrevStepResponse)
def prev_step(request: PrevStepRequest):
    return ScenarioManager.get_prev_screen(request.service_id, request.current_screen_id)
