"""Tests for Pydantic schemas."""
import pytest
from app.models.schemas import ASRRequest


def test_asr_request_with_vad_method():
    """Test that ASRRequest accepts vad_method='ten'."""
    request = ASRRequest(vad_method="ten")
    assert request.vad_method == "ten"


def test_asr_request_default_vad_method():
    """Test that ASRRequest defaults to vad_method='silero'."""
    request = ASRRequest()
    assert request.vad_method == "silero"


def test_asr_request_with_silero_vad_method():
    """Test that ASRRequest accepts vad_method='silero' explicitly."""
    request = ASRRequest(vad_method="silero")
    assert request.vad_method == "silero"


def test_asr_request_with_all_fields():
    """Test that ASRRequest accepts all fields including vad_method."""
    request = ASRRequest(
        asr_method="whisper-api",
        vad_method="ten",
        vad_options={"threshold": 0.5},
        asr_options={"language": "en"},
        output_mode="task"
    )
    assert request.asr_method == "whisper-api"
    assert request.vad_method == "ten"
    assert request.vad_options == {"threshold": 0.5}
    assert request.asr_options == {"language": "en"}
    assert request.output_mode == "task"
