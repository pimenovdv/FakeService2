import json
from typing import List, Dict, Any, Callable, Awaitable
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from src.client import AgentClient
from src.actions import fetch_autocomplete_options

class ChatSession:
    def __init__(self, system_prompt: str, client: AsyncOpenAI = None, model: str = "gpt-4o-mini", agent_client: AgentClient = None):
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
                    "name": "fetch_autocomplete_options",
                    "description": "Fetch autocomplete options for a specific field based on user query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "endpoint": {
                                "type": "string",
                                "description": "The API endpoint to query."
                            },
                            "query": {
                                "type": "string",
                                "description": "The search query from the user."
                            }
                        },
                        "required": ["endpoint", "query"]
                    }
                }
            }
        ]
        self.form_submitted = False
        self.submitted_data = None

    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and get a response from the LLM, potentially handling tool calls.
        """
        self.messages.append({"role": "user", "content": user_input})

        while True:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

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

            if not response_message.tool_calls:
                return response_message.content or ""

            # Handle tool calls
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "submit_form":
                    args = json.loads(tool_call.function.arguments)
                    self.form_submitted = True
                    self.submitted_data = args.get("answers", {})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"status": "success", "message": "Form submitted successfully."})
                    })
                elif tool_call.function.name == "fetch_autocomplete_options":
                    args = json.loads(tool_call.function.arguments)
                    endpoint = args.get("endpoint", "")
                    query = args.get("query", "")

                    if self.agent_client:
                        try:
                            result = await fetch_autocomplete_options(self.agent_client, endpoint, query)
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"status": "success", "data": result})
                            })
                        except Exception as e:
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"status": "error", "message": str(e)})
                            })
                    else:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"status": "error", "message": "AgentClient not configured"})
                        })

async def run_chat_loop(
    session: ChatSession,
    input_func: Callable[[], Awaitable[str]],
    output_func: Callable[[str], Awaitable[None]]
):
    """
    A simple CLI loop for the chat session.
    """
    await output_func("Agent initialized. What would you like to do?")

    while not session.form_submitted:
        user_text = await input_func()
        if user_text.lower() in ["exit", "quit"]:
            await output_func("Exiting chat.")
            break

        response_text = await session.process_user_input(user_text)
        await output_func(response_text)

    if session.form_submitted:
        await output_func(f"Form submission complete with data: {session.submitted_data}")
