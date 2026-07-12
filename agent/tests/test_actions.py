import pytest
from unittest.mock import AsyncMock, MagicMock
from src.actions import AgentActions

@pytest.mark.asyncio
async def test_fetch_autocomplete_options():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"},
        {"id": 3, "name": "Pineapple"}
    ]
    mock_client.get.return_value = mock_response

    # Test filtering by "apple" (should return Apple and Pineapple)
    results = await AgentActions.fetch_autocomplete_options(mock_client, "fruits", "apple")

    mock_client.get.assert_called_once_with("/api/data/fruits")
    assert len(results) == 2
    assert results[0]["name"] == "Apple"
    assert results[1]["name"] == "Pineapple"

@pytest.mark.asyncio
async def test_simulate_form_submission():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"next_screen": "screen_2"}
    mock_client.post.return_value = mock_response

    answers = {"field_1": "value_1"}

    result = await AgentActions.simulate_form_submission(mock_client, "service_1", "screen_1", answers)

    expected_payload = {
        "service_id": "service_1",
        "current_screen_id": "screen_1",
        "answers": answers
    }
    mock_client.post.assert_called_once_with("/api/screens/next_step", json=expected_payload)
    assert result == {"next_screen": "screen_2"}
