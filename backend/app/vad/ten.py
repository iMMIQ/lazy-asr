"""
TEN VAD provider implementation.

This module implements VAD using the native ten-vad Python package.
"""

from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import soundfile as sf

try:
    import ten_vad
    TEN_VAD_AVAILABLE = True
except ImportError:
    TEN_VAD_AVAILABLE = False

from app.vad.base import VADProvider
from app.core.logger import get_logger

logger = get_logger(__name__)


class TenVADProvider(VADProvider):
    """
    VAD provider using native TEN VAD library.

    The native ten_vad package provides proper VAD functionality using
    the TEN framework's compiled library.
    """

    # Model configuration
    SAMPLE_RATE = 16000

    # Valid hop_size values for TEN VAD
    VALID_HOP_SIZES = {160, 256}

    # Valid configuration keys for this provider
    VALID_CONFIG_KEYS = {
        "threshold",
        "min_speech_duration_ms",
        "min_silence_duration_ms",
        "max_speech_duration_s",
        "hop_size",
    }

    def __init__(self, hop_size: int = 256):
        """
        Initialize the TEN VAD provider.

        Args:
            hop_size: Hop size in samples for frame processing (default: 256).
                Must be 160 or 256.
        """
        super().__init__(
            name="ten",
            display_name="TEN VAD",
            description="Voice activity detection using TEN framework VAD model"
        )

        if not TEN_VAD_AVAILABLE:
            raise ImportError("ten_vad package is not available. Install it with: pip install ten-vad")

        self._hop_size = hop_size
        self._vad: Any = None
        self._threshold = 0.5

    def _get_vad(self, threshold: float = 0.5) -> Any:
        """
        Get or create TEN VAD instance.

        Args:
            threshold: Speech probability threshold.

        Returns:
            TEN VAD instance.
        """
        if self._vad is None or self._threshold != threshold:
            self._vad = ten_vad.TenVad(hop_size=self._hop_size, threshold=threshold)
            self._threshold = threshold
            logger.info("TEN VAD model loaded from native package")
        return self._vad

    def _compute_speech_probabilities(
        self,
        audio_data: np.ndarray,
        threshold: float = 0.5,
    ) -> np.ndarray:
        """
        Compute speech probabilities for audio frames.

        Args:
            audio_data: Audio samples as float32 array, normalized to [-1, 1].
            threshold: Speech probability threshold.

        Returns:
            Speech probabilities for each frame.
        """
        vad = self._get_vad(threshold)
        hop_size = self._hop_size
        num_samples = len(audio_data)

        # Calculate number of frames
        num_frames = (num_samples + hop_size - 1) // hop_size

        probabilities = []

        for i in range(num_frames):
            start = i * hop_size
            end = min(start + hop_size, num_samples)
            frame = audio_data[start:end]

            # Pad the last frame if needed
            if len(frame) < hop_size:
                frame = np.pad(frame, (0, hop_size - len(frame)), mode="constant")

            # Convert to int16 as required by TEN VAD
            frame_int16 = (frame * 32767).astype(np.int16)

            # Process frame
            prob, flag = vad.process(frame_int16)
            probabilities.append(prob)

        return np.array(probabilities)

    def _probs_to_segments(
        self,
        probabilities: np.ndarray,
        threshold: float,
        min_speech_duration_ms: float,
        min_silence_duration_ms: float,
    ) -> List[Dict[str, float]]:
        """
        Convert speech probabilities to speech segments.

        Args:
            probabilities: Speech probabilities per frame.
            threshold: Speech probability threshold.
            min_speech_duration_ms: Minimum speech duration in milliseconds.
            min_silence_duration_ms: Minimum silence duration in milliseconds.

        Returns:
            List of speech segment dictionaries with start, end, and duration.
        """
        hop_size_s = self._hop_size / self.SAMPLE_RATE  # Hop size in seconds
        min_speech_frames = max(1, int(min_speech_duration_ms / 1000 / hop_size_s))
        min_silence_frames = max(1, int(min_silence_duration_ms / 1000 / hop_size_s))

        # Convert to binary (speech/no-speech)
        is_speech = probabilities >= threshold

        segments = []
        in_speech = False
        start_idx = 0
        silence_count = 0
        speech_count = 0

        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                # Start of potential speech segment
                in_speech = True
                start_idx = i
                speech_count = 1
                silence_count = 0
            elif speech and in_speech:
                # Continuing speech
                speech_count += 1
                silence_count = 0
            elif not speech and in_speech:
                # Potential end of speech
                silence_count += 1
                if silence_count >= min_silence_frames:
                    # End of speech segment
                    if speech_count >= min_speech_frames:
                        # Valid speech segment
                        start_time = start_idx * hop_size_s
                        end_time = (i - silence_count + 1) * hop_size_s
                        duration = end_time - start_time

                        segments.append({
                            "start": start_time,
                            "end": end_time,
                            "duration": duration,
                        })

                    in_speech = False
                    speech_count = 0

        # Handle case where audio ends during speech
        if in_speech and speech_count >= min_speech_frames:
            start_time = start_idx * hop_size_s
            end_time = len(probabilities) * hop_size_s
            duration = end_time - start_time

            segments.append({
                "start": start_time,
                "end": end_time,
                "duration": duration,
            })

        return segments

    def process_audio(self, audio_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process audio file and detect speech segments.

        Args:
            audio_path: Path to the audio file to process
            config: Configuration options for VAD processing
                - threshold: Speech probability threshold (default: 0.5)
                - min_speech_duration_ms: Minimum speech duration in ms (default: 250)
                - min_silence_duration_ms: Minimum silence duration in ms (default: 100)
                - max_speech_duration_s: Maximum speech duration in seconds (default: 60)
                - hop_size: Hop size in samples (default: 256, must be 160 or 256)

        Returns:
            List of speech segment dictionaries, each containing:
            - start: Start time in seconds
            - end: End time in seconds
            - duration: Duration of the segment in seconds
        """
        # Extract config values with defaults
        threshold = config.get("threshold", 0.5)
        min_speech_duration_ms = config.get("min_speech_duration_ms", 250)
        min_silence_duration_ms = config.get("min_silence_duration_ms", 100)
        max_speech_duration_s = config.get("max_speech_duration_s", 60)
        hop_size = config.get("hop_size", self._hop_size)

        # Update hop_size if provided in config
        if hop_size != self._hop_size:
            self._hop_size = hop_size
            # Reset vad instance when hop_size changes
            self._vad = None

        # Load audio file using soundfile
        audio_data, sample_rate = sf.read(audio_path)

        # Resample to 16kHz if needed
        if sample_rate != self.SAMPLE_RATE:
            logger.debug(f"Resampling audio from {sample_rate}Hz to {self.SAMPLE_RATE}Hz")
            audio_data = self._resample(audio_data, sample_rate, self.SAMPLE_RATE)
            sample_rate = self.SAMPLE_RATE

        # Convert to mono if needed (average channels)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Ensure float32
        audio_data = audio_data.astype(np.float32)

        # Compute speech probabilities
        probabilities = self._compute_speech_probabilities(audio_data, threshold)

        # Convert probabilities to segments
        segments = self._probs_to_segments(
            probabilities,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
        )

        # Apply max_speech_duration_s constraint by splitting long segments
        if max_speech_duration_s > 0:
            segments = self._split_long_segments(segments, max_speech_duration_s)

        return segments

    def _split_long_segments(
        self,
        segments: List[Dict[str, float]],
        max_duration: float,
    ) -> List[Dict[str, float]]:
        """
        Split speech segments that exceed the maximum duration.

        Args:
            segments: List of speech segments.
            max_duration: Maximum duration in seconds.

        Returns:
            List of speech segments with long segments split.
        """
        result = []
        for segment in segments:
            duration = segment["duration"]
            if duration <= max_duration:
                result.append(segment)
            else:
                # Split into multiple segments
                start = segment["start"]
                remaining = duration
                while remaining > 0:
                    current_duration = min(remaining, max_duration)
                    result.append({
                        "start": start,
                        "end": start + current_duration,
                        "duration": current_duration,
                    })
                    start += current_duration
                    remaining -= current_duration

        return result

    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio from original sample rate to target sample rate.

        Args:
            audio: Input audio array.
            orig_sr: Original sample rate.
            target_sr: Target sample rate.

        Returns:
            Resampled audio array.
        """
        # Calculate ratio
        ratio = target_sr / orig_sr
        n_samples = int(len(audio) * ratio)

        # Use numpy for simple linear interpolation
        indices = np.linspace(0, len(audio) - 1, n_samples)
        return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

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
                logger.warning(f"Invalid config key for TEN VAD: {key}")
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

        # Validate max_speech_duration_s if provided
        if "max_speech_duration_s" in config:
            s = config["max_speech_duration_s"]
            if not isinstance(s, (int, float)) or s <= 0:
                logger.warning(f"Invalid max_speech_duration_s value: {s}")
                return False

        # Validate hop_size if provided
        if "hop_size" in config:
            hop_size = config["hop_size"]
            if not isinstance(hop_size, int) or hop_size not in self.VALID_HOP_SIZES:
                logger.warning(f"Invalid hop_size value: {hop_size}. Must be 160 or 256.")
                return False

        return True

    def reset(self):
        """Reset VAD internal state."""
        self._vad = None
        logger.debug("TEN VAD provider state reset")
