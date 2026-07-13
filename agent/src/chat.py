from src.client import AgentClient
import json
import datetime
from typing import List, Dict, Any, Callable, Awaitable
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

class ChatSession:
    def __init__(self, system_prompt: str, client: AsyncOpenAI = None, agent_client: AgentClient = None, model: str = "gpt-4o-mini"):
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
            }
        ]
        self.form_submitted = False
        self.submitted_data = None

    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and get a response from the LLM, potentially handling tool calls.
        """
        self.messages.append({"role": "user", "content": user_input})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

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
                    second_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages
                    )
                    final_msg = second_response.choices[0].message
                    self.messages.append({
                        "role": "assistant",
                        "content": final_msg.content
                    })
                    return final_msg.content or "Form submitted."
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
                    second_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages
                    )
                    final_msg = second_response.choices[0].message
                    self.messages.append({
                        "role": "assistant",
                        "content": final_msg.content
                    })
                    return final_msg.content or ""
                elif tool_call.function.name == "get_current_datetime":
                    tool_content = datetime.datetime.now().isoformat()
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                    second_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages
                    )
                    final_msg = second_response.choices[0].message
                    self.messages.append({
                        "role": "assistant",
                        "content": final_msg.content
                    })
                    return final_msg.content or ""

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

    while not session.form_submitted:
        user_text = await input_func()
        if user_text.lower() in ["exit", "quit"]:
            await output_func("Exiting chat.")
            break

        response_text = await session.process_user_input(user_text)
        await output_func(response_text)

    if session.form_submitted:
        await output_func(f"Form submission complete with data: {session.submitted_data}")
