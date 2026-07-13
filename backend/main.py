import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import screens, data

app = FastAPI()

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
