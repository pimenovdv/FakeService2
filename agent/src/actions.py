from typing import Dict, Any, Optional
from .client import AgentClient

async def fetch_autocomplete_options(client: AgentClient, endpoint: str, query_params: Optional[Dict[str, str]] = None) -> Any:
    """
    Fetches autocomplete options from the backend API.

    Args:
        client: The HTTP client session.
        endpoint: The API endpoint (e.g., "/api/data/regions").
        query_params: Optional query parameters (e.g., {"q": "search term"}).

    Returns:
        The parsed JSON response containing options.
    """
    response = await client.get(endpoint, params=query_params)
    response.raise_for_status()
    return response.json()

async def simulate_form_submission(client: AgentClient, service_id: str, current_screen_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a form submission by sending a POST request to the next_step endpoint.

    Args:
        client: The HTTP client session.
        service_id: The ID of the current service.
        current_screen_id: The ID of the screen being submitted.
        answers: The JSON payload containing filled form fields.

    Returns:
        The parsed JSON response which could be the NextStepResponse.
    """
    payload = {
        "service_id": service_id,
        "current_screen_id": current_screen_id,
        "answers": answers
    }

    response = await client.post("/api/screens/next_step", json=payload)
    response.raise_for_status()
    return response.json()
