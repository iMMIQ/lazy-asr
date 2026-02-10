"""
Silero VAD provider implementation.

This module wraps the ONNXSileroVAD class into the VADProvider pattern.
"""

import numpy as np
import soundfile as sf
from typing import List, Dict, Any, Optional

from app.vad.base import VADProvider
from app.core.logger import get_logger
from app.utils.vad import ONNXSileroVAD, get_vad_model

logger = get_logger(__name__)


class SileroVADProvider(VADProvider):
    """
    VAD provider using Silero VAD model.

    Silero VAD is a high-quality voice activity detection model
    that uses ONNX Runtime for efficient CPU inference.
    """

    # Valid configuration keys for this provider
    VALID_CONFIG_KEYS = {
        "threshold",
        "min_speech_duration_ms",
        "min_silence_duration_ms",
    }

    def __init__(self, model_path: str | None = None):
        """
        Initialize the Silero VAD provider.

        Args:
            model_path: Optional path to a custom ONNX model file.
                If not provided, the default bundled model will be used.
        """
        super().__init__(
            name="silero",
            display_name="Silero VAD",
            description="High-quality voice activity detection using Silero model with ONNX Runtime"
        )
        self._model_path = model_path
        self._model: Optional[ONNXSileroVAD] = None

    def _get_model(self) -> ONNXSileroVAD:
        """
        Lazy-load the VAD model.

        Returns:
            The ONNXSileroVAD model instance.
        """
        if self._model is None:
            logger.info("Lazy-loading Silero VAD model...")
            if self._model_path is not None:
                self._model = ONNXSileroVAD(model_path=self._model_path)
                logger.info(f"Silero VAD model loaded from custom path: {self._model_path}")
            else:
                self._model = get_vad_model()
                logger.info("Silero VAD model loaded from default bundle")
        return self._model

    def process_audio(self, audio_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process audio file and detect speech segments.

        Args:
            audio_path: Path to the audio file to process
            config: Configuration options for VAD processing
                - threshold: Speech probability threshold (default: 0.5)
                - min_speech_duration_ms: Minimum speech duration in ms (default: 250)
                - min_silence_duration_ms: Minimum silence duration in ms (default: 100)

        Returns:
            List of speech segment dictionaries, each containing:
            - start: Start time in seconds
            - end: End time in seconds
            - duration: Duration of the segment in seconds
        """
        model = self._get_model()

        # Extract config values with defaults
        threshold = config.get("threshold", 0.5)
        min_speech_duration_ms = config.get("min_speech_duration_ms", 250)
        min_silence_duration_ms = config.get("min_silence_duration_ms", 100)

        # Load audio file using soundfile
        audio_data, sample_rate = sf.read(audio_path)

        # Convert to mono if needed (average channels)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Process audio with the model
        segments = model.process_audio(
            audio_data,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            return_seconds=True,
        )

        # Add duration to each segment
        for segment in segments:
            segment["duration"] = segment["end"] - segment["start"]

        return segments

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate VAD configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check for invalid keys
        for key in config.keys():
            if key not in self.VALID_CONFIG_KEYS:
                logger.warning(f"Invalid config key for Silero VAD: {key}")
                return False

        # Validate threshold range if provided
        if "threshold" in config:
            threshold = config["threshold"]
            if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
                logger.warning(f"Invalid threshold value: {threshold}")
                return False

        # Validate min_speech_duration_ms if provided
        if "min_speech_duration_ms" in config:
            ms = config["min_speech_duration_ms"]
            if not isinstance(ms, (int, float)) or ms < 0:
                logger.warning(f"Invalid min_speech_duration_ms value: {ms}")
                return False

        # Validate min_silence_duration_ms if provided
        if "min_silence_duration_ms" in config:
            ms = config["min_silence_duration_ms"]
            if not isinstance(ms, (int, float)) or ms < 0:
                logger.warning(f"Invalid min_silence_duration_ms value: {ms}")
                return False

        return True

    def reset(self):
        """Reset VAD internal state."""
        if self._model is not None:
            self._model.reset()
            logger.debug("Silero VAD model state reset")
