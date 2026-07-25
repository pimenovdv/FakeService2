import unittest
import json
from unittest.mock import AsyncMock, MagicMock
from src.chat import ChatSession, run_chat_loop

class TestChatSession(unittest.IsolatedAsyncioTestCase):
    async def test_get_weather(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "city": "London",
                "temperature": 15.0,
                "condition": "Rainy",
                "humidity": 80,
                "wind_speed": 12.5
            }
        )

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_weather_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_weather"
        mock_tool_call.function.arguments = json.dumps({"city": "London"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The weather in London is Rainy and 15.0°C."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession("System Prompt", client=mock_client, agent_client=mock_agent_client)

        response = await session.process_user_input("What is the weather in London?")

        self.assertEqual(response, "The weather in London is Rainy and 15.0°C.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        mock_agent_client.get.assert_called_once_with("/api/weather?city=London")

        # Check tool execution
        tool_msg = next((m for m in session.messages if m.get("role") == "tool"), None)
        self.assertIsNotNone(tool_msg)
        tool_content = json.loads(tool_msg["content"])
        self.assertEqual(tool_content["city"], "London")
        self.assertEqual(tool_content["temperature"], 15.0)
        self.assertEqual(tool_content["condition"], "Rainy")

    async def test_get_current_datetime(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_datetime_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_current_datetime"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The current datetime is 2024-01-01T12:00:00."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client)
        result = await session.process_user_input("What time is it?")

        self.assertEqual(result, "The current datetime is 2024-01-01T12:00:00.")
        self.assertEqual(len(session.messages), 5)

        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertEqual(tool_msg["tool_call_id"], "call_datetime_123")
        tool_content = json.loads(tool_msg["content"])
        self.assertIn("current_datetime", tool_content)

    async def test_generate_uuid(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_uuid_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "generate_uuid"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Here is a uuid: 1234."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client)
        result = await session.process_user_input("Generate a uuid")

        self.assertEqual(result, "Here is a uuid: 1234.")
        self.assertEqual(len(session.messages), 5)

        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertEqual(tool_msg["tool_call_id"], "call_uuid_123")
        tool_content = json.loads(tool_msg["content"])
        self.assertIn("uuid", tool_content)

    async def test_get_exchange_rate(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_exchange_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_exchange_rate"
        mock_tool_call.function.arguments = json.dumps({"base_currency": "USD", "target_currency": "EUR"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The exchange rate for USD to EUR is 0.85."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession("System Prompt", client=mock_client)

        response = await session.process_user_input("What is the exchange rate from USD to EUR?")

        self.assertEqual(response, "The exchange rate for USD to EUR is 0.85.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

        # Check tool execution
        tool_msg = next((m for m in session.messages if m.get("role") == "tool"), None)
        self.assertIsNotNone(tool_msg)
        tool_content = json.loads(tool_msg["content"])
        self.assertEqual(tool_content["base_currency"], "USD")
        self.assertEqual(tool_content["target_currency"], "EUR")
        self.assertIn("exchange_rate", tool_content)

    async def test_translate_text(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_translate_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "translate_text"
        mock_tool_call.function.arguments = json.dumps({"text": "Hello", "source_language": "en", "target_language": "es"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Hola"
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession("System Prompt", client=mock_client)

        response = await session.process_user_input("Translate 'Hello' to Spanish.")

        self.assertEqual(response, "Hola")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

        # Check tool execution
        tool_msg = next((m for m in session.messages if m.get("role") == "tool" and m.get("tool_call_id") == "call_translate_123"), None)
        self.assertIsNotNone(tool_msg)
        tool_content = json.loads(tool_msg["content"])
        self.assertEqual(tool_content["text"], "Hello")
        self.assertEqual(tool_content["source_language"], "en")
        self.assertEqual(tool_content["target_language"], "es")
        self.assertIn("translated_text", tool_content)

    async def test_calculate_distance(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_distance_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "calculate_distance"
        mock_tool_call.function.arguments = json.dumps({"origin": "New York", "destination": "London"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The distance is roughly 5500 km."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession("System Prompt", client=mock_client)

        response = await session.process_user_input("What is the distance between New York and London?")

        self.assertEqual(response, "The distance is roughly 5500 km.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

        # Check tool execution
        tool_msg = next((m for m in session.messages if m.get("role") == "tool" and m.get("tool_call_id") == "call_distance_123"), None)
        self.assertIsNotNone(tool_msg)
        tool_content = json.loads(tool_msg["content"])
        self.assertEqual(tool_content["origin"], "New York")
        self.assertEqual(tool_content["destination"], "London")
        self.assertIn("distance", tool_content)
        self.assertIn("unit", tool_content)

    async def test_get_system_health(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_health_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_system_health"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "System health retrieved."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        mock_api_res = MagicMock()
        mock_api_res.status_code = 200
        mock_api_res.json.return_value = {"status": "healthy"}
        mock_agent_client.get.return_value = mock_api_res

        session = ChatSession("System Prompt", client=mock_client, agent_client=mock_agent_client)

        response = await session.process_user_input("What is the system health?")

        self.assertEqual(response, "System health retrieved.")

        # Verify tool messages
        tool_msg = next((msg for msg in session.messages if msg.get("role") == "tool" and msg.get("tool_call_id") == "call_health_123"), None)
        self.assertIsNotNone(tool_msg)
        self.assertEqual(json.loads(tool_msg["content"]), {"status": "healthy"})


    async def test_retrieve_available_services(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_svc_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "retrieve_available_services"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Available services retrieved."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        mock_api_res = MagicMock()
        mock_api_res.status_code = 200
        mock_api_res.json.return_value = ["service_1", "service_2"]
        mock_agent_client.get.return_value = mock_api_res

        session = ChatSession("System Prompt", client=mock_client, agent_client=mock_agent_client)
        result = await session.process_user_input("What services are available?")

        self.assertEqual(result, "Available services retrieved.")
        mock_agent_client.get.assert_called_with("/api/screens/available_services")

        # Check that the tool result was added to the messages
        tool_msg = next((msg for msg in session.messages if msg.get("role") == "tool" and msg.get("tool_call_id") == "call_svc_123"), None)
        self.assertIsNotNone(tool_msg)
        self.assertIn("service_1", tool_msg["content"])
        self.assertIn("service_2", tool_msg["content"])

    async def test_generate_mock_data(self):
        mock_client = AsyncMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_mock_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "generate_mock_data"
        mock_tool_call.function.arguments = json.dumps({
            "fields": [
                {"id": "field_email", "type": "email", "name": "email", "label": "Email Address"},
                {"id": "field_phone", "type": "text", "name": "phone_num", "label": "Phone Number"},
                {"id": "field_name", "type": "text", "name": "first_name", "label": "First Name"},
                {"id": "field_age", "type": "number", "name": "age", "label": "Age"},
                {"id": "field_unknown", "type": "text", "name": "custom", "label": "Custom"}
            ]
        })

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Mock data generated."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("Generate some mock data for me.")

        self.assertEqual(response, "Mock data generated.")

        # Verify tool messages
        tool_msg = next((msg for msg in session.messages if msg.get("role") == "tool" and msg.get("tool_call_id") == "call_mock_123"), None)
        self.assertIsNotNone(tool_msg)

        tool_content = json.loads(tool_msg["content"])
        self.assertIn("mock_data", tool_content)
        mock_data = tool_content["mock_data"]

        self.assertIn("field_email", mock_data)
        self.assertIn("@example.com", mock_data["field_email"])
        self.assertIn("field_phone", mock_data)
        self.assertTrue(mock_data["field_phone"].startswith("555-01"))
        self.assertIn("field_name", mock_data)
        self.assertEqual(mock_data["field_name"], "Mock Name")
        self.assertIn("field_age", mock_data)
        # Should be a numeric string
        self.assertTrue(mock_data["field_age"].isdigit())
        self.assertIn("field_unknown", mock_data)
        self.assertTrue(mock_data["field_unknown"].startswith("Mock Value "))

    async def test_update_user_preferences(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_pref_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "update_user_preferences"
        mock_tool_call.function.arguments = json.dumps({"preferences": {"language": "Spanish", "tone": "friendly"}})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Preferences updated successfully."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)

        response = await session.process_user_input("Speak to me in Spanish and be friendly.")

        self.assertEqual(response, "Preferences updated successfully.")
        self.assertEqual(session.user_preferences, {"language": "Spanish", "tone": "friendly"})

        tool_msg = session.messages[-2]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertEqual(tool_msg["name"], "update_user_preferences")
        content = json.loads(tool_msg["content"])
        self.assertEqual(content["status"], "success")
        self.assertEqual(content["user_preferences"], {"language": "Spanish", "tone": "friendly"})

    async def test_get_session_stats(self):
        mock_client = AsyncMock()

        # First response: call get_session_stats tool
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_stats_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_session_stats"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"
        mock_response_1.usage.prompt_tokens = 50
        mock_response_1.usage.completion_tokens = 10
        mock_response_1.usage.total_tokens = 60

        # Second response: final assistant reply after stats
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Here are your stats."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None
        mock_response_2.usage.prompt_tokens = 100
        mock_response_2.usage.completion_tokens = 20
        mock_response_2.usage.total_tokens = 120

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        session.prompt_tokens_used = 10
        session.completion_tokens_used = 5
        session.total_tokens_used = 15

        response = await session.process_user_input("What are my stats?")

        self.assertEqual(response, "Here are your stats.")
        self.assertEqual(session.prompt_tokens_used, 160)
        self.assertEqual(session.completion_tokens_used, 35)
        self.assertEqual(session.total_tokens_used, 195)

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[0]["role"], "system")
        self.assertEqual(session.messages[1]["role"], "user")
        self.assertEqual(session.messages[2]["role"], "assistant")
        self.assertEqual(session.messages[3]["role"], "tool")

        tool_content = json.loads(session.messages[3]["content"])
        self.assertEqual(tool_content["prompt_tokens_used"], 60) # 10 + 50
        self.assertEqual(tool_content["completion_tokens_used"], 15) # 5 + 10
        self.assertEqual(tool_content["total_tokens_used"], 75) # 15 + 60
        self.assertEqual(tool_content["message_count"], 3) # system, user, assistant(tool call), tool (itself not appended yet when len calculated)

        self.assertEqual(session.messages[4]["role"], "assistant")


    async def test_reset_session(self):
        mock_client = AsyncMock()

        # First response: call reset_session tool
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "reset_session"
        mock_tool_call.function.arguments = "{}"

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        # Second response: final assistant reply after reset
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Session has been reset."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None # to prevent json serialization error in _call_llm

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        session.messages.append({"role": "user", "content": "Some old history"})
        session.form_aborted = True
        session.aborted_reason = "Something failed"
        session.session_paused = True

        response = await session.process_user_input("Reset my session")

        self.assertEqual(response, "Session has been reset.")
        self.assertFalse(session.form_aborted)
        self.assertIsNone(session.aborted_reason)
        self.assertFalse(session.session_paused)

        # messages should be system prompt + assistant tool call + reset tool result + final assistant reply
        self.assertEqual(len(session.messages), 4)
        self.assertEqual(session.messages[0]["role"], "system")
        self.assertEqual(session.messages[1]["role"], "assistant")
        self.assertEqual(session.messages[2]["role"], "tool")
        self.assertEqual(session.messages[3]["role"], "assistant")

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

    async def test_process_user_input_request_human_handoff(self):
        from unittest.mock import patch

        mock_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_handoff"
        tool_call.type = "function"
        tool_call.function.name = "request_human_handoff"
        tool_call.function.arguments = json.dumps({"summary": "User needs complex support."})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply after tool execution
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I have requested a human operator to assist you."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("I want to speak to a human.")

        self.assertEqual(response, "I have requested a human operator to assist you.")
        self.assertTrue(session.handoff_requested)
        self.assertEqual(session.handoff_summary, "User needs complex support.")
        self.assertEqual(session.messages[-2]["role"], "tool")
        self.assertIn("Handoff to human requested successfully", session.messages[-2]["content"])

    async def test_process_user_input_export_chat_history_success(self):
        import tempfile
        import os
        import json

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = None
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "export_chat_history"
        mock_tool_call.function.arguments = json.dumps({"filepath": "/tmp/dummy"})

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            filepath = tmp_file.name

        try:
            mock_tool_call.function.arguments = json.dumps({"filepath": filepath})
            mock_message.tool_calls = [mock_tool_call]
            mock_response.choices = [MagicMock(message=mock_message)]

            mock_second_response = MagicMock()

            mock_second_message = MagicMock()
            mock_second_message.content = "History exported."
            mock_second_message.tool_calls = None
            mock_second_response.choices = [MagicMock(message=mock_second_message)]

            mock_client.chat.completions.create.side_effect = [mock_response, mock_second_response]

            session = ChatSession(system_prompt="Test prompt", client=mock_client)
            session.messages = [{"role": "system", "content": "Test prompt"}] # ensure predictability

            response = await session.process_user_input("export history")

            self.assertEqual(response, "History exported.")

            # verify file contents
            with open(filepath, "r") as f:
                saved_history = json.load(f)

            self.assertTrue(len(saved_history) > 0)
            self.assertEqual(saved_history[0]["role"], "system")
            self.assertEqual(saved_history[0]["content"], "Test prompt")

            # verify tool output
            self.assertEqual(session.messages[-2]["role"], "tool")
            self.assertIn("success", session.messages[-2]["content"])
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    async def test_process_user_input_pause_session_success(self):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = None
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_pause"
        mock_tool_call.function.name = "pause_session"
        mock_tool_call.function.arguments = '{"reason": "Need to wait for an email"}'
        mock_message.tool_calls = [mock_tool_call]
        mock_response.choices = [MagicMock(message=mock_message)]

        mock_second_response = MagicMock()
        mock_second_message = MagicMock()
        mock_second_message.content = "Session paused. I will wait."
        mock_second_message.tool_calls = None
        mock_second_response.choices = [MagicMock(message=mock_second_message)]

        mock_client.chat.completions.create.side_effect = [mock_response, mock_second_response]

        session = ChatSession(system_prompt="Test", client=mock_client)
        response = await session.process_user_input("Pause the session please.")

        self.assertTrue(session.session_paused)
        self.assertEqual(session.paused_reason, "Need to wait for an email")
        self.assertEqual(response, "Session paused. I will wait.")
        self.assertEqual(len(session.messages), 5) # system, user, assistant(tool), tool result, final answer

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



    async def test_process_user_input_search_system(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = [{"id": 1, "title": "John Doe", "description": "Engineer", "type": "user"}]
        mock_agent_client.get.return_value = mock_http_response

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_search_123"
        tool_call.type = "function"
        tool_call.function.name = "search_system"
        tool_call.function.arguments = json.dumps({"query": "John"})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Found John Doe."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        response = await session.process_user_input("Search for John")

        self.assertEqual(response, "Found John Doe.")

        mock_agent_client.get.assert_called_once_with("/api/search?q=John")

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_search_123")
        self.assertEqual(json.loads(session.messages[3]["content"]), [{"id": 1, "title": "John Doe", "description": "Engineer", "type": "user"}])
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

    async def test_evaluate_js(self):
        mock_client = AsyncMock()

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_js_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "evaluate_js"
        mock_tool_call.function.arguments = json.dumps({"script_content": "a + b;", "context": {"a": 1, "b": 2}})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "JS evaluated successfully."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client)
        response = await session.process_user_input("evaluate this script")

        self.assertEqual(response, "JS evaluated successfully.")
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["name"], "evaluate_js")
        tool_content = json.loads(session.messages[3]["content"])
        self.assertEqual(tool_content["result"], 3)
        self.assertEqual(tool_content["evaluated_script"], "a + b;")

    async def test_process_user_input_upload_file_size_validation_fails(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_upload_789"
        tool_call.type = "function"
        tool_call.function.name = "upload_file"
        tool_call.function.arguments = json.dumps({"url": "/api/upload", "filepath": "toolarge.txt", "max_size": 100})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "File too large."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        import unittest.mock
        with unittest.mock.patch('os.path.exists', return_value=True), \
             unittest.mock.patch('os.path.getsize', return_value=150):
            response = await session.process_user_input("Upload large file")

            self.assertEqual(response, "File too large.")
            self.assertFalse(session.form_submitted)
            mock_agent_client.post.assert_not_called()

            self.assertEqual(session.messages[3]["role"], "tool")
            self.assertEqual(json.loads(session.messages[3]["content"]), {"error": "File exceeds maximum size of 100 bytes"})

    async def test_process_user_input_upload_file_type_validation_fails(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()

        # First response is a tool call
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None

        tool_call = MagicMock()
        tool_call.id = "call_upload_abc"
        tool_call.type = "function"
        tool_call.function.name = "upload_file"
        tool_call.function.arguments = json.dumps({"url": "/api/upload", "filepath": "badtype.exe", "allowed_types": ["image/png", "application/pdf"]})
        mock_response_1.choices[0].message.tool_calls = [tool_call]

        # Second response is the final conversational reply
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "File type not allowed."
        mock_response_2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        import unittest.mock
        with unittest.mock.patch('os.path.exists', return_value=True), \
             unittest.mock.patch('mimetypes.guess_type', return_value=("application/x-msdownload", None)):
            response = await session.process_user_input("Upload bad type file")

            self.assertEqual(response, "File type not allowed.")
            self.assertFalse(session.form_submitted)
            mock_agent_client.post.assert_not_called()

            self.assertEqual(session.messages[3]["role"], "tool")
            self.assertEqual(json.loads(session.messages[3]["content"]), {"error": "File type application/x-msdownload not allowed"})

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

    async def test_process_user_input_multi_turn_tool_calling(self):
        import json
        mock_client = AsyncMock()

        # Turn 1: user asks a question, LLM responds with tool call 1 (translate)
        mock_response_1 = MagicMock()
        mock_msg_1 = MagicMock()
        mock_msg_1.content = None
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "translate_text"
        mock_tool_call_1.function.arguments = json.dumps({
            "text": "Hello",
            "source_language": "en",
            "target_language": "es"
        })
        mock_msg_1.tool_calls = [mock_tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_msg_1)]

        # Turn 2: LLM responds with tool call 2 (get_weather)
        mock_response_2 = MagicMock()
        mock_msg_2 = MagicMock()
        mock_msg_2.content = None
        mock_tool_call_2 = MagicMock()
        mock_tool_call_2.id = "call_2"
        mock_tool_call_2.type = "function"
        mock_tool_call_2.function.name = "get_weather"
        mock_tool_call_2.function.arguments = json.dumps({
            "city": "Madrid"
        })
        mock_msg_2.tool_calls = [mock_tool_call_2]
        mock_response_2.choices = [MagicMock(message=mock_msg_2)]

        # Turn 3: LLM responds with final message
        mock_response_3 = MagicMock()
        mock_msg_3 = MagicMock()
        mock_msg_3.content = "Hola! The weather in Madrid is Sunny."
        mock_msg_3.tool_calls = None
        mock_response_3.choices = [MagicMock(message=mock_msg_3)]

        mock_client.chat.completions.create.side_effect = [
            mock_response_1,
            mock_response_2,
            mock_response_3
        ]

        session = ChatSession(system_prompt="Test", client=mock_client)
        response = await session.process_user_input("Translate Hello to Spanish and get weather in Madrid")

        self.assertEqual(response, "Hola! The weather in Madrid is Sunny.")
        # messages: system, user, assistant(call1), tool1, assistant(call2), tool2, assistant(final)
        self.assertEqual(len(session.messages), 7)
        self.assertEqual(session.messages[1]["role"], "user")
        self.assertEqual(session.messages[2]["role"], "assistant")
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[4]["role"], "assistant")
        self.assertEqual(session.messages[5]["role"], "tool")
        self.assertEqual(session.messages[6]["role"], "assistant")
        self.assertEqual(session.messages[6]["content"], "Hola! The weather in Madrid is Sunny.")



    async def test_validate_form(self):
        mock_client = MagicMock()
        mock_agent_client = MagicMock()

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_validate"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "validate_form"
        mock_tool_call.function.arguments = '{"answers": {"name": "Jo", "age": "17"}, "fields": [{"id": "name", "attributes": {"required": true, "minlength": 3}}, {"id": "age", "attributes": {"min": 18}}]}'

        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]

        mock_message2 = MagicMock()
        mock_message2.content = "Validation complete"
        mock_message2.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message1)]),
            MagicMock(choices=[MagicMock(message=mock_message2)])
        ])

        response = await session.process_user_input("Validate my form")
        self.assertEqual(response, "Validation complete")

        # System prompt + user + assistant (tool call) + tool (result) + assistant (final)
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")

        result_json = session.messages[3]["content"]
        import json
        result = json.loads(result_json)

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 2)

        errors = {e["field"]: e["error"] for e in result["errors"]}
        self.assertTrue(errors["name"].startswith("minlength"))
        self.assertTrue(errors["age"].startswith("min"))

    async def test_validate_form_cross_validations(self):
        mock_client = MagicMock()
        mock_agent_client = MagicMock()

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_validate"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "validate_form"
        mock_tool_call.function.arguments = '{"answers": {"password": "abc", "confirm_password": "def", "has_pet": "yes", "pet_name": ""}, "fields": [], "cross_validations": [{"type": "match", "fields": ["password", "confirm_password"], "message": "Passwords do not match"}, {"type": "required_if", "condition_field": "has_pet", "condition_value": "yes", "target_field": "pet_name", "message": "Pet name is required"}]}'

        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]

        mock_message2 = MagicMock()
        mock_message2.content = "Validation complete"
        mock_message2.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message1)]),
            MagicMock(choices=[MagicMock(message=mock_message2)])
        ])

        response = await session.process_user_input("Validate my form")
        self.assertEqual(response, "Validation complete")

        result_json = session.messages[3]["content"]
        import json
        result = json.loads(result_json)

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 2)

        errors = [e.get("error") for e in result["errors"]]
        self.assertIn("Passwords do not match", errors)
        self.assertIn("Pet name is required", errors)

    async def test_validate_form_cross_validations_valid(self):
        mock_client = MagicMock()
        mock_agent_client = MagicMock()

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_validate"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "validate_form"
        mock_tool_call.function.arguments = '{"answers": {"password": "abc", "confirm_password": "abc", "has_pet": "yes", "pet_name": "Fido"}, "fields": [], "cross_validations": [{"type": "match", "fields": ["password", "confirm_password"], "message": "Passwords do not match"}, {"type": "required_if", "condition_field": "has_pet", "condition_value": "yes", "target_field": "pet_name", "message": "Pet name is required"}]}'

        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]

        mock_message2 = MagicMock()
        mock_message2.content = "Validation complete"
        mock_message2.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message1)]),
            MagicMock(choices=[MagicMock(message=mock_message2)])
        ])

        response = await session.process_user_input("Validate my form")
        self.assertEqual(response, "Validation complete")

        result_json = session.messages[3]["content"]
        import json
        result = json.loads(result_json)

        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)


