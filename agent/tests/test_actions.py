import unittest
from unittest.mock import AsyncMock, MagicMock
from src.actions import AgentActions
from src.client import AgentClient

class TestAgentActions(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_autocomplete_options(self):
        mock_client = AsyncMock(spec=AgentClient)
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1, "name": "Option 1"}]
        mock_client.get.return_value = mock_response

        actions = AgentActions(client=mock_client)
        result = await actions.fetch_autocomplete_options("/api/options", params={"q": "Opt"})

        mock_client.get.assert_called_once_with("/api/options", params={"q": "Opt"})
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, [{"id": 1, "name": "Option 1"}])

    async def test_simulate_form_submission(self):
        mock_client = AsyncMock(spec=AgentClient)
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_client.post.return_value = mock_response

        actions = AgentActions(client=mock_client)
        payload = {"answers": {"field_1": "value_1"}}
        result = await actions.simulate_form_submission("/next_step", payload)

        mock_client.post.assert_called_once_with("/next_step", json=payload)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "success"})
