from fastapi import APIRouter
from .endpoints.asr import router as asr_router
from .endpoints.monitor import router as monitor_router

api_router = APIRouter()

# ASR processing endpoints
api_router.include_router(asr_router, prefix="/asr", tags=["asr"])

# Monitor management endpoints
api_router.include_router(monitor_router, prefix="/monitor", tags=["monitor"])
