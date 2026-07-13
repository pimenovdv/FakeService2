import json
import os
import re
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
                val_type = validation.get("type")
                val_message = validation.get("message", f"Validation failed for {comp_id}")

                if val_type == "required":
                    if comp_id not in answers or answers[comp_id] is None or str(answers[comp_id]).strip() == "":
                        raise HTTPException(status_code=400, detail=val_message)

                # Check other validations only if the value is provided
                if comp_id in answers and answers[comp_id] is not None and str(answers[comp_id]).strip() != "":
                    val_value = validation.get("value")
                    answer = answers[comp_id]

                    if val_type == "regex":
                        if not re.match(val_value, str(answer)):
                            raise HTTPException(status_code=400, detail=val_message)
                    elif val_type == "minLength":
                        if len(str(answer)) < int(val_value):
                            raise HTTPException(status_code=400, detail=val_message)
                    elif val_type == "maxLength":
                        if len(str(answer)) > int(val_value):
                            raise HTTPException(status_code=400, detail=val_message)
                    elif val_type == "min":
                        try:
                            if float(answer) < float(val_value):
                                raise HTTPException(status_code=400, detail=val_message)
                        except ValueError:
                            # It might be a date string
                            from datetime import datetime
                            try:
                                v = datetime.fromisoformat(str(answer))
                                r = datetime.fromisoformat(str(val_value))
                                if v < r:
                                    raise HTTPException(status_code=400, detail=val_message)
                            except ValueError:
                                raise HTTPException(status_code=400, detail=val_message)
                    elif val_type == "max":
                        try:
                            if float(answer) > float(val_value):
                                raise HTTPException(status_code=400, detail=val_message)
                        except ValueError:
                            from datetime import datetime
                            try:
                                v = datetime.fromisoformat(str(answer))
                                r = datetime.fromisoformat(str(val_value))
                                if v > r:
                                    raise HTTPException(status_code=400, detail=val_message)
                            except ValueError:
                                raise HTTPException(status_code=400, detail=val_message)

        # Cross-field validation
        for cross_validation in current_data.get("crossValidations", []) or []:
            if cross_validation.get("type") == "match":
                fields = cross_validation.get("fields", [])
                if len(fields) > 1:
                    first_val = answers.get(fields[0])
                    for field in fields[1:]:
                        if answers.get(field) != first_val:
                            val_message = cross_validation.get("message", "Fields do not match")
                            raise HTTPException(status_code=400, detail=val_message)

        # Configuration-driven routing logic
        routing_filename = f"{service_id}_routing.json"
        routing_filepath = os.path.join(MOCK_DATA_DIR, routing_filename)

        if not os.path.exists(routing_filepath):
            raise HTTPException(status_code=404, detail=f"Routing configuration for service_id '{service_id}' not found.")

        with open(routing_filepath, "r", encoding="utf-8") as f:
            try:
                routing_data = json.load(f)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding routing JSON for service_id '{service_id}'.")

        if current_screen_id not in routing_data:
            raise HTTPException(status_code=404, detail=f"No next step defined for service_id '{service_id}', screen '{current_screen_id}'.")

        next_screen_id = routing_data[current_screen_id]
        if next_screen_id == "completed":
            return {"completed": True}

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

    @staticmethod
    def get_previous_screen(service_id: str, current_screen_id: str) -> dict:
        routing_filename = f"{service_id}_routing.json"
        routing_filepath = os.path.join(MOCK_DATA_DIR, routing_filename)

        if not os.path.exists(routing_filepath):
            raise HTTPException(status_code=404, detail=f"Routing configuration for service_id '{service_id}' not found.")

        with open(routing_filepath, "r", encoding="utf-8") as f:
            try:
                routing_data = json.load(f)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding routing JSON for service_id '{service_id}'.")

        # Reverse lookup in routing config
        previous_screen_id = None
        for k, v in routing_data.items():
            if v == current_screen_id:
                previous_screen_id = k
                break

        if not previous_screen_id:
            raise HTTPException(status_code=404, detail=f"Previous screen not found for service_id '{service_id}', screen '{current_screen_id}'.")

        filename = f"{service_id}_{previous_screen_id}.json"
        filepath = os.path.join(MOCK_DATA_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"Previous screen file '{previous_screen_id}' for service_id '{service_id}' not found.")

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON for service_id '{service_id}', screen '{previous_screen_id}'.")
