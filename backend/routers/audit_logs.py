from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime, timedelta
import random
import uuid

router = APIRouter()

# Generate some mock data
ACTIONS = ["login", "logout", "create_user", "update_profile", "delete_file", "upload_file"]
USERS = ["user_123", "admin_01", "user_456", "system"]

def generate_mock_logs(count=100):
    logs = []
    base_time = datetime.utcnow()
    for i in range(count):
        log_time = base_time - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        logs.append({
            "id": str(uuid.uuid4()),
            "timestamp": log_time.isoformat() + "Z",
            "user_id": random.choice(USERS),
            "action": random.choice(ACTIONS),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "details": f"Action {random.choice(ACTIONS)} executed successfully"
        })
    # Sort by timestamp descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return logs

MOCK_LOGS = generate_mock_logs(200)

@router.get("/api/audit-logs", summary="Get Mock Audit Logs")
async def get_audit_logs(
    skip: int = Query(0, description="Pagination offset"),
    limit: int = Query(10, description="Pagination limit"),
    user_id: Optional[str] = Query(None, description="Filter by user_id"),
    action: Optional[str] = Query(None, description="Filter by action")
):
    filtered_logs = MOCK_LOGS

    if user_id:
        filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]

    if action:
        filtered_logs = [log for log in filtered_logs if log["action"] == action]

    total = len(filtered_logs)
    paginated_logs = filtered_logs[skip : skip + limit]

    return {
        "items": paginated_logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }
