"""
Voice Activity Detection (VAD) using ONNX Runtime.

This module provides a torch-free implementation of Silero VAD using ONNX Runtime.
"""
import os
import numpy as np
import onnxruntime as ort
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)


class ONNXSileroVAD:
    """
    Silero VAD using ONNX Runtime (CPU-only, no torch dependency).

    The ONNX model requires 3 inputs:
    - 'input': Audio chunk with context padding [batch, samples]
    - 'state': LSTM hidden state [2, 1, 128] (h and c states)
    - 'sr': Sample rate as int64 tensor [16000]

    Based on the C++ implementation from:
    https://github.com/snakers4/silero-vad/wiki/English.-Running-VAD-on-CPP
    """

    # Context window size (samples to keep from previous chunk)
    CONTEXT_SIZE = 64

    # LSTM state size
    STATE_SIZE = 2 * 1 * 128  # [2 layers, 1 batch, 128 hidden]

    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: int = 16000,
        window_size_samples: int = 512,
    ):
        """
        Initialize ONNX Silero VAD.

        Args:
            model_path: Path to ONNX model file. If None, will download from Hugging Face.
            sample_rate: Audio sample rate (default: 16000).
            window_size_samples: Window size for VAD processing (default: 512).
        """
        self.sample_rate = sample_rate
        self.window_size_samples = window_size_samples

        # Initialize model
        if model_path is None:
            model_path = self._download_model()

        self.model_path = model_path
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider'],
        )

        # Get input/output names
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

        # Initialize LSTM state (hidden and cell states)
        # Shape: [2, 1, 128] - 2 LSTM layers, batch size 1, 128 hidden units
        self._state = np.zeros((2, 1, 128), dtype=np.float32)

        # Sample rate as int64 tensor
        self._sr = np.array([sample_rate], dtype=np.int64)

        # Context buffer (keep last CONTEXT_SIZE samples for next chunk)
        self._context = np.zeros(self.CONTEXT_SIZE, dtype=np.float32)

        logger.info(f"ONNX Silero VAD initialized with model: {model_path}")
        logger.debug(f"Model inputs: {self.input_names}, outputs: {self.output_names}")

    def _download_model(self) -> str:
        """
        Download Silero VAD ONNX model from Hugging Face.

        Returns:
            Path to downloaded model.
        """
        import requests

        # Model cache directory
        cache_dir = Path.home() / ".cache" / "silero_vad_onnx"
        cache_dir.mkdir(parents=True, exist_ok=True)

        model_path = cache_dir / "silero_vad_v5.onnx"

        if model_path.exists():
            logger.info(f"Using cached ONNX model: {model_path}")
            return str(model_path)

        # Download from Hugging Face
        url = "https://huggingface.co/onnx-community/silero-vad/resolve/main/onnx/model.onnx"

        logger.info(f"Downloading Silero VAD ONNX model from {url}...")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            model_path.write_bytes(response.content)
            logger.info(f"Model downloaded to: {model_path}")
            return str(model_path)

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise

    def reset(self):
        """Reset VAD context and state."""
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros(self.CONTEXT_SIZE, dtype=np.float32)

    def _process_chunk(self, audio_chunk: np.ndarray) -> float:
        """
        Process a single audio chunk with context and return speech probability.

        The chunk is prepended with context from previous processing.

        Args:
            audio_chunk: Audio chunk as numpy array (shape: [window_size_samples]).

        Returns:
            Speech probability (0.0 to 1.0).
        """
        # Ensure correct shape and dtype
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # Pad with context from previous chunk
        # [context_samples (64) | current_window (512)]
        padded_chunk = np.concatenate([self._context, audio_chunk])
        padded_chunk = padded_chunk.reshape(1, -1)  # [1, samples]

        # Prepare inputs
        inputs = {
            'input': padded_chunk,
            'state': self._state,
            'sr': self._sr,
        }

        # Run inference
        # Outputs: [output_prob, new_state]
        outputs = self.session.run(self.output_names, inputs)

        # Get speech probability
        probability = float(outputs[0][0][0])

        # Update state for next chunk
        self._state = outputs[1]

        # Update context (keep last CONTEXT_SIZE samples from current chunk)
        self._context = audio_chunk[-self.CONTEXT_SIZE:].copy()

        return probability

    def process_audio(
        self,
        audio: np.ndarray,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        return_seconds: bool = True,
    ) -> List[Dict[str, float]]:
        """
        Process audio and return speech timestamps.

        Args:
            audio: Audio data as numpy array.
            threshold: Speech probability threshold (default: 0.5).
            min_speech_duration_ms: Minimum speech duration in ms (default: 250).
            min_silence_duration_ms: Minimum silence duration in ms (default: 100).
            return_seconds: Return timestamps in seconds (default: True).

        Returns:
            List of speech segments with 'start' and 'end' timestamps.
        """
        self.reset()

        # Convert to mono if needed
        if audio.ndim > 1:
            audio = np.mean(audio, axis=-1)

        # Resample if needed (simple implementation - assume correct sample rate)
        if len(audio) == 0:
            return []

        # Process in windows
        sample_rate = self.sample_rate
        window_size = self.window_size_samples
        hop_size = window_size  # Non-overlapping windows for simplicity

        num_windows = (len(audio) + hop_size - 1) // hop_size

        # Compute speech probabilities for each window
        probs = []
        for i in range(num_windows):
            start = i * hop_size
            end = min(start + window_size, len(audio))

            if end - start < window_size:
                # Pad last window
                chunk = np.pad(audio[start:end], (0, window_size - (end - start)))
            else:
                chunk = audio[start:end]

            prob = self._process_chunk(chunk)
            probs.append(prob)

        # Convert probabilities to speech timestamps
        return self._probs_to_timestamps(
            probs,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            sample_rate=sample_rate,
            window_size=window_size,
            return_seconds=return_seconds,
        )

    def _probs_to_timestamps(
        self,
        probs: List[float],
        threshold: float,
        min_speech_duration_ms: int,
        min_silence_duration_ms: int,
        sample_rate: int,
        window_size: int,
        return_seconds: bool,
    ) -> List[Dict[str, float]]:
        """
        Convert speech probabilities to timestamp segments.

        Args:
            probs: List of speech probabilities.
            threshold: Speech probability threshold.
            min_speech_duration_ms: Minimum speech duration in ms.
            min_silence_duration_ms: Minimum silence duration in ms.
            sample_rate: Audio sample rate.
            window_size: Window size in samples.
            return_seconds: Return timestamps in seconds.

        Returns:
            List of speech segments.
        """
        # Convert to binary (speech/no-speech)
        is_speech = [p >= threshold for p in probs]

        # Find speech segments
        segments = []
        in_speech = False
        start_idx = 0
        start_samples = 0

        # Convert durations to windows
        min_speech_windows = max(
            1,
            int(min_speech_duration_ms * sample_rate / 1000 / window_size)
        )
        min_silence_windows = max(
            1,
            int(min_silence_duration_ms * sample_rate / 1000 / window_size)
        )

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
                if silence_count >= min_silence_windows:
                    # End of speech segment
                    if speech_count >= min_speech_windows:
                        # Valid speech segment
                        start_time = start_idx * window_size / sample_rate
                        end_time = (i - silence_count + 1) * window_size / sample_rate

                        if return_seconds:
                            segments.append({'start': start_time, 'end': end_time})
                        else:
                            segments.append({
                                'start': int(start_idx * window_size),
                                'end': int((i - silence_count + 1) * window_size),
                            })

                    in_speech = False
                    speech_count = 0

        # Handle case where audio ends during speech
        if in_speech and speech_count >= min_speech_windows:
            start_time = start_idx * window_size / sample_rate
            end_time = len(probs) * window_size / sample_rate

            if return_seconds:
                segments.append({'start': start_time, 'end': end_time})
            else:
                segments.append({
                    'start': int(start_idx * window_size),
                    'end': int(len(probs) * window_size),
                })

        return segments


