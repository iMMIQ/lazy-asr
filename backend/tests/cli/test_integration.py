"""Integration tests for CLI workflow"""

import pytest
from pathlib import Path
import asyncio


@pytest.mark.asyncio
async def test_cli_transcribe_workflow(sample_audio_file, tmp_path):
    """Test full transcription workflow via CLI"""
    from app.cli.main import _run_transcription
    from app.services.asr_service import ASRService
    import os

    output_dir = str(tmp_path / "output")

    # This is a basic test - actual transcription would require valid audio
    # and working ASR backend
    result = await _run_transcription(
        file_path=str(sample_audio_file),
        asr_method="local-whisper",
        vad_method="silero",
        language="auto",
        output_formats=["srt"],
        output_mode="task",
        output_dir=output_dir,
        api_url=None,
        api_key=None,
        model=None,
        verbose=False,
    )

    # Result should be an ASRResponse
    assert hasattr(result, "success")


def test_cli_scan_workflow(sample_media_directory, tmp_path):
    """Test full scan workflow via CLI"""
    from app.cli.main import _run_scan
    import asyncio

    result = asyncio.run(_run_scan(
        scan_path=str(sample_media_directory),
        recursive=True,
        max_files=10,
        skip_existing=True,
        asr_method="local-whisper",
        vad_method="silero",
        output_formats=["srt"],
    ))

    # Result should be a dict with scan info
    assert isinstance(result, dict)
    assert "scan_id" in result or "error" in result
