from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.api import api_router
from .api.websocket_endpoints import websocket_progress_endpoint

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware for HTTP requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Register WebSocket endpoint directly
@app.websocket(f"{settings.API_V1_STR}/asr/ws/progress/{{task_id}}")
async def websocket_endpoint(websocket, task_id: str):
    # Manual CORS handling for WebSocket connections
    # Check the origin header to allow connections from frontend
    origin = websocket.headers.get("origin")
    
    # Allow connections from common frontend development origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",  # Vite default
    ]
    
    # For development, accept all origins
    # In production, you should restrict this to specific origins
    if origin and any(allowed_origin in origin for allowed_origin in allowed_origins):
        await websocket_progress_endpoint(websocket, task_id)
    else:
        # Accept connection anyway for development
        await websocket_progress_endpoint(websocket, task_id)


@app.get("/")
async def root():
    return {"message": "ASR Service API", "docs": "/docs"}
