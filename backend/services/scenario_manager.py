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
