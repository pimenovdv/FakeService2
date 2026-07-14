from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/api/data", tags=["data"])
MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")

@router.get("/{data_source}")
def get_dynamic_data(data_source: str, page: int = 1, limit: int | None = None, search: str | None = None, sort_by: str | None = None, sort_order: str = "asc"):
    filename = f"{data_source}.json"
    filepath = os.path.join(MOCK_DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Data source '{data_source}' not found.")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                if search:
                    search_lower = search.lower()
                    data = [
                        item for item in data
                        if any(search_lower in str(v).lower() for v in (item.values() if isinstance(item, dict) else [item]))
                    ]

                if sort_by:
                    reverse = sort_order.lower() == "desc"

                    def sort_key(item):
                        if isinstance(item, dict) and sort_by in item:
                            val = item.get(sort_by)
                            return (0, val if val is not None else "")
                        return (1, str(item))

                    data.sort(key=sort_key, reverse=reverse)

                if limit is not None:
                    start = (page - 1) * limit
                    end = start + limit
                    return data[start:end]
            return data
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON for data source '{data_source}'.")
