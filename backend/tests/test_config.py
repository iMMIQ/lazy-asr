"""Tests for configuration settings."""
import pytest
from app.core.config import settings


def test_default_vad_method():
    """Test that DEFAULT_VAD_METHOD is set to 'ten'."""
    assert settings.DEFAULT_VAD_METHOD == "ten"


def test_available_vad_methods():
    """Test that AVAILABLE_VAD_METHODS contains 'silero' and 'ten'."""
    assert "silero" in settings.AVAILABLE_VAD_METHODS
    assert "ten" in settings.AVAILABLE_VAD_METHODS
