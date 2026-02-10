"""Tests for audio_processing module with VAD provider support."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.audio_processing import vad_segmentation_with_provider


@pytest.fixture
def sample_audio_file_with_speech(temp_dir: str) -> str:
    """Create a sample audio file with speech-like content for testing."""
    import soundfile as sf

    audio_path = os.path.join(temp_dir, "test_speech.wav")
    # Create 1 second of audio at 16kHz with some "speech-like" patterns
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Create a mix of frequencies to simulate speech-like audio
    audio_data = (
        0.3 * np.sin(2 * np.pi * 200 * t) +  # Base frequency
        0.2 * np.sin(2 * np.pi * 400 * t) +  # Harmonic
        0.1 * np.sin(2 * np.pi * 800 * t) +  # Higher harmonic
        0.05 * np.random.randn(len(t))  # Add some noise
    )
    sf.write(audio_path, audio_data, sample_rate)

    return audio_path


def test_vad_segmentation_with_silero(sample_audio_file_with_speech: str):
    """Test VAD segmentation with Silero provider."""
    from app.vad.manager import vad_manager

    # Ensure silero provider is available
    provider = vad_manager.get_provider("silero")
    assert provider is not None, "Silero provider should be available"

    # Test VAD segmentation with default options
    speech_timestamps, audio_data, sample_rate = vad_segmentation_with_provider(
        sample_audio_file_with_speech,
        provider_name="silero"
    )

    # Verify return types
    assert isinstance(speech_timestamps, list)
    assert isinstance(audio_data, np.ndarray)
    assert isinstance(sample_rate, int)
    assert sample_rate == 16000

    # Verify timestamps structure
    for timestamp in speech_timestamps:
        assert "start" in timestamp
        assert "end" in timestamp
        assert isinstance(timestamp["start"], (int, float))
        assert isinstance(timestamp["end"], (int, float))
        assert timestamp["start"] <= timestamp["end"]


def test_vad_segmentation_with_silero_custom_options(sample_audio_file_with_speech: str):
    """Test VAD segmentation with Silero provider using custom options."""
    # Test VAD segmentation with custom options
    custom_options = {
        "threshold": 0.6,
        "min_speech_duration_ms": 300,
        "min_silence_duration_ms": 400
    }

    speech_timestamps, audio_data, sample_rate = vad_segmentation_with_provider(
        sample_audio_file_with_speech,
        provider_name="silero",
        vad_options=custom_options
    )

    # Verify return types
    assert isinstance(speech_timestamps, list)
    assert isinstance(audio_data, np.ndarray)
    assert isinstance(sample_rate, int)


def test_vad_segmentation_with_invalid_provider(sample_audio_file_with_speech: str):
    """Test VAD segmentation with invalid provider raises ValueError."""
    with pytest.raises(ValueError, match="VAD provider 'invalid_provider' not found"):
        vad_segmentation_with_provider(
            sample_audio_file_with_speech,
            provider_name="invalid_provider"
        )


def test_vad_segmentation_with_ten(sample_audio_file_with_speech: str):
    """Test VAD segmentation with TEN provider (skip if not available)."""
    from app.vad.manager import vad_manager

    # Skip if TEN provider is not available
    provider = vad_manager.get_provider("ten")
    if provider is None:
        pytest.skip("TEN VAD provider not available")

    # Test VAD segmentation with TEN provider
    speech_timestamps, audio_data, sample_rate = vad_segmentation_with_provider(
        sample_audio_file_with_speech,
        provider_name="ten"
    )

    # Verify return types
    assert isinstance(speech_timestamps, list)
    assert isinstance(audio_data, np.ndarray)
    assert isinstance(sample_rate, int)

    # Verify timestamps structure
    for timestamp in speech_timestamps:
        assert "start" in timestamp
        assert "end" in timestamp
