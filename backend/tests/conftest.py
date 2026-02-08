"""
Pytest configuration and fixtures for TDD
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import aiosqlite
import pytest
from httpx import AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_audio_file(temp_dir: str) -> str:
    """Create a sample audio file for testing"""
    import wave

    audio_path = os.path.join(temp_dir, "test_audio.wav")
    with wave.open(audio_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(16000)  # 16kHz sample rate

        # Write 1 second of silence
        silence = b"\x00\x00" * 16000
        wav_file.writeframes(silence)

    return audio_path


@pytest.fixture
async def test_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Create an in-memory SQLite database for testing.

    This fixture provides a clean database for each test function.
    Use it for integration tests that need database isolation.
    """
    async with aiosqlite.connect(":memory:") as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        yield db


@pytest.fixture
def mock_async_client() -> AsyncMock:
    """Create a mock async HTTP client.

    Use this for unit tests that need to mock HTTP calls
    without actually making network requests.
    """
    return AsyncMock()


@pytest.fixture
def mock_logger() -> MagicMock:
    """Create a mock logger for testing.

    Use this to verify log messages in tests.
    """
    return MagicMock()


# Unit test markers
def pytest_configure(config) -> None:
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "fast: Fast running tests")
