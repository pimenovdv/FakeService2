import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.flow import AgentFlow
from src.client import AgentClient

class TestAgentFlow(unittest.IsolatedAsyncioTestCase):
    async def test_start_flow(self):
        mock_client = AsyncMock(spec=AgentClient)
        mock_client.fetch_html.return_value = "<html><body><input id='test'/></body></html>"

        flow = AgentFlow(service_id="service_1", client=mock_client)

        with patch('src.flow.ScreenParser') as MockParser:
            mock_parser_instance = MockParser.return_value
            mock_parser_instance.parse.return_value = {"fields": [{"id": "test"}]}

            parsed_data = await flow.start()

            mock_client.fetch_html.assert_called_once_with("/service_1/1")
            self.assertEqual(parsed_data, {"fields": [{"id": "test"}]})
            self.assertEqual(flow.current_screen_id, "1")
            self.assertFalse(flow.completed)

    async def test_submit_step_next_screen(self):
        mock_client = AsyncMock(spec=AgentClient)

        # Mock the POST response for next_step
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "completed": False,
            "next_screen": {"id": "screen_2"}
        }
        mock_client.post.return_value = mock_post_response

        # Mock the fetch_html for the new screen
        mock_client.fetch_html.return_value = "<html><body><input id='next_test'/></body></html>"

        flow = AgentFlow(service_id="service_1", client=mock_client)
        flow.current_screen_id = "1"

        with patch('src.flow.ScreenParser') as MockParser:
            mock_parser_instance = MockParser.return_value
            mock_parser_instance.parse.return_value = {"fields": [{"id": "next_test"}]}

            answers = {"test": "value"}
            parsed_data = await flow.submit_step(answers)

            # Check post call
            mock_client.post.assert_called_once_with(
                "/api/screens/next_step",
                json={
                    "service_id": "service_1",
                    "current_screen_id": "1",
                    "answers": answers
                }
            )

            # Check fetch_html call for the new screen
            mock_client.fetch_html.assert_called_once_with("/service_1/screen_2")

            # Check state changes and returned data
            self.assertEqual(flow.current_screen_id, "screen_2")
            self.assertFalse(flow.completed)
            self.assertEqual(parsed_data, {"fields": [{"id": "next_test"}]})

    async def test_submit_step_completed(self):
        mock_client = AsyncMock(spec=AgentClient)

        # Mock the POST response for next_step indicating completion
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "completed": True
        }
        mock_client.post.return_value = mock_post_response

        flow = AgentFlow(service_id="service_1", client=mock_client)
        flow.current_screen_id = "screen_2"

        answers = {"confirm": True}
        result = await flow.submit_step(answers)

        # Check post call
        mock_client.post.assert_called_once_with(
            "/api/screens/next_step",
            json={
                "service_id": "service_1",
                "current_screen_id": "screen_2",
                "answers": answers
            }
        )

        # Ensure no new HTML was fetched
        mock_client.fetch_html.assert_not_called()

        # Check state changes and returned data
        self.assertTrue(flow.completed)
        self.assertIsNone(result)

    async def test_submit_step_html_fetch_fails_fallback(self):
        mock_client = AsyncMock(spec=AgentClient)

        # Mock the POST response for next_step
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "completed": False,
            "next_screen": {"id": "screen_3", "fallback_data": "yes"}
        }
        mock_client.post.return_value = mock_post_response

        # Mock the fetch_html to raise an exception
        mock_client.fetch_html.side_effect = Exception("Failed to fetch HTML")

        flow = AgentFlow(service_id="service_1", client=mock_client)
        flow.current_screen_id = "screen_2"

        answers = {"test": "val"}

        # Call should not raise the exception, it should fallback
        result = await flow.submit_step(answers)

        # Check that it fell back to returning the JSON data
        self.assertEqual(result, {"id": "screen_3", "fallback_data": "yes"})
        self.assertEqual(flow.current_screen_id, "screen_3")
