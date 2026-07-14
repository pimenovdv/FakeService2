from typing import Any, Dict
from src.client import AgentClient

class AgentActions:
    """
    Simulates concrete actions the agent can take, such as fetching autocomplete
    options or submitting a form, by making appropriate API calls via the client.
    """

    def __init__(self, client: AgentClient):
        self.client = client

    async def fetch_autocomplete_options(self, url: str, params: Dict[str, Any] = None) -> Any:
        """
        Fetch autocomplete options for a given endpoint.
        """
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def simulate_form_submission(self, url: str, payload: Dict[str, Any]) -> Any:
        """
        Simulate form submission by making a POST request with the given payload.
        """
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def download_and_parse_file(self, url: str) -> Any:
        """
        Download a file from the given URL and parse it if it's JSON,
        otherwise return its text content.
        """
        response = await self.client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            return response.json()
        return response.text
