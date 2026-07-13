import logging
from typing import Dict, Any, Optional
from src.client import AgentClient
from src.parser import ScreenParser

logger = logging.getLogger(__name__)

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
        url = f"/{self.service_id}/1"
        logger.info(f"AgentFlow starting: fetching {url}")
        try:
            html = await self.client.fetch_html(url)
            logger.info(f"AgentFlow successfully fetched {url}")
            return self._parse_and_prepare_screen(html)
        except Exception as e:
            logger.error(f"AgentFlow failed to start fetching {url}: {e}")
            return {"error": "Failed to fetch screen: " + str(e)}

    async def submit_step(self, answers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Submits answers for the current screen and processes the transition.
        """
        payload = {
            "service_id": self.service_id,
            "current_screen_id": self.current_screen_id,
            "answers": answers
        }

        logger.info(f"AgentFlow submitting step for screen {self.current_screen_id} with answers: {answers}")

        try:
            # Simulate form submission exactly as the frontend would
            response = await self.client.post("/api/screens/next_step", json=payload)
            data = response.json()
            logger.info(f"AgentFlow received post response: {data}")

            if data.get("completed"):
                self.completed = True
                return None

            next_screen = data.get("next_screen", {})
            self.current_screen_id = next_screen.get("id")

            if not self.current_screen_id:
                raise ValueError("Next screen ID not found in response.")

            # In a real SSR environment, the frontend fetches the new page via routing.
            # We mimic this by fetching the new HTML for the screen.
            url = f"/{self.service_id}/{self.current_screen_id}"
            try:
                html = await self.client.fetch_html(url)
                return self._parse_and_prepare_screen(html)
            except Exception as e:
                # If the SSR app is configured differently and just returned JSON, fallback
                logger.warning(f"Failed to fetch next screen HTML: {e}. Falling back to next_screen json.")
                return next_screen

        except Exception as e:
            logger.error(f"AgentFlow encountered error during submit_step: {e}")
            return {"error": str(e)}

    def _parse_and_prepare_screen(self, html: str) -> Dict[str, Any]:
        parser = ScreenParser(html)
        return parser.parse()
