"""Fixtures for CLI tests"""

import pytest
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """CLI test runner"""
    from typer.testing import CliRunner
    return CliRunner()


@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a sample audio file for testing"""
    import numpy as np
    import soundfile as sf

    audio_path = tmp_path / "test_audio.wav"
    # Create 1 second of silence
    sample_rate = 16000
    samples = np.zeros(sample_rate, dtype=np.float32)
    sf.write(str(audio_path), samples, sample_rate)

    return audio_path


@pytest.fixture
def sample_media_directory(tmp_path):
    """Create a directory with sample media files"""
    import numpy as np
    import soundfile as sf

    media_dir = tmp_path / "media"
    media_dir.mkdir()

    # Create a few test audio files
    for i in range(3):
        audio_path = media_dir / f"audio_{i}.wav"
        sample_rate = 16000
        samples = np.zeros(sample_rate, dtype=np.float32)
        sf.write(str(audio_path), samples, sample_rate)

    return media_dir
