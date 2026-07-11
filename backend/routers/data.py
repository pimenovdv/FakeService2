from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/api/data", tags=["data"])
MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")

@router.get("/{data_source}")
def get_dynamic_data(data_source: str):
    filename = f"{data_source}.json"
    filepath = os.path.join(MOCK_DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Data source '{data_source}' not found.")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON for data source '{data_source}'.")
