from fastapi import APIRouter

router = APIRouter()

@router.get("/api/health")
async def get_health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "cache": "connected",
            "message_queue": "connected"
        }
    }
