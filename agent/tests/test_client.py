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

@pytest.mark.asyncio
async def test_agent_client_fetch_html(httpx_mock):
    html_content = "<html><body><h1>Hello</h1></body></html>"
    httpx_mock.add_response(url="http://localhost:4200/test", text=html_content)

    async with AgentClient() as client:
        html = await client.fetch_html("http://localhost:4200/test")
        assert html == html_content

@pytest.mark.asyncio
async def test_agent_client_fetch_html_http_error_handling(httpx_mock):
    httpx_mock.add_response(url="http://localhost:4200/error", status_code=500)

    async with AgentClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.fetch_html("http://localhost:4200/error")

@pytest.mark.asyncio
async def test_agent_client_auth_token_management():
    client = AgentClient()

    assert client.auth_token is None
    assert "Authorization" not in client.client.headers

    token = "test_mock_token_123"
    client.set_auth_token(token)
    assert client.auth_token == token
    assert client.client.headers["Authorization"] == f"Bearer {token}"

    client.clear_auth_token()
    assert client.auth_token is None
    assert "Authorization" not in client.client.headers

    await client.close()
