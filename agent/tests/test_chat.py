import unittest
import json
from unittest.mock import AsyncMock, MagicMock
from src.chat import ChatSession, run_chat_loop

class TestChatSession(unittest.IsolatedAsyncioTestCase):
    async def test_usage_tracking(self):
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "I am a test."
        mock_response.choices[0].message.tool_calls = None

        # Mock usage
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 150
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        mock_client.chat.completions.create.return_value = mock_response

        session = ChatSession(system_prompt="Test prompt", client=mock_client)

        # Initial usage should be 0
        self.assertEqual(session.total_tokens_used, 0)
        self.assertEqual(session.prompt_tokens_used, 0)
        self.assertEqual(session.completion_tokens_used, 0)

        await session.process_user_input("Hello")

        self.assertEqual(session.total_tokens_used, 150)
        self.assertEqual(session.prompt_tokens_used, 100)
        self.assertEqual(session.completion_tokens_used, 50)

        # A second call should accumulate
        await session.process_user_input("Hello again")

        self.assertEqual(session.total_tokens_used, 300)
        self.assertEqual(session.prompt_tokens_used, 200)
        self.assertEqual(session.completion_tokens_used, 100)

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

    async def test_process_user_input_download_and_parse_file_tool(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_789"
        tool_call.type = "function"
        tool_call.function.name = "download_and_parse_file"
        tool_call.function.arguments = json.dumps({"url": "/api/file.json"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I downloaded the file."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        mock_agent_res = MagicMock()
        mock_agent_res.status_code = 200
        mock_agent_res.headers = {"content-type": "application/json"}
        mock_agent_res.json.return_value = {"file": "content"}
        mock_agent_client.get.return_value = mock_agent_res

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Download file please")

        self.assertEqual(response, "I downloaded the file.")
        mock_agent_client.get.assert_called_once_with("/api/file.json")
        self.assertEqual(session.messages[-2]["role"], "tool")
        self.assertEqual(session.messages[-2]["content"], '{"file": "content"}')
        self.assertEqual(session.messages[-1]["role"], "assistant")

    async def test_process_user_input_abort_form_success(self):
        from unittest.mock import patch

        mock_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_abort"
        tool_call.type = "function"
        tool_call.function.name = "abort_form"
        tool_call.function.arguments = json.dumps({"reason": "User cancelled"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply after tool execution
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I have aborted the form."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)

        with patch('src.chat.asyncio.wait_for', side_effect=[mock_response_1, mock_response_2]):
            response = await session.process_user_input("Nevermind, stop.")

            self.assertEqual(response, "I have aborted the form.")
            self.assertTrue(session.form_aborted)
            self.assertEqual(session.aborted_reason, "User cancelled")

            # The tool result should have been added
            self.assertEqual(len(session.messages), 5)
            self.assertEqual(session.messages[3]["role"], "tool")
            self.assertEqual(session.messages[3]["tool_call_id"], "call_abort")

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

        # Check messages history:
        # 1. system
        # 2. user
        # 3. assistant (with tool calls)
        # 4. tool
        # 5. assistant (final response)
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_123")
        self.assertEqual(session.messages[4]["role"], "assistant")
        self.assertEqual(session.messages[4]["content"], "Form submitted successfully. Thanks!")


    async def test_process_user_input_fetch_autocomplete_options(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.text = '["option1", "option2"]'
        mock_agent_client.get.return_value = mock_http_response

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_456"
        tool_call.type = "function"
        tool_call.function.name = "fetch_autocomplete_options"
        tool_call.function.arguments = json.dumps({"data_source": "countries", "query": "Test"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply after tool execution
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I found some options."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Fetch countries")

        self.assertEqual(response, "I found some options.")
        self.assertFalse(session.form_submitted)

        mock_agent_client.get.assert_called_once_with("/api/data/countries", params={"q": "Test"})

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_456")
        self.assertEqual(session.messages[3]["content"], '["option1", "option2"]')
        self.assertEqual(session.messages[4]["role"], "assistant")
        self.assertEqual(session.messages[4]["content"], "I found some options.")

    async def test_process_user_input_get_current_datetime(self):
        mock_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_789"
        tool_call.type = "function"
        tool_call.function.name = "get_current_datetime"
        tool_call.function.arguments = "{}"
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Today is a good day."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("What day is today?")

        self.assertEqual(response, "Today is a good day.")
        self.assertFalse(session.form_submitted)

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_789")
        self.assertTrue(isinstance(session.messages[3]["content"], str))
        self.assertTrue(len(session.messages[3]["content"]) > 10)
        self.assertEqual(session.messages[4]["role"], "assistant")
        self.assertEqual(session.messages[4]["content"], "Today is a good day.")


    async def test_process_user_input_upload_file_success(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {"file_id": "test_id", "url": "/test"}
        mock_agent_client.post.return_value = mock_http_response

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_upload_123"
        tool_call.type = "function"
        tool_call.function.name = "upload_file"
        tool_call.function.arguments = json.dumps({"url": "/api/upload", "filepath": "test.txt"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "File uploaded."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        import unittest.mock
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=b"test data")) as mock_file:
            response = await session.process_user_input("Upload this file")

            self.assertEqual(response, "File uploaded.")
            self.assertFalse(session.form_submitted)

            mock_agent_client.post.assert_called_once_with("/api/upload", files={"file": mock_file.return_value})

            self.assertEqual(len(session.messages), 5)
            self.assertEqual(session.messages[3]["role"], "tool")
            self.assertEqual(session.messages[3]["tool_call_id"], "call_upload_123")
            self.assertEqual(json.loads(session.messages[3]["content"]), {"file_id": "test_id", "url": "/test"})

    async def test_process_user_input_upload_file_not_found(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_upload_456"
        tool_call.type = "function"
        tool_call.function.name = "upload_file"
        tool_call.function.arguments = json.dumps({"url": "/api/upload", "filepath": "missing.txt"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "File not found."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        import unittest.mock
        with unittest.mock.patch('builtins.open', side_effect=FileNotFoundError):
            response = await session.process_user_input("Upload missing file")

            self.assertEqual(response, "File not found.")
            self.assertFalse(session.form_submitted)
            mock_agent_client.post.assert_not_called()

            self.assertEqual(session.messages[3]["role"], "tool")
            self.assertEqual(json.loads(session.messages[3]["content"]), {"error": "File not found: missing.txt"})

    async def test_call_llm_success(self):
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = "response"

        session = ChatSession(system_prompt="Test", client=mock_client)
        res = await session._call_llm([{"role": "user", "content": "hi"}])
        self.assertEqual(res, "response")
        self.assertEqual(mock_client.chat.completions.create.call_count, 1)

    async def test_call_llm_retry_success(self):
        import asyncio
        mock_client = AsyncMock()
        # Fail first two times, succeed on the third
        mock_client.chat.completions.create.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            "success"
        ]

        session = ChatSession(system_prompt="Test", client=mock_client, max_retries=3)

        # Patch asyncio.sleep to not actually sleep
        with unittest.mock.patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            res = await session._call_llm([{"role": "user", "content": "hi"}])
            self.assertEqual(res, "success")
            self.assertEqual(mock_client.chat.completions.create.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)

    async def test_call_llm_retry_failure(self):
        import asyncio
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Fail")

        session = ChatSession(system_prompt="Test", client=mock_client, max_retries=2)

        with unittest.mock.patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with self.assertRaises(Exception) as context:
                await session._call_llm([{"role": "user", "content": "hi"}])

            self.assertEqual(str(context.exception), "Fail")
            self.assertEqual(mock_client.chat.completions.create.call_count, 2)
            self.assertEqual(mock_sleep.call_count, 1)

    async def test_call_llm_timeout(self):
        import asyncio
        mock_client = AsyncMock()

        # We don't need a custom slow_create, we can just mock wait_for
        # But wait, wait_for gets `coro`, so if we mock wait_for, `coro` is never awaited,
        # which causes the RuntimeWarning because mock_client.chat.completions.create is an AsyncMock
        # that returns a coroutine.
        # To avoid the unawaited coroutine warning, we can just use a regular MagicMock for create,
        # or we can await the coroutine in our mocked wait_for.

        async def mock_wait_for(coro, timeout):
            # Await it and just ignore the result, then raise TimeoutError
            try:
                await coro
            except Exception:
                pass
            raise asyncio.TimeoutError()

        session = ChatSession(system_prompt="Test", client=mock_client, max_retries=1)

        with unittest.mock.patch('asyncio.wait_for', side_effect=mock_wait_for):
            with self.assertRaises(asyncio.TimeoutError):
                await session._call_llm([{"role": "user", "content": "hi"}])

class TestChatLoop(unittest.IsolatedAsyncioTestCase):
    async def test_run_chat_loop_exit(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False

        input_func = AsyncMock(side_effect=["exit"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Agent initialized. What would you like to do?")
        output_func.assert_any_call("Exiting chat.")
        self.assertFalse(session.process_user_input.called)

    async def test_run_chat_loop_submit(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False

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

    async def test_process_user_input_exception_handling(self):
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("LLM API is down")

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("Hello")

        self.assertEqual(response, "I encountered an error processing your request.")
        self.assertFalse(session.form_submitted)

class TestChatSessionPersistence(unittest.TestCase):
    def test_save_and_load_state(self):
        import tempfile
        import os

        # Initialize and modify state

        mock_client = AsyncMock()
        session = ChatSession(system_prompt="You are a helpful assistant.", client=mock_client, model="test-model", max_retries=5, timeout=42.0)

        session.messages.append({"role": "user", "content": "Hello"})
        session.form_submitted = True
        session.submitted_data = {"key": "value"}
        session.form_aborted = True
        session.aborted_reason = "Test reason"
        session.total_tokens_used = 100
        session.prompt_tokens_used = 60
        session.completion_tokens_used = 40

        # Save state to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name

        try:
            session.save_state(tmp_path)

            # Load state into new instance
            loaded_session = ChatSession.load_state(tmp_path, client=mock_client)

            # Assert properties match
            self.assertEqual(loaded_session.model, "test-model")
            self.assertEqual(loaded_session.max_retries, 5)
            self.assertEqual(loaded_session.timeout, 42.0)
            self.assertEqual(len(loaded_session.messages), 2)
            self.assertEqual(loaded_session.messages[0]["content"], "You are a helpful assistant.")
            self.assertEqual(loaded_session.messages[1]["content"], "Hello")
            self.assertTrue(loaded_session.form_submitted)
            self.assertEqual(loaded_session.submitted_data, {"key": "value"})
            self.assertTrue(loaded_session.form_aborted)
            self.assertEqual(loaded_session.aborted_reason, "Test reason")
            self.assertEqual(loaded_session.total_tokens_used, 100)
            self.assertEqual(loaded_session.prompt_tokens_used, 60)
            self.assertEqual(loaded_session.completion_tokens_used, 40)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
