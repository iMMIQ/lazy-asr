"""
Tests for VAD provider base class.
"""

import pytest
from typing import List, Dict, Any
from app.vad.base import VADProvider


class MockVADProvider(VADProvider):
    """Mock VAD provider for testing."""

    def __init__(self):
        super().__init__(
            name="mock_vad",
            display_name="Mock VAD",
            description="A mock VAD provider for testing"
        )

    def process_audio(self, audio_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process audio and return speech segments."""
        return [
            {"start": 0.0, "end": 1.5, "duration": 1.5},
            {"start": 2.0, "end": 3.5, "duration": 1.5},
        ]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate VAD configuration."""
        return True


def test_vad_provider_creation():
    """Test creating a VAD provider instance."""
    provider = MockVADProvider()

    assert provider.name == "mock_vad"
    assert provider.display_name == "Mock VAD"
    assert provider.description == "A mock VAD provider for testing"


def test_vad_provider_process_audio():
    """Test process_audio returns segments."""
    provider = MockVADProvider()
    segments = provider.process_audio("/path/to/audio.wav", {})

    assert len(segments) == 2
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 1.5
    assert segments[1]["start"] == 2.0
    assert segments[1]["end"] == 3.5


def test_vad_provider_validate_config():
    """Test validate_config works."""
    provider = MockVADProvider()

    assert provider.validate_config({}) is True
    assert provider.validate_config({"threshold": 0.5}) is True


def test_cannot_instantiate_base_class():
    """Test that the base VADProvider class cannot be instantiated."""
    with pytest.raises(TypeError):
        VADProvider("test", "Test", "Description")
