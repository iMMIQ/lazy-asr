"""
Tests for ASR API routes.

Tests VAD method parameter acceptance in the ASR endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO


@pytest.fixture
def mock_asr_service():
    """Mock ASR service."""
    with patch("app.api.endpoints.asr.asr_service") as mock:
        mock.process_audio = AsyncMock()
        yield mock


@pytest.fixture
def mock_plugin_manager():
    """Mock plugin manager."""
    with patch("app.api.endpoints.asr.plugin_manager") as mock:
        mock.get_plugin_names.return_value = ["whisper-api", "whisper-local"]
        mock.get_plugin.return_value = Mock()
        yield mock


@pytest.fixture
def mock_vad_manager():
    """Mock VAD manager."""
    with patch("app.vad.manager.vad_manager") as mock:
        mock.get_provider_names.return_value = ["silero", "ten"]
        mock.get_provider.return_value = Mock()
        yield mock


@pytest.mark.asyncio
class TestProcessEndpointVADMethod:
    """Test VAD method parameter in /process endpoint."""

    async def test_process_accepts_vad_method_parameter(
        self, client: AsyncClient, mock_asr_service, mock_plugin_manager,
        mock_vad_manager
    ):
        """Test that the /process endpoint accepts vad_method parameter."""
        # Mock successful ASR processing
        from app.models.schemas import ASRResponse
        mock_asr_service.process_audio.return_value = ASRResponse(
            success=True,
            message="Processing completed",
            srt_file_path="/output/test.srt",
            output_files={"srt": "/output/test.srt"},
            segments=[],
            stats={"total_subtitles": 10},
            task_id="test-task-id"
        )

        # Create a mock file upload
        file_content = b"fake audio data"
        files = {"media_file": ("test.wav", BytesIO(file_content), "audio/wav")}

        # Test with silero VAD method (default)
        data = {
            "asr_method": "whisper-api",
            "vad_method": "silero",
        }

        response = await client.post("/api/v1/asr/process", files=files, data=data)

        assert response.status_code == 200
        mock_asr_service.process_audio.assert_called_once()
        # Check vad_method was passed
        call_kwargs = mock_asr_service.process_audio.call_args[1]
        assert call_kwargs["vad_method"] == "silero"

    async def test_process_with_ten_vad_method(
        self, client: AsyncClient, mock_asr_service, mock_plugin_manager,
        mock_vad_manager
    ):
        """Test that the /process endpoint accepts ten as vad_method."""
        from app.models.schemas import ASRResponse
        mock_asr_service.process_audio.return_value = ASRResponse(
            success=True,
            message="Processing completed",
            srt_file_path="/output/test.srt",
            output_files={"srt": "/output/test.srt"},
            segments=[],
            stats={"total_subtitles": 10},
            task_id="test-task-id"
        )

        file_content = b"fake audio data"
        files = {"media_file": ("test.wav", BytesIO(file_content), "audio/wav")}

        data = {
            "asr_method": "whisper-api",
            "vad_method": "ten",
        }

        response = await client.post("/api/v1/asr/process", files=files, data=data)

        assert response.status_code == 200
        call_kwargs = mock_asr_service.process_audio.call_args[1]
        assert call_kwargs["vad_method"] == "ten"


@pytest.mark.asyncio
class TestProcessMultipleEndpointVADMethod:
    """Test VAD method parameter in /process-multiple endpoint."""

    async def test_process_multiple_accepts_vad_method_parameter(
        self, client: AsyncClient, mock_asr_service, mock_plugin_manager,
        mock_vad_manager
    ):
        """Test that the /process-multiple endpoint accepts vad_method parameter."""
        from app.models.schemas import ASRResponse
        mock_asr_service.process_audio.return_value = ASRResponse(
            success=True,
            message="Processing completed",
            srt_file_path="/output/test.srt",
            output_files={"srt": "/output/test.srt"},
            segments=[],
            stats={"total_subtitles": 10},
            task_id="test-task-id"
        )

        file_content = b"fake audio data"
        files = [
            ("audio_files", ("test1.wav", BytesIO(file_content), "audio/wav")),
            ("audio_files", ("test2.wav", BytesIO(file_content), "audio/wav")),
        ]

        data = {
            "asr_method": "whisper-api",
            "vad_method": "silero",
        }

        response = await client.post("/api/v1/asr/process-multiple", files=files, data=data)

        assert response.status_code == 200
        # Check vad_method was passed in calls
        assert mock_asr_service.process_audio.call_count == 2
        for call in mock_asr_service.process_audio.call_args_list:
            call_kwargs = call[1]
            assert call_kwargs["vad_method"] == "silero"


@pytest.mark.asyncio
class TestVADEndpoints:
    """Test VAD provider info endpoint."""

    async def test_get_vad_providers(self, client: AsyncClient):
        """Test getting available VAD providers."""
        with patch("app.api.endpoints.vad.vad_manager") as mock_manager:
            mock_manager.get_available_providers.return_value = [
                {
                    "name": "silero",
                    "display_name": "Silero VAD",
                    "description": "High-quality VAD using Silero model"
                },
                {
                    "name": "ten",
                    "display_name": "TEN VAD",
                    "description": "TEN VAD provider"
                }
            ]

            response = await client.get("/api/v1/vad/providers")

            assert response.status_code == 200
            data = response.json()
            assert "providers" in data
            assert "default" in data
            assert data["default"] == "silero"
            assert len(data["providers"]) >= 1
            assert any(p["name"] == "silero" for p in data["providers"])

    async def test_vad_providers_structure(self, client: AsyncClient):
        """Test VAD providers response structure."""
        with patch("app.api.endpoints.vad.vad_manager") as mock_manager:
            mock_manager.get_available_providers.return_value = [
                {
                    "name": "silero",
                    "display_name": "Silero VAD",
                    "description": "High-quality VAD using Silero model"
                }
            ]

            response = await client.get("/api/v1/vad/providers")
            data = response.json()

            # Validate structure
            assert isinstance(data, dict)
            assert isinstance(data["providers"], list)
            assert isinstance(data["default"], str)

            # Validate provider structure
            if data["providers"]:
                provider = data["providers"][0]
                assert "name" in provider
                assert "display_name" in provider
                assert "description" in provider
