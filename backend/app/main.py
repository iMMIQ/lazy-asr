from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.api import api_router
from .core.logger import get_logger
from .core.database import init_database, close_database
from .services.monitor_service import monitor_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ASR Service...")

    # Initialize database
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Start monitor service
    try:
        await monitor_service.start()
        logger.info("Monitor service started successfully")
    except Exception as e:
        logger.warning(f"Failed to start monitor service: {e}")

    yield

    # Shutdown
    logger.info("Shutting down ASR Service...")

    # Stop monitor service
    try:
        await monitor_service.stop()
        logger.info("Monitor service stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping monitor service: {e}")

    # Close database connections
    try:
        await close_database()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

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


@app.get("/")
async def root():
    return {"message": "ASR Service API", "docs": "/docs"}