class TestChatLoop(unittest.IsolatedAsyncioTestCase):
    async def test_run_chat_loop_exit(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False
        session.handoff_requested = False
        session.session_paused = False

        input_func = AsyncMock(side_effect=["exit"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Agent initialized. What would you like to do?")
        output_func.assert_any_call("Exiting chat.")
        self.assertFalse(session.process_user_input.called)

    async def test_run_chat_loop_pause(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False
        session.handoff_requested = False
        session.session_paused = False

        async def mock_process(text):
            if text == "pause":
                session.session_paused = True
                session.paused_reason = "User needs a break."
                return "Session paused."
            return "Ok"

        session.process_user_input = AsyncMock(side_effect=mock_process)

        input_func = AsyncMock(side_effect=["pause"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Session paused.")
        output_func.assert_any_call("Session paused. Reason: User needs a break.")

    async def test_run_chat_loop_handoff(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False
        session.handoff_requested = False
        session.session_paused = False

        async def mock_process(text):
            if text == "handoff":
                session.handoff_requested = True
                session.handoff_summary = "Help needed."
                return "Handoff requested."
            return "Ok"

        session.process_user_input = AsyncMock(side_effect=mock_process)

        input_func = AsyncMock(side_effect=["handoff"])
        output_func = AsyncMock()

        await run_chat_loop(session, input_func, output_func)

        output_func.assert_any_call("Handoff requested.")
        output_func.assert_any_call("Handoff to human requested. Summary: Help needed.")

    async def test_run_chat_loop_submit(self):
        session = MagicMock()
        session.form_submitted = False
        session.form_aborted = False
        session.handoff_requested = False
        session.session_paused = False

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

    async def test_get_audit_logs(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"items": [{"id": "1", "action": "login"}], "total": 1, "skip": 0, "limit": 10}
        mock_agent_client.get.return_value = mock_response_get

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_audit_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_audit_logs"
        mock_tool_call.function.arguments = json.dumps({"skip": 0, "limit": 10, "user_id": "user1", "action": "login"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "Here are the logs."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Get audit logs.")

        self.assertEqual(response, "Here are the logs.")
        mock_agent_client.get.assert_called_with("/api/audit-logs?skip=0&limit=10&user_id=user1&action=login")
        self.assertEqual(len(session.messages), 5)
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("login", tool_msg["content"])

    async def test_get_analytics_data(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"metric": "revenue", "data": [{"timestamp": "2023-01-01", "value": 100.0}]}
        mock_agent_client.get.return_value = mock_response_get

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_analytics_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_analytics_data"
        mock_tool_call.function.arguments = json.dumps({"start_date": "2023-01-01", "end_date": "2023-01-10", "metric": "revenue"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The analytics data."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Get analytics data.")

        self.assertEqual(response, "The analytics data.")
        mock_agent_client.get.assert_called_with("/api/analytics?start_date=2023-01-01&end_date=2023-01-10&metric=revenue")
        self.assertEqual(len(session.messages), 5) # System, User, Assistant(tool), Tool, Assistant
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("revenue", tool_msg["content"])

    async def test_get_webhook(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"webhook_id": "test_id", "payloads": [{"event": "test"}]}
        mock_agent_client.get.return_value = mock_response_get

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_webhook_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "get_webhook"
        mock_tool_call.function.arguments = json.dumps({"webhook_id": "test_id"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response_1.choices[0].message.role = "assistant"

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "The webhook data."
        mock_response_2.choices[0].message.tool_calls = None
        mock_response_2.choices[0].message.role = "assistant"
        mock_response_2.choices[0].message.type = None

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Get webhook data.")

        self.assertEqual(response, "The webhook data.")
        mock_agent_client.get.assert_called_with("/api/webhooks/test_id")
        self.assertEqual(len(session.messages), 5) # System, User, Assistant(tool), Tool, Assistant
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("test_id", tool_msg["content"])

    async def test_manage_settings_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"theme": "light", "notifications_enabled": True}
        mock_agent_client.get.return_value = mock_response_get

        # Mock LLM calls:
        mock_response_1 = MagicMock()
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "manage_settings"
        mock_tool_call_1.function.arguments = json.dumps({"action": "get"})
        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_message_1)]

        mock_response_2 = MagicMock()
        mock_message_2 = MagicMock()
        mock_message_2.role = "assistant"
        mock_message_2.content = "Settings fetched."
        mock_message_2.tool_calls = None
        mock_response_2.choices = [MagicMock(message=mock_message_2)]

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Get settings")

        self.assertEqual(response, "Settings fetched.")
        mock_agent_client.get.assert_called_with("/api/settings")

        self.assertEqual(len(session.messages), 5)
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("light", tool_msg["content"])

    async def test_manage_profile_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"id": "123", "username": "mockuser", "email": "mockuser@example.com"}
        mock_agent_client.get.return_value = mock_response_get

        mock_response_1 = MagicMock()
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_profile_1"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "manage_profile"
        mock_tool_call_1.function.arguments = json.dumps({"action": "get"})
        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_message_1)]

        mock_response_2 = MagicMock()
        mock_message_2 = MagicMock()
        mock_message_2.role = "assistant"
        mock_message_2.content = "Here is the profile."
        mock_message_2.tool_calls = None
        mock_response_2.choices = [MagicMock(message=mock_message_2)]

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Get my profile")

        self.assertEqual(response, "Here is the profile.")
        mock_agent_client.get.assert_called_with("/api/profile")

        self.assertEqual(len(session.messages), 5)
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("mockuser", tool_msg["content"])

    async def test_manage_profile_put(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.put = AsyncMock()

        mock_response_put = MagicMock()
        mock_response_put.status_code = 200
        mock_response_put.json.return_value = {"id": "123", "username": "newname", "email": "mockuser@example.com"}
        mock_agent_client.put.return_value = mock_response_put

        mock_response_1 = MagicMock()
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_profile_2"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "manage_profile"
        mock_tool_call_1.function.arguments = json.dumps({"action": "put", "profile": {"username": "newname"}})
        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_message_1)]

        mock_response_2 = MagicMock()
        mock_message_2 = MagicMock()
        mock_message_2.role = "assistant"
        mock_message_2.content = "Profile updated."
        mock_message_2.tool_calls = None
        mock_response_2.choices = [MagicMock(message=mock_message_2)]

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Update my username to newname")

        self.assertEqual(response, "Profile updated.")
        mock_agent_client.put.assert_called_with("/api/profile", json={"username": "newname"})

        self.assertEqual(len(session.messages), 5)
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("newname", tool_msg["content"])

    async def test_manage_settings_put(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.put = AsyncMock()

        mock_response_put = MagicMock()
        mock_response_put.status_code = 200
        mock_response_put.json.return_value = {"theme": "dark", "notifications_enabled": False}
        mock_agent_client.put.return_value = mock_response_put

        # Mock LLM calls:
        mock_response_1 = MagicMock()
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_2"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "manage_settings"
        mock_tool_call_1.function.arguments = json.dumps({"action": "put", "settings": {"theme": "dark", "notifications_enabled": False}})
        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_message_1)]

        mock_response_2 = MagicMock()
        mock_message_2 = MagicMock()
        mock_message_2.role = "assistant"
        mock_message_2.content = "Settings updated."
        mock_message_2.tool_calls = None
        mock_response_2.choices = [MagicMock(message=mock_message_2)]

        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)
        response = await session.process_user_input("Update settings")

        self.assertEqual(response, "Settings updated.")
        mock_agent_client.put.assert_called_with("/api/settings", json={"theme": "dark", "notifications_enabled": False})

        self.assertEqual(len(session.messages), 5)
        tool_msg = session.messages[3]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertIn("dark", tool_msg["content"])

    async def test_cache_interaction(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get = AsyncMock()
        mock_agent_client.post = AsyncMock()
        mock_agent_client.delete = AsyncMock()

        # Mock GET response
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {"key": "test_key", "value": "test_val"}
        mock_agent_client.get.return_value = mock_response_get

        # Mock POST response
        mock_response_post = MagicMock()
        mock_response_post.status_code = 200
        mock_response_post.json.return_value = {"status": "success", "message": "Key 'test_key' set.", "ttl": 60}
        mock_agent_client.post.return_value = mock_response_post

        # Mock DELETE response
        mock_response_delete = MagicMock()
        mock_response_delete.status_code = 200
        mock_response_delete.json.return_value = {"status": "success", "message": "Key 'test_key' deleted."}
        mock_agent_client.delete.return_value = mock_response_delete

        # Setup tool call for 'set'
        mock_tool_call_set = MagicMock()
        mock_tool_call_set.id = "call_cache_set"
        mock_tool_call_set.type = "function"
        mock_tool_call_set.function.name = "cache_interaction"
        mock_tool_call_set.function.arguments = json.dumps({"action": "set", "key": "test_key", "value": "test_val", "ttl": 60})

        # Setup tool call for 'get'
        mock_tool_call_get = MagicMock()
        mock_tool_call_get.id = "call_cache_get"
        mock_tool_call_get.type = "function"
        mock_tool_call_get.function.name = "cache_interaction"
        mock_tool_call_get.function.arguments = json.dumps({"action": "get", "key": "test_key"})

        # Setup tool call for 'delete'
        mock_tool_call_delete = MagicMock()
        mock_tool_call_delete.id = "call_cache_delete"
        mock_tool_call_delete.type = "function"
        mock_tool_call_delete.function.name = "cache_interaction"
        mock_tool_call_delete.function.arguments = json.dumps({"action": "delete", "key": "test_key"})


        def create_mock_assistant_response(tool_call, final_text):
            mock_response_1 = MagicMock()
            mock_response_1.choices = [MagicMock()]
            mock_response_1.choices[0].message.content = None
            mock_response_1.choices[0].message.tool_calls = [tool_call]
            mock_response_1.choices[0].message.role = "assistant"

            mock_response_2 = MagicMock()
            mock_response_2.choices = [MagicMock()]
            mock_response_2.choices[0].message.content = final_text
            mock_response_2.choices[0].message.tool_calls = None
            mock_response_2.choices[0].message.role = "assistant"
            mock_response_2.choices[0].message.type = None

            return [mock_response_1, mock_response_2]

        mock_client.chat.completions.create.side_effect = (
            create_mock_assistant_response(mock_tool_call_set, "Set cache.") +
            create_mock_assistant_response(mock_tool_call_get, "Got cache.") +
            create_mock_assistant_response(mock_tool_call_delete, "Deleted cache.")
        )

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        # Test Set
        response_set = await session.process_user_input("Set cache")
        self.assertEqual(response_set, "Set cache.")
        mock_agent_client.post.assert_called_with("/api/cache/test_key?ttl=60", content="test_val")

        # Session message length will be 5
        self.assertEqual(len(session.messages), 5)
        self.assertIn("success", session.messages[3]["content"])

        # Test Get
        response_get = await session.process_user_input("Get cache")
        self.assertEqual(response_get, "Got cache.")
        mock_agent_client.get.assert_called_with("/api/cache/test_key")

        # Session message length will be 9
        self.assertEqual(len(session.messages), 9)
        self.assertIn("test_val", session.messages[7]["content"])

        # Test Delete
        response_delete = await session.process_user_input("Delete cache")
        self.assertEqual(response_delete, "Deleted cache.")
        mock_agent_client.delete.assert_called_with("/api/cache/test_key")

        # Session message length will be 13
        self.assertEqual(len(session.messages), 13)
        self.assertIn("deleted", session.messages[11]["content"])



    async def test_manage_features_get(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"new-ui": True, "beta-feature": False}
        mock_agent_client.get.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_feat1"
        mock_tool_call_1.function.name = "manage_features"
        mock_tool_call_1.function.arguments = '{"action": "get"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Features listed."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("List features")

        self.assertEqual(response, "Features listed.")
        mock_agent_client.get.assert_called_once_with("/api/features")
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_feat1")
        self.assertEqual(json.loads(session.messages[3]["content"]), {"new-ui": True, "beta-feature": False})

    async def test_manage_features_put(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Feature updated successfully"}
        mock_agent_client.put.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_feat2"
        mock_tool_call_1.function.name = "manage_features"
        mock_tool_call_1.function.arguments = '{"action": "put", "feature_name": "new-ui", "enabled": true}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Feature updated."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Enable new-ui")

        self.assertEqual(response, "Feature updated.")
        mock_agent_client.put.assert_called_once_with("/api/features/new-ui", json={"enabled": True})
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_feat2")
        self.assertEqual(json.loads(session.messages[3]["content"]), {"message": "Feature updated successfully"})

    async def test_manage_features_delete(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Feature deleted successfully"}
        mock_agent_client.delete.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_feat3"
        mock_tool_call_1.function.name = "manage_features"
        mock_tool_call_1.function.arguments = '{"action": "delete", "feature_name": "new-ui"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Feature deleted."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Delete new-ui")

        self.assertEqual(response, "Feature deleted.")
        mock_agent_client.delete.assert_called_once_with("/api/features/new-ui")
        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertEqual(session.messages[3]["tool_call_id"], "call_feat3")
        self.assertEqual(json.loads(session.messages[3]["content"]), {"message": "Feature deleted successfully"})


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
        session.session_paused = True
        session.paused_reason = "Waiting for external API"
        session.total_tokens_used = 100
        session.prompt_tokens_used = 60
        session.completion_tokens_used = 40
        session.user_preferences = {"theme": "dark", "language": "French"}

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
            self.assertEqual(loaded_session.user_preferences, {"theme": "dark", "language": "French"})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestChatSessionNotifications(unittest.IsolatedAsyncioTestCase):
    async def test_manage_notifications_get(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "n1", "user_id": "u1", "is_read": False}]
        mock_agent_client.get.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_notif1"
        mock_tool_call_1.function.name = "manage_notifications"
        mock_tool_call_1.function.arguments = '{"action": "get", "user_id": "u1", "unread_only": true}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Notifications retrieved."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Get my notifications")
        self.assertEqual(response, "Notifications retrieved.")
        mock_agent_client.get.assert_called_with("/api/notifications", params={"user_id": "u1", "unread_only": "true"})

    async def test_manage_notifications_mark_read(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "n1", "user_id": "u1", "is_read": True}
        mock_agent_client.put.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_notif2"
        mock_tool_call_1.function.name = "manage_notifications"
        mock_tool_call_1.function.arguments = '{"action": "mark_read", "notification_id": "n1"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Notification marked read."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Mark notification n1 as read")
        self.assertEqual(response, "Notification marked read.")
        mock_agent_client.put.assert_called_with("/api/notifications/n1/read")

class TestChatSessionComments(unittest.IsolatedAsyncioTestCase):
    async def test_manage_comments_get(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "c1", "user_id": "u1", "text": "Hello"}]
        mock_agent_client.get.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_com1"
        mock_tool_call_1.function.name = "manage_comments"
        mock_tool_call_1.function.arguments = '{"action": "get", "entity_id": "e1"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Comments retrieved."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Get comments for e1")
        self.assertEqual(response, "Comments retrieved.")
        mock_agent_client.get.assert_called_with("/api/comments/e1")

    async def test_manage_comments_create(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "c2", "user_id": "u1", "text": "New"}
        mock_agent_client.post.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_com2"
        mock_tool_call_1.function.name = "manage_comments"
        mock_tool_call_1.function.arguments = '{"action": "create", "entity_id": "e1", "user_id": "u1", "text": "New"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Comment created."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Create comment")
        self.assertEqual(response, "Comment created.")
        mock_agent_client.post.assert_called_with("/api/comments/e1", json={"user_id": "u1", "text": "New"})

    async def test_manage_comments_delete(self):
        mock_client = MagicMock()
        mock_agent_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_agent_client.delete.return_value = mock_response

        session = ChatSession(system_prompt="Test", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_com3"
        mock_tool_call_1.function.name = "manage_comments"
        mock_tool_call_1.function.arguments = '{"action": "delete", "comment_id": "c1"}'

        mock_message_1 = MagicMock()
        mock_message_1.role = "assistant"
        mock_message_1.content = None
        mock_message_1.tool_calls = [mock_tool_call_1]

        mock_message_final = MagicMock()
        mock_message_final.role = "assistant"
        mock_message_final.content = "Comment deleted."
        mock_message_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_message_1)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)])
        ])

        response = await session.process_user_input("Delete comment c1")
        self.assertEqual(response, "Comment deleted.")
        mock_agent_client.delete.assert_called_with("/api/comments/c1")

    async def test_manage_events_list(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"id": "evt_1", "title": "Test Event"}]
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_evt_list"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_events"
        mock_tool_call.function.arguments = json.dumps({"action": "list"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Events listed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        await session.process_user_input("List events")
        mock_agent_client.get.assert_called_with("/api/events")

    async def test_manage_events_create(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=201,
            json=lambda: {"id": "evt_2", "title": "New Event"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_evt_create"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_events"
        mock_tool_call.function.arguments = json.dumps({"action": "create", "title": "New Event", "start_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Event created."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        await session.process_user_input("Create event")
        mock_agent_client.post.assert_called_with("/api/events", json={"title": "New Event", "start_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"})

    async def test_manage_payments_process(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"payment_id": "pay_1", "status": "success"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_pay_process"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_payments"
        mock_tool_call.function.arguments = json.dumps({"action": "process", "amount": 100, "currency": "USD", "payment_method": "credit_card"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Payment processed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        await session.process_user_input("Process payment")
        mock_agent_client.post.assert_called_with("/api/payments", json={"amount": 100, "currency": "USD", "payment_method": "credit_card"})

    async def test_manage_payments_get_status(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"payment_id": "pay_1", "status": "success"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_pay_get"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_payments"
        mock_tool_call.function.arguments = json.dumps({"action": "get_status", "payment_id": "pay_1"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Payment status fetched."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        await session.process_user_input("Get payment status")
        mock_agent_client.get.assert_called_with("/api/payments/pay_1")


    async def test_manage_subscriptions_create(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"subscription_id": "sub_1", "status": "active"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_sub_create"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_subscriptions"
        mock_tool_call.function.arguments = json.dumps({"action": "create", "plan_id": "plan_A", "user_id": "user_1"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Subscription created."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Create subscription")
        self.assertEqual(response, "Subscription created.")
        mock_agent_client.post.assert_called_with("/api/subscriptions", json={"plan_id": "plan_A", "user_id": "user_1"})

    async def test_manage_subscriptions_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"subscription_id": "sub_1", "status": "active"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_sub_get"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_subscriptions"
        mock_tool_call.function.arguments = json.dumps({"action": "get", "subscription_id": "sub_1"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Subscription found."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Get subscription")
        self.assertEqual(response, "Subscription found.")
        mock_agent_client.get.assert_called_with("/api/subscriptions/sub_1")

    async def test_manage_subscriptions_cancel(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.delete.return_value = MagicMock(
            status_code=200,
            json=lambda: {"detail": "Subscription canceled successfully", "subscription_id": "sub_1"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_sub_cancel"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_subscriptions"
        mock_tool_call.function.arguments = json.dumps({"action": "cancel", "subscription_id": "sub_1"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Subscription canceled."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Cancel subscription")
        self.assertEqual(response, "Subscription canceled.")
        mock_agent_client.delete.assert_called_with("/api/subscriptions/sub_1")

    async def test_manage_tickets_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"ticket_id": "ticket_1", "subject": "Issue 1"}]
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_tickets_get"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_tickets"
        mock_tool_call.function.arguments = json.dumps({"action": "get"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Tickets listed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Get tickets")
        self.assertEqual(response, "Tickets listed.")
        mock_agent_client.get.assert_called_with("/api/tickets")

    async def test_manage_tickets_create(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"ticket_id": "ticket_2", "subject": "Issue 2"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_tickets_create"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_tickets"
        mock_tool_call.function.arguments = json.dumps({
            "action": "create",
            "subject": "Issue 2",
            "description": "It is broken",
            "user_id": "user_1"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Ticket created."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Create ticket")
        self.assertEqual(response, "Ticket created.")
        mock_agent_client.post.assert_called_with("/api/tickets", json={"subject": "Issue 2", "description": "It is broken", "user_id": "user_1"})

    async def test_manage_tickets_update(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.patch.return_value = MagicMock(
            status_code=200,
            json=lambda: {"ticket_id": "ticket_3", "status": "closed"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_tickets_update"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_tickets"
        mock_tool_call.function.arguments = json.dumps({
            "action": "update",
            "ticket_id": "ticket_3",
            "status": "closed"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Ticket updated."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Update ticket")
        self.assertEqual(response, "Ticket updated.")
        mock_agent_client.patch.assert_called_with("/api/tickets/ticket_3", json={"status": "closed"})

    async def test_manage_devices_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"id": "dev_1", "name": "Device 1", "type": "desktop"}]
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_devices_get"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_devices"
        mock_tool_call.function.arguments = json.dumps({"action": "get"})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Devices listed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ]

        response = await session.process_user_input("list devices")
        self.assertEqual(response, "Devices listed.")

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        tool_content = json.loads(session.messages[3]["content"])
        self.assertEqual(tool_content[0]["name"], "Device 1")
        mock_agent_client.get.assert_called_with("/api/devices")

    async def test_manage_devices_create(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "dev_2", "name": "Device 2", "type": "mobile"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_devices_create"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_devices"
        mock_tool_call.function.arguments = json.dumps({
            "action": "create",
            "name": "Device 2",
            "type": "mobile",
            "os_version": "iOS 16"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Device registered."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ]

        response = await session.process_user_input("register device")
        self.assertEqual(response, "Device registered.")

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertIn("Device registered", session.messages[3]["content"])
        mock_agent_client.post.assert_called_with("/api/devices", json={"name": "Device 2", "type": "mobile", "os_version": "iOS 16"})

    async def test_manage_devices_delete(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.delete.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "deleted"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_devices_delete"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_devices"
        mock_tool_call.function.arguments = json.dumps({
            "action": "delete",
            "device_id": "dev_3"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Device removed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ]

        response = await session.process_user_input("remove device")
        self.assertEqual(response, "Device removed.")

        self.assertEqual(len(session.messages), 5)
        self.assertEqual(session.messages[3]["role"], "tool")
        self.assertIn("Device deleted", session.messages[3]["content"])
        mock_agent_client.delete.assert_called_with("/api/devices/dev_3")


    async def test_manage_user_tasks_get(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"id": "task_1", "title": "Task 1", "completed": False}]
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_user_tasks_get"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_user_tasks"
        mock_tool_call.function.arguments = json.dumps({"action": "get", "completed": False})

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "User tasks listed."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Get user tasks")
        self.assertEqual(response, "User tasks listed.")
        mock_agent_client.get.assert_called_with("/api/user-tasks", params={"completed": "false"})

    async def test_manage_user_tasks_create(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "task_2", "title": "Task 2"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_user_tasks_create"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_user_tasks"
        mock_tool_call.function.arguments = json.dumps({
            "action": "create",
            "title": "Task 2",
            "description": "My task",
            "completed": True
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "User task created."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Create user task")
        self.assertEqual(response, "User task created.")
        mock_agent_client.post.assert_called_with("/api/user-tasks", json={"title": "Task 2", "description": "My task", "completed": True})

    async def test_manage_user_tasks_update(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.patch.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "task_3", "completed": True}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_user_tasks_update"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_user_tasks"
        mock_tool_call.function.arguments = json.dumps({
            "action": "update",
            "task_id": "task_3",
            "completed": True
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "User task updated."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Update user task")
        self.assertEqual(response, "User task updated.")
        mock_agent_client.patch.assert_called_with("/api/user-tasks/task_3", json={"completed": True})

    async def test_manage_user_tasks_delete(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.delete.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "deleted"}
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_user_tasks_delete"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_user_tasks"
        mock_tool_call.function.arguments = json.dumps({
            "action": "delete",
            "task_id": "task_4"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "User task deleted."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Delete user task")
        self.assertEqual(response, "User task deleted.")
        mock_agent_client.delete.assert_called_with("/api/user-tasks/task_4")

    async def test_manage_email_send(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.post.return_value = MagicMock(
            status_code=201,
            text='{"id": "msg_1", "to": "test@example.com", "subject": "Hello", "body": "World", "sent_at": "2023-10-27T10:00:00Z"}'
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_email_send"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_email"
        mock_tool_call.function.arguments = json.dumps({
            "action": "send",
            "payload": {
                "to": "test@example.com",
                "subject": "Hello",
                "body": "World"
            }
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Email sent."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Send email")
        self.assertEqual(response, "Email sent.")
        mock_agent_client.post.assert_called_with("/api/email/send", json={"to": "test@example.com", "subject": "Hello", "body": "World"})
        self.assertIn("Email sent successfully", session.messages[3]["content"])

    async def test_manage_email_get_outbox(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.get.return_value = MagicMock(
            status_code=200,
            text='[{"id": "msg_1", "to": "test@example.com", "subject": "Hello", "body": "World", "sent_at": "2023-10-27T10:00:00Z"}]'
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_email_get_outbox"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_email"
        mock_tool_call.function.arguments = json.dumps({
            "action": "get_outbox"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Email outbox retrieved."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Get email outbox")
        self.assertEqual(response, "Email outbox retrieved.")
        mock_agent_client.get.assert_called_with("/api/email/outbox")
        self.assertIn("Email outbox:", session.messages[3]["content"])

    async def test_manage_email_clear_outbox(self):
        mock_client = AsyncMock()
        mock_agent_client = AsyncMock()
        mock_agent_client.delete.return_value = MagicMock(
            status_code=204
        )

        session = ChatSession(system_prompt="Test prompt", client=mock_client, agent_client=mock_agent_client)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_email_clear_outbox"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "manage_email"
        mock_tool_call.function.arguments = json.dumps({
            "action": "clear_outbox"
        })

        mock_msg_1 = MagicMock()
        mock_msg_1.role = "assistant"
        mock_msg_1.content = None
        mock_msg_1.tool_calls = [mock_tool_call]

        mock_msg_final = MagicMock()
        mock_msg_final.role = "assistant"
        mock_msg_final.content = "Email outbox cleared."
        mock_msg_final.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(side_effect=[
            MagicMock(choices=[MagicMock(message=mock_msg_1)]),
            MagicMock(choices=[MagicMock(message=mock_msg_final)])
        ])

        response = await session.process_user_input("Clear email outbox")
        self.assertEqual(response, "Email outbox cleared.")
        mock_agent_client.delete.assert_called_with("/api/email/outbox")
        self.assertIn("Email outbox cleared successfully.", session.messages[3]["content"])
