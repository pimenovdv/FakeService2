import unittest
import json
from unittest.mock import AsyncMock, MagicMock
from src.chat import ChatSession, run_chat_loop

class TestChatSession(unittest.IsolatedAsyncioTestCase):
    async def test_process_user_input_normal_response(self):
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "What is your name?"
        mock_response.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.return_value = mock_response

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("Hello")

        self.assertEqual(response, "What is your name?")
        self.assertEqual(len(session.messages), 3) # system, user, assistant
        self.assertEqual(session.messages[-1]["content"], "What is your name?")
        self.assertFalse(session.form_submitted)

    async def test_process_user_input_tool_call(self):
        mock_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_123"
        tool_call.type = "function"
        tool_call.function.name = "submit_form"
        tool_call.function.arguments = json.dumps({"answers": {"name": "John Doe"}})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply after tool execution
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Form submitted successfully. Thanks!"
        mock_response_2.choices[0].message.tool_calls = None

        # Setup side_effect to return these sequentially
        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("My name is John Doe, please submit.")

        self.assertEqual(response, "Form submitted successfully. Thanks!")
        self.assertTrue(session.form_submitted)
        self.assertEqual(session.submitted_data, {"name": "John Doe"})

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_123")
        self.assertEqual(session.messages[4]["role"], "assistant")
        self.assertEqual(session.messages[4]["content"], "Form submitted successfully. Thanks!")

    async def test_process_user_input_multiple_tool_calls(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        # Setup mock for fetch_autocomplete_options via agent_client
        mock_response_http = MagicMock()
        mock_response_http.json.return_value = [{"id": "RU", "name": "Russia"}]
        mock_agent_client.get.return_value = mock_response_http

        # First response: LLM decides to fetch autocomplete options
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call_1 = MagicMock()
        tool_call_1.id = "call_auto"
        tool_call_1.type = "function"
        tool_call_1.function.name = "fetch_autocomplete_options"
        tool_call_1.function.arguments = json.dumps({"endpoint": "/api/countries", "query": "Rus"})
        mock_response_1.choices[0].message.tool_calls = [tool_call_1]

        # Second response: LLM receives autocomplete data, decides to submit
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = None

        tool_call_2 = MagicMock()
        tool_call_2.id = "call_submit"
        tool_call_2.type = "function"
        tool_call_2.function.name = "submit_form"
        tool_call_2.function.arguments = json.dumps({"answers": {"country": "RU"}})
        mock_response_2.choices[0].message.tool_calls = [tool_call_2]

        # Third response: LLM says thanks
        mock_response_3 = MagicMock()
        mock_response_3.choices = [MagicMock()]
        mock_response_3.choices[0].message.content = "All done!"
        mock_response_3.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2, mock_response_3]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("My country is Rus, please submit.")

        self.assertEqual(response, "All done!")
        self.assertTrue(session.form_submitted)
        self.assertEqual(session.submitted_data, {"country": "RU"})

        self.assertEqual(len(session.messages), 7)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_auto")
        self.assertIn("Russia", session.messages[3]["content"])

        self.assertEqual(session.messages[5]["role"], "tool")
        self.assertEqual(session.messages[5]["tool_call_id"], "call_submit")

class TestChatLoop(unittest.IsolatedAsyncioTestCase):
    async def test_run_chat_loop_exit(self):
        session = MagicMock()
        session.form_submitted = False

        input_func = AsyncMock(side_effect=["exit"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Agent initialized. What would you like to do?")
        output_func.assert_any_call("Exiting chat.")
        self.assertFalse(session.process_user_input.called)

    async def test_run_chat_loop_submit(self):
        session = MagicMock()
        session.form_submitted = False

        async def mock_process(text):
            if text == "submit":
                session.form_submitted = True
                session.submitted_data = {"test": "data"}
                return "Done"
            return "Ok"

        session.process_user_input = AsyncMock(side_effect=mock_process)

        input_func = AsyncMock(side_effect=["hello", "submit"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Agent initialized. What would you like to do?")
        output_func.assert_any_call("Ok")
        output_func.assert_any_call("Done")
        output_func.assert_any_call("Form submission complete with data: {'test': 'data'}")
