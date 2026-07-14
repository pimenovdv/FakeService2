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

    async def test_download_and_parse_file_json(self):
        mock_client = AsyncMock(spec=AgentClient)
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}
        mock_client.get.return_value = mock_response

        actions = AgentActions(client=mock_client)
        result = await actions.download_and_parse_file("/file.json")

        mock_client.get.assert_called_once_with("/file.json")
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"key": "value"})

    async def test_download_and_parse_file_text(self):
        mock_client = AsyncMock(spec=AgentClient)
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "hello world"
        mock_client.get.return_value = mock_response

        actions = AgentActions(client=mock_client)
        result = await actions.download_and_parse_file("/file.txt")

        mock_client.get.assert_called_once_with("/file.txt")
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, "hello world")
