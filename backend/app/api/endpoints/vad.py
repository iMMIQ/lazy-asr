"""
VAD Provider Info Endpoint.

Provides information about available VAD providers.
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.vad.manager import vad_manager

router = APIRouter()


@router.get("/providers")
async def get_vad_providers() -> Dict[str, Any]:
    """
    Get list of available VAD providers and the default provider.

    Returns:
        Dictionary with:
        - providers: List of available VAD provider information
        - default: Name of the default VAD provider
    """
    return {
        "providers": vad_manager.get_available_providers(),
        "default": "silero"
    }
