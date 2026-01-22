"""
Pytest configuration and fixtures for TDD
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

import pytest
from httpx import AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
async def client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing"""
    import wave
    import struct

    audio_path = os.path.join(temp_dir, "test_audio.wav")
    with wave.open(audio_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(16000)  # 16kHz sample rate

        # Write 1 second of silence
        silence = b"\x00\x00" * 16000
        wav_file.writeframes(silence)

    return audio_path


# Unit test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
