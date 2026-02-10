"""
Tests for TEN VAD provider.
"""

import numpy as np
import pytest
import soundfile as sf
import tempfile
import os
from app.vad.ten import TenVADProvider


def test_ten_provider_creation():
    """Test creating a TEN VAD provider instance."""
    provider = TenVADProvider()

    assert provider.name == "ten"
    assert "TEN" in provider.display_name
    assert provider.description is not None


def test_ten_provider_validate_config():
    """Test validate_config works for TEN provider."""
    provider = TenVADProvider()

    # Empty config should be valid (uses defaults)
    assert provider.validate_config({}) is True

    # Valid keys should be accepted
    assert provider.validate_config({"threshold": 0.5}) is True
    assert provider.validate_config({"min_speech_duration_ms": 250}) is True
    assert provider.validate_config({"min_silence_duration_ms": 100}) is True
    assert provider.validate_config({"max_speech_duration_s": 60}) is True
    assert provider.validate_config({
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "min_silence_duration_ms": 100,
    }) is True

    # Invalid threshold should be rejected
    assert provider.validate_config({"threshold": 1.5}) is False
    assert provider.validate_config({"threshold": -0.1}) is False

    # Invalid keys should be rejected
    assert provider.validate_config({"invalid_key": 123}) is False
    assert provider.validate_config({"threshold": 0.5, "bad_key": "value"}) is False


def test_ten_provider_process_audio_short():
    """Test process_audio with short silence audio."""
    provider = TenVADProvider()

    # Create 1 second of silence (zeros) at 16kHz
    audio = np.zeros(16000, dtype=np.float32)

    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        sf.write(tmp_path, audio, 16000)
        config = {}

        # Should return a list (may be empty or contain segments)
        result = provider.process_audio(tmp_path, config)

        assert isinstance(result, list)
        # All elements should be dictionaries with start/end keys
        for segment in result:
            assert "start" in segment
            assert "end" in segment
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_ten_provider_reset():
    """Test reset() method doesn't raise."""
    provider = TenVADProvider()

    # Should not raise any exception
    provider.reset()
