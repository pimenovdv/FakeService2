from typing import Dict, Any, Optional
from src.client import AgentClient
from src.parser import ScreenParser
from src.logger import get_logger

logger = get_logger()

class AgentFlow:
    """
    Manages the overall flow of the agent through the screens,
    handling transitions and completions.
    """
    def __init__(self, service_id: str, client: AgentClient):
        self.service_id = service_id
        self.client = client
        self.current_screen_id = "1"
        self.completed = False

    async def start(self) -> Dict[str, Any]:
        """
        Starts the flow by fetching the initial screen HTML.
        """
        logger.info(f"Starting flow for service {self.service_id}")
        url = f"/{self.service_id}/1"
        html = await self.client.fetch_html(url)
        return self._parse_and_prepare_screen(html)

    async def submit_step(self, answers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Submits answers for the current screen and processes the transition.
        """
        payload = {
            "service_id": self.service_id,
            "current_screen_id": self.current_screen_id,
            "answers": answers
        }

        # Simulate form submission exactly as the frontend would
        response = await self.client.post("/api/screens/next_step", json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("completed"):
            self.completed = True
            return None

        next_screen = data.get("next_screen", {})
        self.current_screen_id = next_screen.get("id")

        if not self.current_screen_id:
            raise ValueError("Next screen ID not found in response.")

        logger.info(f"Transitioning to screen {self.current_screen_id}")

        # In a real SSR environment, the frontend fetches the new page via routing.
        # We mimic this by fetching the new HTML for the screen.
        url = f"/{self.service_id}/{self.current_screen_id}"
        try:
            html = await self.client.fetch_html(url)
            return self._parse_and_prepare_screen(html)
        except Exception as e:
            # If the SSR app is configured differently and just returned JSON, fallback
            return next_screen

    def _parse_and_prepare_screen(self, html: str) -> Dict[str, Any]:
        parser = ScreenParser(html)
        parsed_screen = parser.parse()
        logger.debug(f"Parsed screen: {parsed_screen}")
        return parsed_screen
