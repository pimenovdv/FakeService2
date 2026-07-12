import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.actions import fetch_autocomplete_options, simulate_form_submission
from src.client import AgentClient

@pytest.mark.asyncio
async def test_fetch_autocomplete_options():
    mock_client = MagicMock(spec=AgentClient)

    # Mock the get response
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "Option 1"}]
    mock_client.get = AsyncMock(return_value=mock_response)

    endpoint = "/api/data/regions"
    query_params = {"q": "Option"}

    result = await fetch_autocomplete_options(mock_client, endpoint, query_params)

    mock_client.get.assert_called_once_with(endpoint, params=query_params)
    mock_response.raise_for_status.assert_called_once()
    assert result == [{"id": 1, "name": "Option 1"}]

@pytest.mark.asyncio
async def test_simulate_form_submission():
    mock_client = MagicMock(spec=AgentClient)

    # Mock the post response
    mock_response = MagicMock()
    mock_response.json.return_value = {"next_screen": {"id": "step2"}, "completed": False}
    mock_client.post = AsyncMock(return_value=mock_response)

    service_id = "test_service"
    current_screen_id = "step1"
    answers = {"field1": "value1"}

    result = await simulate_form_submission(mock_client, service_id, current_screen_id, answers)

    expected_payload = {
        "service_id": service_id,
        "current_screen_id": current_screen_id,
        "answers": answers
    }
    mock_client.post.assert_called_once_with("/api/screens/next_step", json=expected_payload)
    mock_response.raise_for_status.assert_called_once()
    assert result == {"next_screen": {"id": "step2"}, "completed": False}
