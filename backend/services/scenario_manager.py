import json
import os
from fastapi import HTTPException

MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")

class ScenarioManager:
    @staticmethod
    def get_initial_screen(service_id: str) -> dict:
        filename = f"{service_id}_screen_1.json"
        filepath = os.path.join(MOCK_DATA_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"Initial screen for service_id '{service_id}' not found.")

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON for service_id '{service_id}'.")

    @staticmethod
    def get_next_screen(service_id: str, current_screen_id: str, answers: dict) -> dict:
        # Load current screen to validate answers
        current_filename = f"{service_id}_{current_screen_id}.json"
        current_filepath = os.path.join(MOCK_DATA_DIR, current_filename)
        if not os.path.exists(current_filepath):
            raise HTTPException(status_code=404, detail=f"Current screen '{current_screen_id}' for service_id '{service_id}' not found.")

        with open(current_filepath, "r", encoding="utf-8") as f:
            try:
                current_data = json.load(f)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON for service_id '{service_id}', screen '{current_screen_id}'.")

        # Basic validation
        for component in current_data.get("components", []):
            comp_id = component.get("id")
            for validation in component.get("validations", []):
                if validation.get("type") == "required":
                    if comp_id not in answers or answers[comp_id] is None or str(answers[comp_id]).strip() == "":
                        raise HTTPException(status_code=400, detail=validation.get("message", f"{comp_id} is required"))

        # Mock logic for determining the next screen
        if service_id == "service_1" and current_screen_id == "screen_1":
            # Just move to screen 2
            next_screen_id = "screen_2"
        elif service_id == "service_1" and current_screen_id == "screen_2":
            return {"completed": True}
        else:
            raise HTTPException(status_code=404, detail=f"No next step defined for service_id '{service_id}', screen '{current_screen_id}'.")

        filename = f"{service_id}_{next_screen_id}.json"
        filepath = os.path.join(MOCK_DATA_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"Next screen '{next_screen_id}' for service_id '{service_id}' not found.")

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {"next_screen": data, "completed": False}
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON for service_id '{service_id}', screen '{next_screen_id}'.")
