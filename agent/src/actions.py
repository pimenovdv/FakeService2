import json
from src.client import AgentClient

async def fetch_autocomplete_options(client: AgentClient, endpoint: str, query: str) -> dict:
    """
    Simulates fetching autocomplete options by making an API call.
    """
    # Build query params
    # We'll just assume the query is passed via a query parameter or similar.
    # The endpoint in mock metadata typically looks like `/api/data/countries`
    # We will pass the query as a param just in case
    response = await client.get(endpoint, params={"query": query})
    response.raise_for_status()
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "content": response.text}

async def simulate_form_submission(client: AgentClient, url: str, payload: dict) -> dict:
    """
    Simulates form submission by making a POST request.
    """
    response = await client.post(url, json=payload)
    response.raise_for_status()
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "content": response.text}
