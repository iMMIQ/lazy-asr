from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .core.config import settings
from .api.api import api_router
from .core.logger import get_logger
import os

logger = get_logger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files from frontend build directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount the static files directory that contains CSS, JS, etc.
    static_files_dir = os.path.join(static_dir, "static")
    if os.path.exists(static_files_dir):
        app.mount("/static", StaticFiles(directory=static_files_dir), name="static")
        logger.info(f"Static files mounted from {static_files_dir}")
    else:
        logger.warning(f"Static files directory {static_files_dir} not found")
else:
    logger.warning(f"Static directory {static_dir} not found, frontend will not be served")


@app.get("/")
async def root():
    """Serve React frontend index.html"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ASR Service API", "docs": "/docs"}


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route for React Router"""
    # If the path is an API route, let it through
    if full_path.startswith(settings.API_V1_STR.lstrip("/")):
        return {"detail": "Not Found"}
    
    # Otherwise serve the React app
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}
