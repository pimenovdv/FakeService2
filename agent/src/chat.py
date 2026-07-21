from src.client import AgentClient
import json
import re
import asyncio
import datetime
import random
import string
import logging
import os
import mimetypes
from typing import List, Dict, Any, Callable, Awaitable
from openai import AsyncOpenAI
from py_mini_racer import MiniRacer
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)

class ChatSession:
    def __init__(self, system_prompt: str, client: AsyncOpenAI = None, agent_client: AgentClient = None, model: str = "gpt-4o-mini", max_retries: int = 3, timeout: float = 30.0):
        self.max_retries = max_retries
        self.timeout = timeout
        self.client = client or AsyncOpenAI()
        self.model = model
        self.agent_client = agent_client
        self.messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]
        self.user_preferences: Dict[str, Any] = {}
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_datetime",
                    "description": "Get the current date and time.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_uuid",
                    "description": "Generate a new UUID v4.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_user_preferences",
                    "description": "Update the user's preferences (e.g., tone, language, verbosity) for the session.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "preferences": {
                                "type": "object",
                                "description": "A dictionary of key-value pairs representing the user preferences.",
                                "additionalProperties": True
                            }
                        },
                        "required": ["preferences"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_exchange_rate",
                    "description": "Get the current mock exchange rate between two currencies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base_currency": {
                                "type": "string",
                                "description": "The base currency code (e.g., USD)."
                            },
                            "target_currency": {
                                "type": "string",
                                "description": "The target currency code (e.g., EUR)."
                            }
                        },
                        "required": ["base_currency", "target_currency"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "translate_text",
                    "description": "Mock tool to translate text from one language to another.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to translate."
                            },
                            "source_language": {
                                "type": "string",
                                "description": "The source language code (e.g., en)."
                            },
                            "target_language": {
                                "type": "string",
                                "description": "The target language code (e.g., es)."
                            }
                        },
                        "required": ["text", "source_language", "target_language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_distance",
                    "description": "Mock tool to calculate the distance between two locations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "string",
                                "description": "The origin location."
                            },
                            "destination": {
                                "type": "string",
                                "description": "The destination location."
                            }
                        },
                        "required": ["origin", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_js",
                    "description": "Mock tool to evaluate simple JavaScript state changes based on extracted logic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "script_content": {
                                "type": "string",
                                "description": "The JavaScript code to evaluate."
                            },
                            "context": {
                                "type": "object",
                                "description": "Current state/context variables to pass to the script.",
                                "additionalProperties": True
                            }
                        },
                        "required": ["script_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current mock weather for a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to get the weather for."
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_health",
                    "description": "Retrieve the current health status of the backend system and its connected services.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_available_services",
                    "description": "Retrieve the list of available service IDs from the backend that the user can start a form for.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_mock_data",
                    "description": "Auto-generate mock values for the provided fields to help the user fill out a form faster.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "fields": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "label": {"type": "string"}
                                    },
                                    "required": ["id"]
                                },
                                "description": "The fields to generate mock values for."
                            }
                        },
                        "required": ["fields"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_autocomplete_options",
                    "description": "Fetch available options for an autocomplete field from the backend.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_source": {
                                "type": "string",
                                "description": "The data source endpoint to fetch from."
                            },
                            "query": {
                                "type": "string",
                                "description": "Optional search query to filter the autocomplete options."
                            }
                        },
                        "required": ["data_source"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_session_stats",
                    "description": "Retrieve current session statistics, including token usage and message count.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "reset_session",
                    "description": "Resets the chat session state, clearing the conversation history and resetting all session states. Use this when the user wants to start over from scratch.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_and_parse_file",
                    "description": "Download a file from a given URL and parse its content. Use this to retrieve downloaded files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the file to download."
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "upload_file",
                    "description": "Upload a local file to a given URL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to upload the file to."
                            },
                            "filepath": {
                                "type": "string",
                                "description": "The local path to the file to upload."
                            },
                            "max_size": {
                                "type": "integer",
                                "description": "The maximum allowed file size in bytes (optional)."
                            },
                            "allowed_types": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "A list of allowed MIME types for the file (optional)."
                            }
                        },
                        "required": ["url", "filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_datetime",
                    "description": "Get the current date and time to help calculate date offsets or relative dates like 'tomorrow'.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_form",
                    "description": "Evaluate offline form validation logic (required, minlength, maxlength, pattern, min, max, etc.) for a set of answers against a set of fields before submission.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answers": {
                                "type": "object",
                                "description": "The current answers provided by the user.",
                                "additionalProperties": True
                            },
                            "fields": {
                                "type": "array",
                                "description": "The field definitions extracted from the screen.",
                                "items": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            },
                            "cross_validations": {
                                "type": "array",
                                "description": "The cross-validation rules to evaluate.",
                                "items": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        },
                        "required": ["answers", "fields"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "submit_form",
                    "description": "Submit the form data once all required fields are gathered.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answers": {
                                "type": "object",
                                "description": "The key-value pairs representing the filled form fields."
                            }
                        },
                        "required": ["answers"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "abort_form",
                    "description": "Abort the form submission flow. Use this when the user explicitly cancels or when an unrecoverable error occurs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "The reason for aborting the form submission."
                            }
                        },
                        "required": ["reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "export_chat_history",
                    "description": "Exports the current chat history to a specified local JSON file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "The local path where the chat history should be saved as a JSON file."
                            }
                        },
                        "required": ["filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pause_session",
                    "description": "Pause the current session, saving the state so it can be resumed later. Use this when you are waiting for a long-running process or need the user to take actions before continuing.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "The reason for pausing the session."
                            }
                        },
                        "required": ["reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "request_human_handoff",
                    "description": "Escalate the session to a human operator. Use this when you are unable to assist the user further or when they explicitly request human assistance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "A summary of the situation and why handoff is needed."
                            }
                        },
                        "required": ["summary"]
                    }
                }
            }
        ]
        self.form_submitted = False
        self.submitted_data = None
        self.form_aborted = False
        self.aborted_reason = None
        self.handoff_requested = False
        self.handoff_summary = None
        self.session_paused = False
        self.paused_reason = None

        # Token usage tracking
        self.total_tokens_used = 0
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0



    def save_state(self, filepath: str) -> None:
        """
        Save the current state of the chat session to a JSON file.
        """
        state = {
            "model": self.model,
            "messages": self.messages,
            "form_submitted": self.form_submitted,
            "submitted_data": self.submitted_data,
            "form_aborted": self.form_aborted,
            "aborted_reason": self.aborted_reason,
            "handoff_requested": self.handoff_requested,
            "handoff_summary": self.handoff_summary,
            "session_paused": self.session_paused,
            "paused_reason": self.paused_reason,
            "total_tokens_used": self.total_tokens_used,
            "prompt_tokens_used": self.prompt_tokens_used,
            "completion_tokens_used": self.completion_tokens_used,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "user_preferences": self.user_preferences
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_state(cls, filepath: str, client: AsyncOpenAI = None, agent_client: AgentClient = None) -> 'ChatSession':
        """
        Load a ChatSession from a previously saved state JSON file.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # Initialize with dummy prompt, we will overwrite messages
        session = cls(system_prompt="", client=client, agent_client=agent_client,
                      model=state.get("model", "gpt-4o-mini"),
                      max_retries=state.get("max_retries", 3),
                      timeout=state.get("timeout", 30.0))

        session.messages = state.get("messages", [])
        session.form_submitted = state.get("form_submitted", False)
        session.submitted_data = state.get("submitted_data", None)
        session.form_aborted = state.get("form_aborted", False)
        session.aborted_reason = state.get("aborted_reason", None)
        session.handoff_requested = state.get("handoff_requested", False)
        session.handoff_summary = state.get("handoff_summary", None)
        session.session_paused = state.get("session_paused", False)
        session.paused_reason = state.get("paused_reason", None)
        session.total_tokens_used = state.get("total_tokens_used", 0)
        session.prompt_tokens_used = state.get("prompt_tokens_used", 0)
        session.completion_tokens_used = state.get("completion_tokens_used", 0)
        session.user_preferences = state.get("user_preferences", {})

        return session

    async def _call_llm(self, messages, tools=None, tool_choice=None):
        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                if tool_choice:
                    kwargs["tool_choice"] = tool_choice

                # The openai client natively supports `timeout` param, but we can also use wait_for
                # for strict enforcement. We pass timeout to create() as well.
                coro = self.client.chat.completions.create(**kwargs, timeout=self.timeout)
                response = await asyncio.wait_for(coro, timeout=self.timeout + 5.0)

                # Update usage tracking
                if hasattr(response, "usage") and response.usage:
                    self.total_tokens_used += getattr(response.usage, "total_tokens", 0) or 0
                    self.prompt_tokens_used += getattr(response.usage, "prompt_tokens", 0) or 0
                    self.completion_tokens_used += getattr(response.usage, "completion_tokens", 0) or 0

                return response
            except Exception as e:
                logger.warning(f"LLM API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and get a response from the LLM, potentially handling tool calls.
        """
        logger.info(f"User input: {user_input}")
        self.messages.append({"role": "user", "content": user_input})

        MAX_TURNS = 10
        for turn in range(MAX_TURNS):
            try:
                response = await self._call_llm(
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
            except Exception as e:
                logger.error(f"Error during LLM completion: {e}")
                return "I encountered an error processing your request."

            response_message = response.choices[0].message
            logger.debug(f"LLM response content: {response_message.content}, tool_calls: {response_message.tool_calls}")

            message_dict = {"role": "assistant"}
            if response_message.content:
                message_dict["content"] = response_message.content
            if getattr(response_message, "tool_calls", None):
                message_dict["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        }
                    }
                    for tool_call in response_message.tool_calls
                ]
            self.messages.append(message_dict)

            if not getattr(response_message, "tool_calls", None):
                # No more tool calls, we can return the response
                return response_message.content or ""

            for tool_call in response_message.tool_calls:
                logger.info(f"Executing tool call: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
                if tool_call.function.name == "submit_form":
                    args = json.loads(tool_call.function.arguments)
                    self.form_submitted = True
                    self.submitted_data = args.get("answers", {})

                    # Provide tool result back to the model
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Form submitted successfully."})
                    })


                elif tool_call.function.name == "validate_form":
                    args = json.loads(tool_call.function.arguments)
                    answers = args.get("answers", {})
                    fields = args.get("fields", [])

                    errors = []
                    for field in fields:
                        field_id = field.get("id") or field.get("name")
                        if not field_id:
                            continue

                        val = answers.get(field_id)
                        attrs = field.get("attributes", {})

                        # required
                        if attrs.get("required") and (val is None or val == ""):
                            errors.append({"field": field_id, "error": "required"})

                        if val is not None and val != "":
                            # minlength
                            if "minlength" in attrs:
                                try:
                                    if len(str(val)) < int(attrs["minlength"]):
                                        errors.append({"field": field_id, "error": f"minlength ({attrs['minlength']})"})
                                except ValueError:
                                    pass

                            # maxlength
                            if "maxlength" in attrs:
                                try:
                                    if len(str(val)) > int(attrs["maxlength"]):
                                        errors.append({"field": field_id, "error": f"maxlength ({attrs['maxlength']})"})
                                except ValueError:
                                    pass

                            # pattern
                            if "pattern" in attrs:
                                try:
                                    if not re.search(attrs["pattern"], str(val)):
                                        errors.append({"field": field_id, "error": f"pattern mismatch ({attrs['pattern']})"})
                                except Exception as e:
                                    logger.error(f"Error evaluating pattern {attrs['pattern']} on field {field_id}: {e}")

                            # min
                            if "min" in attrs:
                                try:
                                    if float(val) < float(attrs["min"]):
                                        errors.append({"field": field_id, "error": f"min ({attrs['min']})"})
                                except ValueError:
                                    pass

                            # max
                            if "max" in attrs:
                                try:
                                    if float(val) > float(attrs["max"]):
                                        errors.append({"field": field_id, "error": f"max ({attrs['max']})"})
                                except ValueError:
                                    pass

                    cross_validations = args.get("cross_validations", [])
                    for rule in cross_validations:
                        rule_type = rule.get("type")
                        if rule_type == "match":
                            rule_fields = rule.get("fields", [])
                            if len(rule_fields) > 1:
                                first_val = answers.get(rule_fields[0])
                                for i in range(1, len(rule_fields)):
                                    if answers.get(rule_fields[i]) != first_val:
                                        errors.append({"error": rule.get("message", "match failed")})
                                        break
                        elif rule_type == "required_if":
                            cond_field = rule.get("condition_field")
                            target_field = rule.get("target_field")
                            if cond_field and target_field:
                                cond_val = answers.get(cond_field)
                                if cond_val == rule.get("condition_value"):
                                    target_val = answers.get(target_field)
                                    if target_val is None or target_val == "":
                                        errors.append({"field": target_field, "error": rule.get("message", "required_if failed")})

                    result = {
                        "valid": len(errors) == 0,
                        "errors": errors
                    }

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                elif tool_call.function.name == "pause_session":
                    args = json.loads(tool_call.function.arguments)
                    self.session_paused = True
                    self.paused_reason = args.get("reason", "No reason provided")

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Session paused successfully."})
                    })

                elif tool_call.function.name == "abort_form":
                    args = json.loads(tool_call.function.arguments)
                    self.form_aborted = True
                    self.aborted_reason = args.get("reason", "No reason provided")

                    # Provide tool result back to the model
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Form aborted successfully."})
                    })

                elif tool_call.function.name == "reset_session":
                    # Truncate messages to only the system prompt and the assistant tool call message
                    self.messages = [self.messages[0], self.messages[-1]]

                    # Reset all session states
                    self.form_submitted = False
                    self.submitted_data = None
                    self.form_aborted = False
                    self.aborted_reason = None
                    self.handoff_requested = False
                    self.handoff_summary = None
                    self.session_paused = False
                    self.paused_reason = None

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Session reset successfully."})
                    })

                elif tool_call.function.name == "update_user_preferences":
                    args = json.loads(tool_call.function.arguments)
                    preferences = args.get("preferences", {})
                    self.user_preferences.update(preferences)

                    tool_content = json.dumps({"status": "success", "user_preferences": self.user_preferences})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_content
                    })

                elif tool_call.function.name == "get_session_stats":
                    stats = {
                        "prompt_tokens_used": self.prompt_tokens_used,
                        "completion_tokens_used": self.completion_tokens_used,
                        "total_tokens_used": self.total_tokens_used,
                        "message_count": len(self.messages)
                    }
                    tool_content = json.dumps(stats)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_content
                    })

                elif tool_call.function.name == "export_chat_history":
                    args = json.loads(tool_call.function.arguments)
                    filepath = args.get("filepath")

                    try:
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(self.messages, f, ensure_ascii=False, indent=2)
                        tool_content = json.dumps({"status": "success", "message": f"Chat history exported to {filepath}"})
                    except Exception as e:
                        tool_content = json.dumps({"status": "error", "message": f"Failed to export chat history: {e}"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "request_human_handoff":
                    args = json.loads(tool_call.function.arguments)
                    self.handoff_requested = True
                    self.handoff_summary = args.get("summary", "No summary provided")

                    # Provide tool result back to the model
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Handoff to human requested successfully."})
                    })

                elif tool_call.function.name == "fetch_autocomplete_options":
                    args = json.loads(tool_call.function.arguments)
                    data_source = args.get("data_source")
                    query = args.get("query")
                    params = {"q": query} if query else None

                    if self.agent_client:
                        try:
                            res = await self.agent_client.get(f"/api/data/{data_source}", params=params)
                            if res.status_code == 200:
                                tool_content = res.text
                            else:
                                tool_content = json.dumps({"error": f"Failed to fetch data, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                    # After fetching data, we need to let the LLM generate a response

                elif tool_call.function.name == "get_weather":
                    args = json.loads(tool_call.function.arguments)
                    location = args.get("location", "Unknown Location")

                    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
                    weather_condition = random.choice(conditions)
                    temperature = random.randint(-10, 35)

                    tool_content = json.dumps({
                        "location": location,
                        "temperature": f"{temperature}°C",
                        "condition": weather_condition
                    })

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "get_current_datetime":
                    import datetime
                    now = datetime.datetime.now().isoformat()
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"current_datetime": now})
                    })

                elif tool_call.function.name == "generate_uuid":
                    import uuid
                    new_uuid = str(uuid.uuid4())
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"uuid": new_uuid})
                    })

                elif tool_call.function.name == "get_exchange_rate":
                    args = json.loads(tool_call.function.arguments)
                    base_currency = args.get("base_currency", "USD").upper()
                    target_currency = args.get("target_currency", "EUR").upper()

                    rate = round(random.uniform(0.5, 1.5), 4)

                    tool_content = json.dumps({
                        "base_currency": base_currency,
                        "target_currency": target_currency,
                        "exchange_rate": rate
                    })

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "translate_text":
                    args = json.loads(tool_call.function.arguments)
                    text = args.get("text", "")
                    source_language = args.get("source_language", "")
                    target_language = args.get("target_language", "")

                    # Mock translation logic
                    mock_translation = f"Translated '{text}' from {source_language} to {target_language} (mocked)"

                    tool_content = json.dumps({
                        "text": text,
                        "source_language": source_language,
                        "target_language": target_language,
                        "translated_text": mock_translation
                    })

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "calculate_distance":
                    args = json.loads(tool_call.function.arguments)
                    origin = args.get("origin", "")
                    destination = args.get("destination", "")

                    # Mock distance logic
                    mock_distance = round(random.uniform(10.0, 1000.0), 2)
                    unit = "km"

                    tool_content = json.dumps({
                        "origin": origin,
                        "destination": destination,
                        "distance": mock_distance,
                        "unit": unit
                    })

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "evaluate_js":
                    args = json.loads(tool_call.function.arguments)
                    script_content = args.get("script_content", "")
                    context_data = args.get("context", {})

                    try:
                        ctx = MiniRacer()
                        if context_data:
                            for key, value in context_data.items():
                                val_json = json.dumps(value)
                                ctx.eval(f"var {key} = {val_json};")

                        result = ctx.eval(script_content)
                        tool_content = json.dumps({"result": result, "evaluated_script": script_content})
                    except Exception as e:
                        logger.error(f"Error evaluating JS: {e}")
                        tool_content = json.dumps({"error": str(e), "evaluated_script": script_content})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_content
                    })

                elif tool_call.function.name == "generate_mock_data":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        fields = args.get("fields", [])

                        mocked_data = {}

                        for field in fields:
                            field_id = field.get("id")
                            if not field_id:
                                continue

                            field_type = str(field.get("type", "")).lower()
                            field_name = str(field.get("name", "")).lower()
                            field_label = str(field.get("label", "")).lower()

                            if "email" in field_type or "email" in field_name or "email" in field_label:
                                val = "mockuser" + str(random.randint(100, 999)) + "@example.com"
                            elif "phone" in field_type or "phone" in field_name or "phone" in field_label:
                                val = "555-01" + str(random.randint(10, 99))
                            elif field_type == "number":
                                val = str(random.randint(1, 100))
                            elif "date" in field_type or "date" in field_name:
                                val = "2024-01-01"
                            elif "name" in field_name or "name" in field_label:
                                val = "Mock Name"
                            else:
                                val = "Mock Value " + ''.join(random.choices(string.ascii_letters, k=5))

                            mocked_data[field_id] = val

                        tool_content = json.dumps({"mock_data": mocked_data})
                    except Exception as e:
                        logger.error(f"Error generating mock data: {e}")
                        tool_content = json.dumps({"error": str(e)})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "retrieve_available_services":
                    if self.agent_client:
                        try:
                            res = await self.agent_client.get("/api/screens/available_services")
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to fetch services, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "get_system_health":
                    if self.agent_client:
                        try:
                            res = await self.agent_client.get("/api/health")
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to fetch health, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "download_and_parse_file":
                    args = json.loads(tool_call.function.arguments)
                    url = args.get("url")

                    if self.agent_client:
                        try:
                            res = await self.agent_client.get(url)
                            if res.status_code == 200:
                                content_type = res.headers.get("content-type", "")
                                if "application/json" in content_type.lower():
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = res.text
                            else:
                                tool_content = json.dumps({"error": f"Failed to download file, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "upload_file":
                    args = json.loads(tool_call.function.arguments)
                    url = args.get("url")
                    filepath = args.get("filepath")
                    max_size = args.get("max_size")
                    allowed_types = args.get("allowed_types")

                    if self.agent_client:
                        try:
                            # File validation
                            if os.path.exists(filepath):
                                if max_size is not None:
                                    file_size = os.path.getsize(filepath)
                                    if file_size > max_size:
                                        raise ValueError(f"File exceeds maximum size of {max_size} bytes")

                                if allowed_types is not None and len(allowed_types) > 0:
                                    mime_type, _ = mimetypes.guess_type(filepath)
                                    if mime_type not in allowed_types:
                                        raise ValueError(f"File type {mime_type} not allowed")

                            with open(filepath, "rb") as f:
                                res = await self.agent_client.post(url, files={"file": f})
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to upload file, status code {res.status_code}"})
                        except FileNotFoundError:
                            tool_content = json.dumps({"error": f"File not found: {filepath}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })





        return "I'm sorry, but I was unable to complete the request within the allowed number of steps."

async def run_chat_loop(
    session: ChatSession,
    input_func: Callable[[], Awaitable[str]],
    output_func: Callable[[str], Awaitable[None]]
):
    """
    A simple CLI loop for the chat session.
    """
    await output_func("Agent initialized. What would you like to do?")

    while not session.form_submitted and not session.form_aborted and not session.handoff_requested and not getattr(session, "session_paused", False):
        user_text = await input_func()
        if user_text.lower() in ["exit", "quit"]:
            await output_func("Exiting chat.")
            break

        response_text = await session.process_user_input(user_text)
        await output_func(response_text)

    if session.form_submitted:
        await output_func(f"Form submission complete with data: {session.submitted_data}")
    elif session.form_aborted:
        await output_func(f"Form aborted with reason: {session.aborted_reason}")
    elif session.handoff_requested:
        await output_func(f"Handoff to human requested. Summary: {session.handoff_summary}")
    elif session.session_paused:
        await output_func(f"Session paused. Reason: {session.paused_reason}")
