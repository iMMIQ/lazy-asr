"""
ASR Service Tests - TDD for Configurable VAD
Tests for the ASR service to verify VAD method parameter support
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.asr_service import ASRService


class TestASRServiceVADMethodParameter:
    """Test that ASRService accepts and uses vad_method parameter"""

    def test_asr_service_exists(self):
        """ASRService class should exist"""
        from app.services.asr_service import ASRService
        assert ASRService is not None

    def test_asr_service_has_process_media_method(self):
        """ASRService should have process_media method"""
        from app.services.asr_service import ASRService
        assert hasattr(ASRService, "process_media")

    def test_asr_service_accepts_vad_method_parameter(self):
        """process_media should accept vad_method parameter"""
        from app.services.asr_service import ASRService
        import inspect

        sig = inspect.signature(ASRService.process_media)
        params = sig.parameters

        assert "vad_method" in params, "process_media should have vad_method parameter"
        assert params["vad_method"].default == "silero", "vad_method should default to 'silero'"


class TestASRServiceVADMethodUsage:
    """Test that ASRService uses the configurable VAD segmentation"""

    @pytest.mark.asyncio
    async def test_process_media_uses_vad_segmentation_with_provider(self):
        """process_media should use vad_segmentation_with_provider when vad_method is provided"""
        from app.services.asr_service import ASRService
        from unittest.mock import AsyncMock, patch

        service = ASRService()

        # Mock all the dependencies
        mock_speech_timestamps = [
            {'start': 0.0, 'end': 2.5},
            {'start': 3.0, 'end': 5.5}
        ]

        with patch('app.services.asr_service.validate_media_file', return_value=(True, "")), \
             patch('app.services.asr_service.prepare_media_for_asr', return_value=("/fake/audio.wav", "audio")), \
             patch('app.services.asr_service.vad_segmentation_with_provider',
                   return_value=(mock_speech_timestamps, MagicMock(), 16000)) as mock_vad, \
             patch('app.services.asr_service.export_silero_segments', return_value=[
                 {'index': 1, 'file_path': '/fake/seg1.wav', 'start_time': 0.0, 'end_time': 2.5, 'duration': 2.5}
             ]), \
             patch('plugins.manager.plugin_manager.get_plugin') as mock_get_plugin:

            # Mock plugin
            mock_plugin = MagicMock()
            mock_plugin.transcribe_segments = AsyncMock(return_value=[
                {'success': True, 'transcription': ['Hello world'], 'segment_info': None, 'segment_index': 0}
            ])
            mock_get_plugin.return_value = mock_plugin

            with patch('app.services.asr_service.generate_subtitle_files', return_value={'srt': '/fake/output.srt'}), \
                 patch('app.services.asr_service.os.path.exists', return_value=True):

                # Call process_media with vad_method parameter
                await service.process_media(
                    media_path="/fake/media.mp4",
                    asr_method="whisper-api",
                    vad_method="silero"
                )

                # Verify vad_segmentation_with_provider was called with the correct provider_name
                mock_vad.assert_called_once()
                call_args = mock_vad.call_args
                assert call_args[1]['provider_name'] == "silero", "vad_segmentation_with_provider should be called with provider_name='silero'"

    @pytest.mark.asyncio
    async def test_process_media_uses_default_vad_method_when_not_specified(self):
        """process_media should use 'silero' as default vad_method when not specified"""
        from app.services.asr_service import ASRService
        from unittest.mock import AsyncMock, patch

        service = ASRService()

        # Mock all the dependencies
        mock_speech_timestamps = [
            {'start': 0.0, 'end': 2.5}
        ]

        with patch('app.services.asr_service.validate_media_file', return_value=(True, "")), \
             patch('app.services.asr_service.prepare_media_for_asr', return_value=("/fake/audio.wav", "audio")), \
             patch('app.services.asr_service.vad_segmentation_with_provider',
                   return_value=(mock_speech_timestamps, MagicMock(), 16000)) as mock_vad, \
             patch('app.services.asr_service.export_silero_segments', return_value=[
                 {'index': 1, 'file_path': '/fake/seg1.wav', 'start_time': 0.0, 'end_time': 2.5, 'duration': 2.5}
             ]), \
             patch('plugins.manager.plugin_manager.get_plugin') as mock_get_plugin:

            # Mock plugin
            mock_plugin = MagicMock()
            mock_plugin.transcribe_segments = AsyncMock(return_value=[
                {'success': True, 'transcription': ['Hello world'], 'segment_info': None, 'segment_index': 0}
            ])
            mock_get_plugin.return_value = mock_plugin

            with patch('app.services.asr_service.generate_subtitle_files', return_value={'srt': '/fake/output.srt'}), \
                 patch('app.services.asr_service.os.path.exists', return_value=True):

                # Call process_media WITHOUT vad_method parameter
                await service.process_media(
                    media_path="/fake/media.mp4",
                    asr_method="whisper-api"
                )

                # Verify vad_segmentation_with_provider was called with default 'silero'
                mock_vad.assert_called_once()
                call_args = mock_vad.call_args
                assert call_args[1]['provider_name'] == "silero", "vad_segmentation_with_provider should be called with provider_name='silero' by default"

    @pytest.mark.asyncio
    async def test_process_media_passes_vad_options_to_vad_segmentation(self):
        """process_media should pass vad_options to vad_segmentation_with_provider"""
        from app.services.asr_service import ASRService
        from unittest.mock import AsyncMock, patch

        service = ASRService()

        # Mock all the dependencies
        mock_speech_timestamps = [
            {'start': 0.0, 'end': 2.5}
        ]

        with patch('app.services.asr_service.validate_media_file', return_value=(True, "")), \
             patch('app.services.asr_service.prepare_media_for_asr', return_value=("/fake/audio.wav", "audio")), \
             patch('app.services.asr_service.vad_segmentation_with_provider',
                   return_value=(mock_speech_timestamps, MagicMock(), 16000)) as mock_vad, \
             patch('app.services.asr_service.export_silero_segments', return_value=[
                 {'index': 1, 'file_path': '/fake/seg1.wav', 'start_time': 0.0, 'end_time': 2.5, 'duration': 2.5}
             ]), \
             patch('plugins.manager.plugin_manager.get_plugin') as mock_get_plugin:

            # Mock plugin
            mock_plugin = MagicMock()
            mock_plugin.transcribe_segments = AsyncMock(return_value=[
                {'success': True, 'transcription': ['Hello world'], 'segment_info': None, 'segment_index': 0}
            ])
            mock_get_plugin.return_value = mock_plugin

            with patch('app.services.asr_service.generate_subtitle_files', return_value={'srt': '/fake/output.srt'}), \
                 patch('app.services.asr_service.os.path.exists', return_value=True):

                # Call process_media with custom vad_options
                custom_vad_options = {
                    'threshold': 0.7,
                    'min_speech_duration_ms': 300,
                    'min_silence_duration_ms': 400
                }

                await service.process_media(
                    media_path="/fake/media.mp4",
                    asr_method="whisper-api",
                    vad_method="silero",
                    vad_options=custom_vad_options
                )

                # Verify vad_segmentation_with_provider was called with the correct options
                mock_vad.assert_called_once()
                call_args = mock_vad.call_args
                assert call_args[1]['vad_options'] == custom_vad_options, "vad_segmentation_with_provider should receive the vad_options"
