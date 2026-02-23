from fastapi import APIRouter
from .endpoints.asr import router as asr_router
from .endpoints.websocket import router as websocket_router
from .endpoints.vad import router as vad_router

api_router = APIRouter()

# ASR processing endpoints
api_router.include_router(asr_router, prefix="/asr", tags=["asr"])

# WebSocket endpoints for real-time updates
api_router.include_router(websocket_router, tags=["websocket"])

# VAD provider info endpoints
api_router.include_router(vad_router, prefix="/vad", tags=["vad"])