# Global VAD instance cache
_vad_instance: Optional[ONNXSileroVAD] = None


def get_vad_model() -> ONNXSileroVAD:
    """
    Get or create global VAD model instance.

    Returns:
        ONNXSileroVAD instance.
    """
    global _vad_instance
    if _vad_instance is None:
        _vad_instance = ONNXSileroVAD()
    return _vad_instance


def vad_segmentation(
    audio_path: str,
    threshold: float = 0.5,
    min_speech_duration_ms: int = 500,
    min_silence_duration_ms: int = 500,
) -> Tuple[List[Dict], Any, int]:
    """
    Perform speech activity detection and audio segmentation using ONNX Silero VAD.

    This function replaces silero_vad_segmentation for torch-free operation.

    Args:
        audio_path: Path to the audio file.
        threshold: Speech probability threshold (default: 0.5).
        min_speech_duration_ms: Minimum speech duration in ms (default: 500).
        min_silence_duration_ms: Minimum silence duration in ms (default: 500).

    Returns:
        Tuple of (speech_timestamps, audio_data, sample_rate).
    """
    import soundfile as sf

    logger.info("Loading audio file for VAD processing...")
    audio_data, sample_rate = sf.read(audio_path)

    # Get VAD model
    vad = get_vad_model()

    # Resample if needed (simple implementation - assumes 16kHz for best results)
    # For production, you'd want proper resampling here

    logger.info("Starting VAD speech detection...")
    speech_timestamps = vad.process_audio(
        audio_data,
        threshold=threshold,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
        return_seconds=True,
    )

    logger.info(f"VAD detection completed, found {len(speech_timestamps)} speech segments")

    return speech_timestamps, audio_data, sample_rate


# Compatibility layer - replace silero_vad imports
def load_silero_vad(onnx: bool = True):
    """Compatibility function for silero_vad module."""
    return get_vad_model()


def read_audio(audio_path: str) -> np.ndarray:
    """Compatibility function for silero_vad module."""
    import soundfile as sf
    audio, sr = sf.read(audio_path)
    # Convert to mono if needed
    if audio.ndim > 1:
        audio = np.mean(audio, axis=-1)
    # Resample to 16kHz if needed (simplified)
    if sr != 16000:
        # For production, implement proper resampling
        logger.warning(f"Audio sample rate is {sr}, expected 16000. Results may vary.")
    return audio


def get_speech_timestamps(
    audio: np.ndarray,
    model: ONNXSileroVAD,
    threshold: float = 0.5,
    min_speech_duration_ms: int = 250,
    min_silence_duration_ms: int = 100,
    return_seconds: bool = True,
    **kwargs
) -> List[Dict[str, float]]:
    """Compatibility function for silero_vad module."""
    return model.process_audio(
        audio,
        threshold=threshold,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
        return_seconds=return_seconds,
    )
