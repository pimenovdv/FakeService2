import pytest
from unittest.mock import AsyncMock, MagicMock
from src.actions import fetch_autocomplete_options, simulate_form_submission
import json

@pytest.mark.asyncio
async def test_fetch_autocomplete_options_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "Test"}]
    mock_client.get.return_value = mock_response

    result = await fetch_autocomplete_options(mock_client, "/api/test", "query_text")

    mock_client.get.assert_called_once_with("/api/test", params={"query": "query_text"})
    mock_response.raise_for_status.assert_called_once()
    assert result == [{"id": 1, "name": "Test"}]

@pytest.mark.asyncio
async def test_fetch_autocomplete_options_json_error():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    mock_response.text = "Not JSON"
    mock_client.get.return_value = mock_response

    result = await fetch_autocomplete_options(mock_client, "/api/test", "query_text")

    assert result == {"error": "Invalid JSON response", "content": "Not JSON"}

@pytest.mark.asyncio
async def test_simulate_form_submission_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"next_screen": "screen_2"}
    mock_client.post.return_value = mock_response

    payload = {"field1": "value1"}
    result = await simulate_form_submission(mock_client, "/api/submit", payload)

    mock_client.post.assert_called_once_with("/api/submit", json=payload)
    mock_response.raise_for_status.assert_called_once()
    assert result == {"next_screen": "screen_2"}

@pytest.mark.asyncio
async def test_simulate_form_submission_json_error():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    mock_response.text = "Bad Response"
    mock_client.post.return_value = mock_response

    result = await simulate_form_submission(mock_client, "/api/submit", {})

    assert result == {"error": "Invalid JSON response", "content": "Bad Response"}
