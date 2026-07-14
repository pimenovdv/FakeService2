import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

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
        logger.debug(f"AgentClient GET request to {url}")
        try:
            response = await self.client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTPError on GET {url}: {e}")
            raise

    async def fetch_html(self, url: str) -> str:
        """Fetch pre-rendered HTML from a given URL."""
        logger.debug(f"AgentClient fetching HTML from {url}")
        response = await self.get(url)
        return response.text

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Perform a POST request."""
        logger.debug(f"AgentClient POST request to {url}")
        try:
            response = await self.client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTPError on POST {url}: {e}")
            raise

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
