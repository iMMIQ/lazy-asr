"""
VAD (Voice Activity Detection) providers.

This module contains the base class and implementations for various
Voice Activity Detection providers that can be used to segment audio
before ASR processing.
"""

from app.vad.base import VADProvider
from app.vad.silero import SileroVADProvider
from app.vad.ten import TenVADProvider
from app.vad.manager import vad_manager, VADManager

__all__ = [
    "vad_manager",
    "VADManager",
    "VADProvider",
    "SileroVADProvider",
    "TenVADProvider",
]
