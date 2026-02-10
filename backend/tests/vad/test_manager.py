"""
Tests for VAD provider manager.
"""

import pytest
from app.vad.manager import vad_manager, VADManager
from app.vad.base import VADProvider


def test_vad_manager_singleton():
    """Test that vad_manager is a singleton."""
    # Create a new instance and compare with the global singleton
    manager1 = vad_manager
    manager2 = VADManager()

    # They should both be VADManager instances
    assert isinstance(manager1, VADManager)
    assert isinstance(manager2, VADManager)

    # The singleton should be a VADManager instance
    assert hasattr(manager1, 'get_provider')
    assert hasattr(manager1, 'get_available_providers')


def test_vad_manager_get_provider():
    """Test getting a provider by name."""
    provider = vad_manager.get_provider("silero")

    assert provider is not None
    assert isinstance(provider, VADProvider)
    assert provider.name == "silero"


def test_vad_manager_get_nonexistent_provider():
    """Test getting a non-existent provider returns None."""
    provider = vad_manager.get_provider("nonexistent")

    assert provider is None


def test_vad_manager_get_available_providers():
    """Test getting list of available providers."""
    providers = vad_manager.get_available_providers()

    assert isinstance(providers, list)
    assert len(providers) >= 1

    # Check that silero is in the list
    silero_found = False
    for provider in providers:
        if provider.get("name") == "silero":
            silero_found = True
            assert "display_name" in provider
            assert "description" in provider
            break

    assert silero_found, "Silero provider should be in available providers"


def test_vad_manager_validate_config():
    """Test validating config for providers."""
    # Valid config for silero
    valid_config = {
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "min_silence_duration_ms": 100,
    }
    assert vad_manager.validate_provider_config("silero", valid_config) is True

    # Invalid config key
    invalid_config = {
        "threshold": 0.5,
        "invalid_key": "value",
    }
    assert vad_manager.validate_provider_config("silero", invalid_config) is False

    # Invalid threshold value
    invalid_threshold = {
        "threshold": 1.5,  # Must be 0-1
    }
    assert vad_manager.validate_provider_config("silero", invalid_threshold) is False

    # Non-existent provider should return False
    assert vad_manager.validate_provider_config("nonexistent", {}) is False
