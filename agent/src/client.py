import httpx
from typing import Any, Dict, Optional
from src.logger import get_logger

logger = get_logger()

class AgentClient:
    """
    A robust HTTP client for interacting with the Angular SSR backend.
    Manages cookies and headers to simulate a real user session.
    """

    def __init__(self, base_url: str = "http://localhost:4200", default_headers: Optional[Dict[str, str]] = None):
        if default_headers is None:
            default_headers = {
                "User-Agent": "Agent/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }

        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=default_headers,
            follow_redirects=True,
            timeout=30.0
        )

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Perform a GET request."""
        logger.info(f"GET request to {url}")
        try:
            response = await self.client.get(url, **kwargs)
            logger.info(f"Response from {url}: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error during GET request to {url}: {e}")
            raise

    async def fetch_html(self, url: str) -> str:
        """Fetch pre-rendered HTML from a given URL."""
        logger.debug(f"Fetching HTML for {url}")
        response = await self.get(url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError while fetching HTML from {url}: {e}")
            raise
        return response.text

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Perform a POST request."""
        logger.info(f"POST request to {url}")
        try:
            response = await self.client.post(url, **kwargs)
            logger.info(f"Response from {url}: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error during POST request to {url}: {e}")
            raise

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
