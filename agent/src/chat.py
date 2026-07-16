from src.client import AgentClient
import json
import asyncio
import datetime
import logging
from typing import List, Dict, Any, Callable, Awaitable
from openai import AsyncOpenAI
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
        self.tools = [
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
            "timeout": self.timeout
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

        try:
            response = await self._call_llm(
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )
        except Exception as e:
            logger.error(f"Error during initial LLM completion: {e}")
            return "I encountered an error processing your request."

        response_message = response.choices[0].message
        logger.debug(f"LLM initial response content: {response_message.content}, tool_calls: {response_message.tool_calls}")

        # We need to serialize the response message back into dict format if we append it
        message_dict = {"role": "assistant"}
        if response_message.content:
            message_dict["content"] = response_message.content
        if response_message.tool_calls:
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

        if response_message.tool_calls:
            # Handle tool calls
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

                    # Get final conversational response after tool call
                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or "Form submitted."
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (submit_form): {e}")
                        return "I encountered an error processing your request."
                elif tool_call.function.name == "pause_session":
                    args = json.loads(tool_call.function.arguments)
                    self.session_paused = True
                    self.paused_reason = args.get("reason", "No reason provided")

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Session paused successfully."})
                    })

                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or "Session paused."
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (pause_session): {e}")
                        return "I encountered an error processing your request."
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

                    # Get final conversational response after tool call
                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or "Form aborted."
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (abort_form): {e}")
                        return "I encountered an error processing your request."
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

                    # Get final conversational response after tool call
                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or "Handoff requested."
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (request_human_handoff): {e}")
                        return "I encountered an error processing your request."
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
                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or ""
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (fetch_autocomplete): {e}")
                        return "I encountered an error processing your request."
                elif tool_call.function.name == "get_current_datetime":
                    tool_content = datetime.datetime.now().isoformat()
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or ""
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (datetime): {e}")
                        return "I encountered an error processing your request."
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

                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or ""
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (download_and_parse_file): {e}")
                        return "I encountered an error processing your request."
                elif tool_call.function.name == "upload_file":
                    args = json.loads(tool_call.function.arguments)
                    url = args.get("url")
                    filepath = args.get("filepath")

                    if self.agent_client:
                        try:
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

                    try:
                        second_response = await self._call_llm(
                            messages=self.messages
                        )
                        final_msg = second_response.choices[0].message
                        logger.debug(f"LLM final response after tool call: {final_msg.content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": final_msg.content
                        })
                        return final_msg.content or ""
                    except Exception as e:
                        logger.error(f"Error during secondary LLM completion (upload_file): {e}")
                        return "I encountered an error processing your request."

        return response_message.content or ""

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
