from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Any

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# In-memory store for webhook payloads
# Structure: { "webhook_id": [ payload1, payload2, ... ] }
webhook_store: Dict[str, List[Any]] = {}

@router.post("/{webhook_id}")
async def receive_webhook(webhook_id: str, request: Request):
    """
    Receive a webhook payload and store it in memory.
    """
    try:
        payload = await request.json()
    except Exception:
        # If the body is not JSON, we store it as text or raw bytes if needed
        # For simplicity, we just fallback to raw body text
        body = await request.body()
        payload = body.decode("utf-8") if body else ""

    if webhook_id not in webhook_store:
        webhook_store[webhook_id] = []

    webhook_store[webhook_id].append(payload)
    return {"status": "success", "message": f"Webhook {webhook_id} received."}

@router.get("/{webhook_id}")
async def get_webhook_payloads(webhook_id: str):
    """
    Retrieve all stored payloads for a given webhook_id.
    """
    if webhook_id not in webhook_store:
        return {"webhook_id": webhook_id, "payloads": []}

    return {"webhook_id": webhook_id, "payloads": webhook_store[webhook_id]}

@router.delete("/{webhook_id}")
async def clear_webhook_payloads(webhook_id: str):
    """
    Clear stored payloads for a given webhook_id.
    """
    if webhook_id in webhook_store:
        del webhook_store[webhook_id]
    return {"status": "success", "message": f"Webhook {webhook_id} cleared."}
