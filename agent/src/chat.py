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
                    "name": "extract_document",
                    "description": "Upload a local file (e.g. ID card or invoice) for document extraction.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "The local path to the file to upload and extract data from."
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Optional type of the document (e.g., 'id_card', 'invoice')."
                            }
                        },
                        "required": ["filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_crud_resources",
                    "description": "Manage generic CRUD resources. Action can be 'list', 'get', 'create', 'update', or 'delete'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["list", "get", "create", "update", "delete"],
                                "description": "The action to perform."
                            },
                            "resource_name": {
                                "type": "string",
                                "description": "The name of the resource (e.g. 'users', 'posts'). Required for all actions."
                            },
                            "item_id": {
                                "type": "string",
                                "description": "The ID of the item. Required for 'get', 'update', and 'delete'."
                            },
                            "item_data": {
                                "type": "object",
                                "description": "The data for the item. Required for 'create' and 'update'."
                            }
                        },
                        "required": ["action", "resource_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_background_tasks",
                    "description": "Manage background tasks. Action can be 'start' or 'get_status' (requires task_id).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["start", "get_status"],
                                "description": "The action to perform."
                            },
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to get status for (required for get_status)."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_email",
                    "description": "Manage emails (send, get_outbox, clear_outbox).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to perform: 'send' to send an email, 'get_outbox' to get the email outbox, 'clear_outbox' to clear the outbox."
                            },
                            "payload": {
                                "type": "object",
                                "description": "The payload for creating/sending an email. Required for 'send' action. Must contain 'to', 'subject', and 'body'."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_orders",
                    "description": "Manage orders. Action can be 'create' (requires items, customer_id), 'list', or 'get' (requires order_id).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "items": {"type": "array", "items": {"type": "object"}},
                            "customer_id": {"type": "string"},
                            "order_id": {"type": "string"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_invoices",
                    "description": "Manage invoices. Action can be 'create' (requires items, customer_id), 'list', 'get' (requires invoice_id), or 'pay' (requires invoice_id).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "items": {"type": "array", "items": {"type": "object"}},
                            "customer_id": {"type": "string"},
                            "invoice_id": {"type": "string"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_products",
                    "description": "Manage products. Action can be 'create' (requires name, price, stock; optional description), 'list', 'get' (requires product_id), 'update' (requires product_id, plus optional fields), or 'delete' (requires product_id).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "product_id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "price": {"type": "number"},
                            "stock": {"type": "integer"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_devices",
                    "description": "Manage devices (list, register, delete).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "create", "delete"],
                                "description": "The action to perform: 'get' to list all devices, 'create' to register a device, 'delete' to remove a device."
                            },
                            "device_id": {
                                "type": "string",
                                "description": "The ID of the device (required for delete)."
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the device (required for create)."
                            },
                            "type": {
                                "type": "string",
                                "description": "Type of the device (required for create)."
                            },
                            "os_version": {
                                "type": "string",
                                "description": "OS version of the device."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_user_tasks",
                    "description": "Manage user tasks (list, create, update, delete).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "create", "update", "delete"],
                                "description": "The action to perform: 'get' to list all user tasks, 'create' to create a task, 'update' to update a task, 'delete' to delete a task."
                            },
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task (required for update and delete)."
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the task (required for create)."
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the task."
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "Completion status of the task."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_tickets",
                    "description": "Manage support tickets (list, create, update).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "create", "update"],
                                "description": "The action to perform: 'get' to list all tickets, 'create' to create a ticket, 'update' to update a ticket's status."
                            },
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to update (required for update)."
                            },
                            "subject": {
                                "type": "string",
                                "description": "Subject of the ticket (required for create)."
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the issue (required for create)."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "ID of the user creating the ticket (required for create)."
                            },
                            "status": {
                                "type": "string",
                                "description": "New status for the ticket (required for update)."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_events",
                    "description": "Manage mock calendar events (list, create).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["list", "create"],
                                "description": "The action to perform: 'list' to get all events, 'create' to create a new event."
                            },
                            "title": {
                                "type": "string",
                                "description": "The title of the event (required for create)."
                            },
                            "description": {
                                "type": "string",
                                "description": "The description of the event."
                            },
                            "start_time": {
                                "type": "string",
                                "description": "The start time of the event in ISO format (required for create)."
                            },
                            "end_time": {
                                "type": "string",
                                "description": "The end time of the event in ISO format (required for create)."
                            },
                            "location": {
                                "type": "string",
                                "description": "The location of the event."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_payments",
                    "description": "Manage mock payments (process, get_status).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["process", "get_status"],
                                "description": "The action to perform: 'process' to create a payment, 'get_status' to fetch the status."
                            },
                            "payment_id": {
                                "type": "string",
                                "description": "The ID of the payment (required for get_status)."
                            },
                            "amount": {
                                "type": "number",
                                "description": "The amount to pay (required for process)."
                            },
                            "currency": {
                                "type": "string",
                                "description": "The currency of the payment (required for process)."
                            },
                            "payment_method": {
                                "type": "string",
                                "description": "The payment method (required for process)."
                            },
                            "description": {
                                "type": "string",
                                "description": "The description of the payment."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_subscriptions",
                    "description": "Manage mock user subscriptions (create, get, cancel).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["create", "get", "cancel"],
                                "description": "The action to perform: 'create' to create a subscription, 'get' to fetch, 'cancel' to cancel."
                            },
                            "subscription_id": {
                                "type": "string",
                                "description": "The ID of the subscription (required for get and cancel)."
                            },
                            "plan_id": {
                                "type": "string",
                                "description": "The ID of the subscription plan (required for create)."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user subscribing (required for create)."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_audit_logs",
                    "description": "Retrieve mock audit logs. Allows pagination via 'skip' and 'limit', and filtering by 'user_id' and 'action'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skip": {
                                "type": "integer",
                                "description": "Pagination offset."
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Pagination limit."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "Filter by user ID."
                            },
                            "action": {
                                "type": "string",
                                "description": "Filter by action type (e.g. login, create_user)."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_comments",
                    "description": "Manage user comments (get, create, delete).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "create", "delete"],
                                "description": "The action to perform: 'get' to list comments, 'create' to add a comment, 'delete' to remove a comment."
                            },
                            "entity_id": {
                                "type": "string",
                                "description": "The ID of the entity to manage comments for (required for 'get' and 'create')."
                            },
                            "comment_id": {
                                "type": "string",
                                "description": "The ID of the comment to delete (required for 'delete')."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user creating the comment (required for 'create')."
                            },
                            "text": {
                                "type": "string",
                                "description": "The content of the comment (required for 'create')."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_profile",
                    "description": "Manage user profile (get or put).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "put"],
                                "description": "The action to perform: 'get' to fetch profile, 'put' to update."
                            },
                            "profile": {
                                "type": "object",
                                "description": "The profile data to update (only used when action is 'put').",
                                "additionalProperties": True
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_notifications",
                    "description": "Manage user notifications (get, mark_read).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "mark_read"],
                                "description": "The action to perform: 'get' to list notifications, 'mark_read' to mark a notification as read."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "The user ID to filter notifications by (optional for 'get')."
                            },
                            "unread_only": {
                                "type": "boolean",
                                "description": "Filter to show only unread notifications (optional for 'get')."
                            },
                            "notification_id": {
                                "type": "string",
                                "description": "The ID of the notification to mark as read (required for 'mark_read')."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_settings",
                    "description": "Manage application settings (get or put).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "put"],
                                "description": "The action to perform: 'get' to fetch settings, 'put' to update settings."
                            },
                            "settings": {
                                "type": "object",
                                "description": "The settings to update (only used when action is 'put'). Possible fields: theme, notifications_enabled, language, timezone."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_features",
                    "description": "Manage feature flags (get, put, delete).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "put", "delete"],
                                "description": "The action to perform: 'get' to list all feature flags, 'put' to update a feature flag, 'delete' to remove a feature flag."
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "The name of the feature flag to update or delete (required for 'put' and 'delete')."
                            },
                            "enabled": {
                                "type": "boolean",
                                "description": "The state of the feature flag (only used when action is 'put')."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cache_interaction",
                    "description": "Interact with the key-value cache (get, set, delete).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "set", "delete"],
                                "description": "The cache action to perform."
                            },
                            "key": {
                                "type": "string",
                                "description": "The cache key."
                            },
                            "value": {
                                "type": "string",
                                "description": "The cache value (required for 'set')."
                            },
                            "ttl": {
                                "type": "integer",
                                "description": "Optional Time-To-Live in seconds (only for 'set')."
                            }
                        },
                        "required": ["action", "key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_webhook",
                    "description": "Retrieve stored webhook payloads for a given webhook_id.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "webhook_id": {
                                "type": "string",
                                "description": "The ID of the webhook to retrieve."
                            }
                        },
                        "required": ["webhook_id"]
                    }
                }
            },
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
                    "description": "Get the current mock weather for a given city.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city to get the weather for."
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_analytics_data",
                    "description": "Retrieve mock analytics data. Allows filtering by start_date, end_date (YYYY-MM-DD) and metric (e.g. visitors, revenue, errors).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format"
                            },
                            "metric": {
                                "type": "string",
                                "description": "Metric to retrieve, defaults to visitors"
                            }
                        },
                        "required": []
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
                    "name": "search_system",
                    "description": "Search the system for users, pages, or documents using a query string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string."
                            }
                        },
                        "required": ["query"]
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


                elif tool_call.function.name == "manage_background_tasks":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")
                    if action == "start":
                        try:
                            resp = await self.agent_client.post("/api/tasks")
                            mock_task_res = resp.json()
                            tool_result = json.dumps(mock_task_res)
                        except Exception as e:
                            tool_result = json.dumps({"error": str(e)})
                    elif action == "get_status":
                        task_id = args.get("task_id")
                        if not task_id:
                            tool_result = json.dumps({"error": "task_id required for get_status action"})
                        else:
                            try:
                                resp = await self.agent_client.get(f"/api/tasks/{task_id}")
                                mock_status_res = resp.json()
                                tool_result = json.dumps(mock_status_res)
                            except Exception as e:
                                tool_result = json.dumps({"error": str(e)})
                    else:
                        tool_result = json.dumps({"error": "Invalid action"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result
                    })

                elif tool_call.function.name == "manage_crud_resources":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")
                    resource_name = args.get("resource_name")
                    item_id = args.get("item_id")
                    item_data = args.get("item_data", {})

                    if not resource_name:
                        tool_result = json.dumps({"error": "resource_name is required"})
                    else:
                        base_url = f"/api/resource/{resource_name}"
                        try:
                            if action == "list":
                                resp = await self.agent_client.get(base_url)
                                tool_result = json.dumps(resp.json())
                            elif action == "get":
                                if not item_id:
                                    tool_result = json.dumps({"error": "item_id required for get"})
                                else:
                                    resp = await self.agent_client.get(f"{base_url}/{item_id}")
                                    tool_result = json.dumps(resp.json())
                            elif action == "create":
                                resp = await self.agent_client.post(base_url, json=item_data)
                                tool_result = json.dumps(resp.json())
                            elif action == "update":
                                if not item_id:
                                    tool_result = json.dumps({"error": "item_id required for update"})
                                else:
                                    resp = await self.agent_client.put(f"{base_url}/{item_id}", json=item_data)
                                    tool_result = json.dumps(resp.json())
                            elif action == "delete":
                                if not item_id:
                                    tool_result = json.dumps({"error": "item_id required for delete"})
                                else:
                                    resp = await self.agent_client.delete(f"{base_url}/{item_id}")
                                    tool_result = json.dumps({"status": "success", "message": f"Deleted item {item_id}"})
                            else:
                                tool_result = json.dumps({"error": f"Invalid action {action}"})
                        except Exception as e:
                            tool_result = json.dumps({"error": str(e)})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result
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

                elif tool_call.function.name == "get_webhook":
                    args = json.loads(tool_call.function.arguments)
                    webhook_id = args.get("webhook_id")

                    if self.agent_client:
                        url = f"/api/webhooks/{webhook_id}"
                        try:
                            res = await self.agent_client.get(url)
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to fetch webhook, status code {res.status_code}"})
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
                    city = args.get("city")

                    if self.agent_client:
                        try:
                            import urllib.parse
                            encoded_city = urllib.parse.quote(city) if city else ""
                            url = f"/api/weather?city={encoded_city}"
                            res = await self.agent_client.get(url)
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to get weather, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": f"HTTP request failed: {str(e)}"})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "cache_interaction":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")
                    key = args.get("key")
                    value = args.get("value")
                    ttl = args.get("ttl")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get(f"/api/cache/{key}")
                                tool_content = json.dumps(res.json())
                            elif action == "set":
                                url = f"/api/cache/{key}"
                                if ttl is not None:
                                    url += f"?ttl={ttl}"
                                res = await self.agent_client.post(url, content=value)
                                tool_content = json.dumps(res.json())
                            elif action == "delete":
                                res = await self.agent_client.delete(f"/api/cache/{key}")
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            # Typically if it's a 404 from httpx we'd catch an HTTPStatusError and get JSON,
                            # but for simplicity, we capture the exception
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

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

                    if self.agent_client:
                        try:
                            payload = {
                                "text": text,
                                "target_language": target_language
                            }
                            if source_language:
                                payload["source_language"] = source_language

                            res = await self.agent_client.post("/api/translate", json=payload)

                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Backend returned status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        # Fallback mock logic if no agent_client
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

                elif tool_call.function.name == "get_analytics_data":
                    args = json.loads(tool_call.function.arguments)
                    start_date = args.get("start_date")
                    end_date = args.get("end_date")
                    metric = args.get("metric")

                    if self.agent_client:
                        query_params = []
                        if start_date:
                            query_params.append(f"start_date={start_date}")
                        if end_date:
                            query_params.append(f"end_date={end_date}")
                        if metric:
                            query_params.append(f"metric={metric}")

                        url = "/api/analytics"
                        if query_params:
                            url += "?" + "&".join(query_params)

                        try:
                            res = await self.agent_client.get(url)
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to fetch analytics, status code {res.status_code}"})
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

                elif tool_call.function.name == "manage_profile":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get("/api/profile")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get profile, status code {res.status_code}"})
                            elif action == "put":
                                profile_data = args.get("profile", {})
                                res = await self.agent_client.put("/api/profile", json=profile_data)
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to update profile, status code {res.status_code}"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_settings":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get("/api/settings")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get settings, status code {res.status_code}"})
                            elif action == "put":
                                settings_data = args.get("settings", {})
                                res = await self.agent_client.put("/api/settings", json=settings_data)
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to update settings, status code {res.status_code}"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "get_audit_logs":
                    args = json.loads(tool_call.function.arguments)
                    skip = args.get("skip")
                    limit = args.get("limit")
                    user_id = args.get("user_id")
                    action = args.get("action")

                    if self.agent_client:
                        query_params = []
                        if skip is not None:
                            query_params.append(f"skip={skip}")
                        if limit is not None:
                            query_params.append(f"limit={limit}")
                        if user_id:
                            query_params.append(f"user_id={user_id}")
                        if action:
                            query_params.append(f"action={action}")

                        url = "/api/audit-logs"
                        if query_params:
                            url += "?" + "&".join(query_params)

                        try:
                            res = await self.agent_client.get(url)
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to get audit logs, status code {res.status_code}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": f"HTTP request failed: {str(e)}"})
                    else:
                        tool_content = json.dumps({"error": "No agent_client available"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_email":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")
                    payload = args.get("payload", {})

                    if self.agent_client:
                        try:
                            if action == "send":
                                res = await self.agent_client.post("/api/email/send", json=payload)
                                if res.status_code in (200, 201):
                                    tool_content = f"Email sent successfully: {res.text}"
                                else:
                                    tool_content = f"Failed to send email: {res.text}"
                            elif action == "get_outbox":
                                res = await self.agent_client.get("/api/email/outbox")
                                if res.status_code == 200:
                                    tool_content = f"Email outbox: {res.text}"
                                else:
                                    tool_content = f"Failed to get email outbox: {res.text}"
                            elif action == "clear_outbox":
                                res = await self.agent_client.delete("/api/email/outbox")
                                if res.status_code in (200, 204):
                                    tool_content = "Email outbox cleared successfully."
                                else:
                                    tool_content = f"Failed to clear email outbox: {res.text}"
                            else:
                                tool_content = f"Unknown manage_email action: {action}"
                        except Exception as e:
                            tool_content = f"Error managing email: {e}"
                    else:
                        tool_content = "No API client available to manage emails."

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_orders":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "list":
                                res = await self.agent_client.get("/api/orders")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get orders, status code {res.status_code}"})
                            elif action == "get":
                                order_id = args.get("order_id")
                                if order_id:
                                    res = await self.agent_client.get(f"/api/orders/{order_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get order, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "order_id is required for get action"})
                            elif action == "create":
                                items = args.get("items")
                                customer_id = args.get("customer_id")
                                if items and customer_id:
                                    res = await self.agent_client.post("/api/orders", json={"items": items, "customer_id": customer_id})
                                    if res.status_code in (200, 201):
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create order, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "items and customer_id are required for create action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No API client available"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_invoices":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "list":
                                res = await self.agent_client.get("/api/invoices")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get invoices, status code {res.status_code}"})
                            elif action == "get":
                                invoice_id = args.get("invoice_id")
                                if invoice_id:
                                    res = await self.agent_client.get(f"/api/invoices/{invoice_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get invoice, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "invoice_id is required for get action"})
                            elif action == "create":
                                items = args.get("items")
                                customer_id = args.get("customer_id")
                                if items and customer_id:
                                    res = await self.agent_client.post("/api/invoices", json={"items": items, "customer_id": customer_id})
                                    if res.status_code in (200, 201):
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create invoice, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "items and customer_id are required for create action"})
                            elif action == "pay":
                                invoice_id = args.get("invoice_id")
                                if invoice_id:
                                    res = await self.agent_client.patch(f"/api/invoices/{invoice_id}/pay")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to pay invoice, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "invoice_id is required for pay action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No API client available"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_products":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "list":
                                res = await self.agent_client.get("/api/products")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get products, status code {res.status_code}"})
                            elif action == "get":
                                product_id = args.get("product_id")
                                if product_id:
                                    res = await self.agent_client.get(f"/api/products/{product_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get product, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "product_id is required for get action"})
                            elif action == "create":
                                name = args.get("name")
                                price = args.get("price")
                                stock = args.get("stock")
                                description = args.get("description")
                                if name is not None and price is not None and stock is not None:
                                    payload = {"name": name, "price": price, "stock": stock}
                                    if description is not None:
                                        payload["description"] = description
                                    res = await self.agent_client.post("/api/products", json=payload)
                                    if res.status_code in (200, 201):
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create product, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "name, price, and stock are required for create action"})
                            elif action == "update":
                                product_id = args.get("product_id")
                                if product_id:
                                    payload = {}
                                    if "name" in args: payload["name"] = args["name"]
                                    if "description" in args: payload["description"] = args["description"]
                                    if "price" in args: payload["price"] = args["price"]
                                    if "stock" in args: payload["stock"] = args["stock"]
                                    res = await self.agent_client.put(f"/api/products/{product_id}", json=payload)
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to update product, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "product_id is required for update action"})
                            elif action == "delete":
                                product_id = args.get("product_id")
                                if product_id:
                                    res = await self.agent_client.delete(f"/api/products/{product_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to delete product, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "product_id is required for delete action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No API client available"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_devices":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get("/api/devices")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = f"Failed to list devices: {res.text}"
                            elif action == "create":
                                payload = {}
                                if "name" in args:
                                    payload["name"] = args["name"]
                                if "type" in args:
                                    payload["type"] = args["type"]
                                if "os_version" in args:
                                    payload["os_version"] = args["os_version"]
                                res = await self.agent_client.post("/api/devices", json=payload)
                                if res.status_code == 200:
                                    tool_content = f"Device registered: {res.json()}"
                                else:
                                    tool_content = f"Failed to register device: {res.text}"
                            elif action == "delete":
                                device_id = args.get("device_id")
                                if device_id:
                                    res = await self.agent_client.delete(f"/api/devices/{device_id}")
                                    if res.status_code == 200:
                                        tool_content = f"Device deleted: {res.json()}"
                                    else:
                                        tool_content = f"Failed to delete device: {res.text}"
                                else:
                                    tool_content = "device_id is required to delete a device."
                        except Exception as e:
                            tool_content = f"Error managing devices: {str(e)}"
                    else:
                        tool_content = "Agent client not available."

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_user_tasks":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                params = {}
                                if "completed" in args:
                                    params["completed"] = "true" if args["completed"] else "false"
                                res = await self.agent_client.get("/api/user-tasks", params=params)
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = f"Failed to list user tasks: {res.text}"
                            elif action == "create":
                                payload = {}
                                if "title" in args:
                                    payload["title"] = args["title"]
                                if "description" in args:
                                    payload["description"] = args["description"]
                                if "completed" in args:
                                    payload["completed"] = args["completed"]
                                res = await self.agent_client.post("/api/user-tasks", json=payload)
                                if res.status_code == 200:
                                    tool_content = f"Task created: {res.json()}"
                                else:
                                    tool_content = f"Failed to create user task: {res.text}"
                            elif action == "update":
                                task_id = args.get("task_id")
                                if task_id:
                                    payload = {}
                                    if "title" in args:
                                        payload["title"] = args["title"]
                                    if "description" in args:
                                        payload["description"] = args["description"]
                                    if "completed" in args:
                                        payload["completed"] = args["completed"]
                                    res = await self.agent_client.patch(f"/api/user-tasks/{task_id}", json=payload)
                                    if res.status_code == 200:
                                        tool_content = f"Task updated: {res.json()}"
                                    else:
                                        tool_content = f"Failed to update task: {res.text}"
                                else:
                                    tool_content = "task_id is required to update a user task."
                            elif action == "delete":
                                task_id = args.get("task_id")
                                if task_id:
                                    res = await self.agent_client.delete(f"/api/user-tasks/{task_id}")
                                    if res.status_code == 200:
                                        tool_content = f"Task deleted: {res.json()}"
                                    else:
                                        tool_content = f"Failed to delete task: {res.text}"
                                else:
                                    tool_content = "task_id is required to delete a user task."
                            else:
                                tool_content = f"Unknown action: {action}"
                        except Exception as e:
                            tool_content = f"Error managing user tasks: {e}"
                    else:
                        tool_content = "Agent client not configured."

                elif tool_call.function.name == "manage_tickets":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get("/api/tickets")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get tickets, status code {res.status_code}"})
                            elif action == "create":
                                subject = args.get("subject")
                                description = args.get("description")
                                user_id = args.get("user_id")
                                if subject and description and user_id:
                                    res = await self.agent_client.post("/api/tickets", json={"subject": subject, "description": description, "user_id": user_id})
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create ticket, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "subject, description, and user_id are required for create action"})
                            elif action == "update":
                                ticket_id = args.get("ticket_id")
                                status = args.get("status")
                                if ticket_id and status:
                                    res = await self.agent_client.patch(f"/api/tickets/{ticket_id}", json={"status": status})
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to update ticket, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "ticket_id and status are required for update action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_events":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "list":
                                res = await self.agent_client.get("/api/events")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to list events, status code {res.status_code}"})
                            elif action == "create":
                                payload = {k: v for k, v in args.items() if k in ["title", "description", "start_time", "end_time", "location"] and v is not None}
                                if "title" in payload and "start_time" in payload and "end_time" in payload:
                                    res = await self.agent_client.post("/api/events", json=payload)
                                    if res.status_code == 201:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create event, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "title, start_time, and end_time are required to create an event"})
                            else:
                                tool_content = json.dumps({"error": "Unknown action"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "agent_client not initialized"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_payments":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "process":
                                payload = {k: v for k, v in args.items() if k in ["amount", "currency", "payment_method", "description"] and v is not None}
                                if "amount" in payload and "currency" in payload and "payment_method" in payload:
                                    res = await self.agent_client.post("/api/payments", json=payload)
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to process payment, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "amount, currency, and payment_method are required to process a payment"})
                            elif action == "get_status":
                                payment_id = args.get("payment_id")
                                if payment_id:
                                    res = await self.agent_client.get(f"/api/payments/{payment_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    elif res.status_code == 404:
                                        tool_content = json.dumps({"error": "Payment not found"})
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get payment status, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "payment_id is required to get payment status"})
                            else:
                                tool_content = json.dumps({"error": "Unknown action"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "agent_client not initialized"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_subscriptions":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "create":
                                plan_id = args.get("plan_id")
                                user_id = args.get("user_id")
                                if plan_id and user_id:
                                    res = await self.agent_client.post("/api/subscriptions", json={"plan_id": plan_id, "user_id": user_id})
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create subscription, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "plan_id and user_id are required for create action"})
                            elif action == "get":
                                subscription_id = args.get("subscription_id")
                                if subscription_id:
                                    res = await self.agent_client.get(f"/api/subscriptions/{subscription_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get subscription, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "subscription_id is required for get action"})
                            elif action == "cancel":
                                subscription_id = args.get("subscription_id")
                                if subscription_id:
                                    res = await self.agent_client.delete(f"/api/subscriptions/{subscription_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to cancel subscription, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "subscription_id is required for cancel action"})
                            else:
                                tool_content = json.dumps({"error": f"Unknown action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent_client available"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_comments":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                entity_id = args.get("entity_id")
                                if entity_id:
                                    res = await self.agent_client.get(f"/api/comments/{entity_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to get comments, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "entity_id is required for get action"})
                            elif action == "create":
                                entity_id = args.get("entity_id")
                                user_id = args.get("user_id")
                                text = args.get("text")
                                if entity_id and user_id and text:
                                    res = await self.agent_client.post(f"/api/comments/{entity_id}", json={"user_id": user_id, "text": text})
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to create comment, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "entity_id, user_id, and text are required for create action"})
                            elif action == "delete":
                                comment_id = args.get("comment_id")
                                if comment_id:
                                    res = await self.agent_client.delete(f"/api/comments/{comment_id}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to delete comment, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "comment_id is required for delete action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_notifications":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                params = {}
                                user_id = args.get("user_id")
                                unread_only = args.get("unread_only")
                                if user_id is not None:
                                    params["user_id"] = user_id
                                if unread_only is not None:
                                    params["unread_only"] = str(unread_only).lower()

                                res = await self.agent_client.get("/api/notifications", params=params)
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get notifications, status code {res.status_code}"})
                            elif action == "mark_read":
                                notification_id = args.get("notification_id")
                                if notification_id:
                                    res = await self.agent_client.put(f"/api/notifications/{notification_id}/read")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to mark notification as read, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "notification_id is required for mark_read action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "manage_features":
                    args = json.loads(tool_call.function.arguments)
                    action = args.get("action")

                    if self.agent_client:
                        try:
                            if action == "get":
                                res = await self.agent_client.get("/api/features")
                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to get features, status code {res.status_code}"})
                            elif action == "put":
                                feature_name = args.get("feature_name")
                                enabled = args.get("enabled", False)
                                if feature_name:
                                    res = await self.agent_client.put(f"/api/features/{feature_name}", json={"enabled": enabled})
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to update feature, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "feature_name is required for put action"})
                            elif action == "delete":
                                feature_name = args.get("feature_name")
                                if feature_name:
                                    res = await self.agent_client.delete(f"/api/features/{feature_name}")
                                    if res.status_code == 200:
                                        tool_content = json.dumps(res.json())
                                    else:
                                        tool_content = json.dumps({"error": f"Failed to delete feature, status code {res.status_code}"})
                                else:
                                    tool_content = json.dumps({"error": "feature_name is required for delete action"})
                            else:
                                tool_content = json.dumps({"error": f"Invalid action: {action}"})
                        except Exception as e:
                            tool_content = json.dumps({"error": str(e)})
                    else:
                        tool_content = json.dumps({"error": "No agent client configured."})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content
                    })

                elif tool_call.function.name == "extract_document":
                    args = json.loads(tool_call.function.arguments)
                    filepath = args.get("filepath")
                    document_type = args.get("document_type")

                    if self.agent_client:
                        try:
                            if os.path.exists(filepath):
                                filename = os.path.basename(filepath)
                                mime_type, _ = mimetypes.guess_type(filepath)
                                if not mime_type:
                                    mime_type = "application/octet-stream"

                                with open(filepath, "rb") as f:
                                    files = {"file": (filename, f, mime_type)}
                                    data = {}
                                    if document_type:
                                        data["document_type"] = document_type

                                    res = await self.agent_client.post("/api/extract", files=files, data=data)

                                if res.status_code == 200:
                                    tool_content = json.dumps(res.json())
                                else:
                                    tool_content = json.dumps({"error": f"Failed to extract document, status code {res.status_code}", "response": res.text})
                            else:
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

                elif tool_call.function.name == "search_system":
                    args = json.loads(tool_call.function.arguments)
                    query = args.get("query")

                    if self.agent_client:
                        try:
                            # Use query params for the search
                            res = await self.agent_client.get(f"/api/search?q={query}")
                            if res.status_code == 200:
                                tool_content = json.dumps(res.json())
                            else:
                                tool_content = json.dumps({"error": f"Failed to perform search, status code {res.status_code}"})
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
