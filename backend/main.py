import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from fastapi.responses import JSONResponse
from routers import screens, data, upload, auth, crud, tasks, download, health, websocket, stream, graphql, webhooks, cache, email, features, extract, analytics, audit_logs, notifications

app = FastAPI()

class RateLimiter:
    def __init__(self):
        self.clients = {}

    def is_allowed(self, client_ip: str, limit: int, window: int) -> bool:
        now = time.time()
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        # Remove timestamps outside the current window
        self.clients[client_ip] = [t for t in self.clients[client_ip] if now - t < window]
        if len(self.clients[client_ip]) >= limit:
            return False
        self.clients[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    limit_str = request.headers.get("x-mock-rate-limit")
    if limit_str and limit_str.isdigit():
        limit = int(limit_str)
        client_ip = request.client.host if request.client else "unknown"
        # Using a fixed 60-second window for the mock rate limiter
        if not rate_limiter.is_allowed(client_ip, limit, window=60):
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    return await call_next(request)

@app.middleware("http")
async def mock_testing_middleware(request: Request, call_next):
    # Simulate errors if header is present
    error_code = request.headers.get("x-mock-error-code")
    if error_code:
        try:
            status_code = int(error_code)
            return JSONResponse(status_code=status_code, content={"detail": f"Mock error: {status_code}"})
        except ValueError:
            pass # Ignore invalid format

    # Simulate delays if header is present
    delay_ms = request.headers.get("x-mock-delay-ms")
    if delay_ms:
        try:
            delay_seconds = int(delay_ms) / 1000.0
            await asyncio.sleep(delay_seconds)
        except ValueError:
            pass # Ignore invalid format

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"status": "ok"}

app.include_router(screens.router)
app.include_router(data.router)
app.include_router(upload.router)
app.include_router(auth.router)
app.include_router(crud.router)
app.include_router(tasks.router)
app.include_router(download.router)
app.include_router(health.router)
app.include_router(websocket.router)
app.include_router(stream.router)
app.include_router(graphql.router)
app.include_router(webhooks.router)
app.include_router(cache.router)
app.include_router(email.router)
app.include_router(features.router)
app.include_router(extract.router)
app.include_router(analytics.router)
app.include_router(audit_logs.router)
app.include_router(notifications.router)
