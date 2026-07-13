import pytest
from unittest.mock import AsyncMock, MagicMock
from src.actions import AgentActions

@pytest.fixture
def mock_client():
    return AsyncMock()

@pytest.fixture
def agent_actions(mock_client):
    return AgentActions(mock_client)

@pytest.mark.asyncio
async def test_fetch_autocomplete_options(agent_actions, mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "Test"}]
    mock_client.get.return_value = mock_response

    result = await agent_actions.fetch_autocomplete_options("/api/test", params={"query": "test"})

    mock_client.get.assert_called_once_with("/api/test", params={"query": "test"})
    mock_response.raise_for_status.assert_called_once()
    assert result == [{"id": 1, "name": "Test"}]

@pytest.mark.asyncio
async def test_simulate_form_submission(agent_actions, mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"next_screen": "screen_2"}
    mock_client.post.return_value = mock_response

    payload = {"field1": "value1"}
    result = await agent_actions.simulate_form_submission("/api/submit", payload)

    mock_client.post.assert_called_once_with("/api/submit", json=payload)
    mock_response.raise_for_status.assert_called_once()
    assert result == {"next_screen": "screen_2"}
