import pytest
import httpx
from src.client import AgentClient

@pytest.mark.asyncio
async def test_agent_client_initialization():
    client = AgentClient()
    assert client.client.base_url == httpx.URL("http://localhost:4200")
    assert "User-Agent" in client.client.headers
    assert client.client.headers["User-Agent"] == "Agent/1.0"
    await client.close()

@pytest.mark.asyncio
async def test_agent_client_custom_headers():
    custom_headers = {"User-Agent": "CustomAgent/2.0", "X-Test": "test"}
    client = AgentClient(default_headers=custom_headers)
    assert client.client.headers["User-Agent"] == "CustomAgent/2.0"
    assert client.client.headers["X-Test"] == "test"
    await client.close()

@pytest.mark.asyncio
async def test_agent_client_context_manager():
    async with AgentClient() as client:
        assert isinstance(client, AgentClient)
        assert not client.client.is_closed

    assert client.client.is_closed
