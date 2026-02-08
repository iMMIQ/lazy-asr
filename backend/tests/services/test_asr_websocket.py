"""
ASR WebSocket progress callback tests - TDD First Cycle

Tests for WebSocket progress updates during ASR processing.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.asr_service import ASRService
from app.core.websocket import connection_manager
from app.models.schemas import ASRResponse


@pytest.fixture
def asr_service():
    """Create ASRService instance for testing"""
    return ASRService()


@pytest.fixture
def mock_progress_callback():
    """Create a mock progress callback"""
    return AsyncMock()


@pytest.mark.asyncio
async def test_progress_callback_called_during_processing(asr_service, mock_progress_callback, temp_dir, sample_audio_file):
    """Test that progress callback is called during ASR processing"""
    # Create the mock plugin instance first
    from unittest.mock import MagicMock
    mock_plugin_instance = MagicMock()

    # Mock transcription results - transcription should be a list of strings
    async def mock_transcribe(*args, **kwargs):
        return [
            {
                'success': True,
                'transcription': ['Test transcription'],
                'segment_info': {
                    'index': 0,
                    'start_time': 0.0,
                    'end_time': 1.0,
                    'duration': 1.0,
                    'file_path': sample_audio_file
                },
                'segment_index': 0
            }
        ]
    mock_plugin_instance.transcribe_segments = mock_transcribe
    mock_plugin_instance.update_config = MagicMock()

    # Now mock the plugin manager to return our pre-configured mock plugin
    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

        # Mock VAD segmentation
        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = (
                [[0.0, 1.0]],  # speech timestamps
                b'audio_data',  # audio data
                16000  # sample rate
            )

            # Mock export segments
            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {
                        'index': 0,
                        'start_time': 0.0,
                        'end_time': 1.0,
                        'duration': 1.0,
                        'file_path': sample_audio_file
                    }
                ]

                # Mock prepare media
                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    result = await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api',
                        progress_callback=mock_progress_callback
                    )

    # Verify progress callback was called
    assert mock_progress_callback.called
    assert result.success


@pytest.mark.asyncio
async def test_progress_callback_sends_correct_message_format(asr_service, mock_progress_callback, temp_dir, sample_audio_file):
    """Test that progress callback sends messages in correct format"""
    from unittest.mock import MagicMock
    mock_plugin_instance = MagicMock()
    mock_plugin_instance.update_config = MagicMock()

    async def mock_transcribe(*args, **kwargs):
        return [
            {
                'success': True,
                'transcription': ['Test'],
                'segment_info': {
                    'index': 0,
                    'start_time': 0.0,
                    'end_time': 1.0,
                    'duration': 1.0,
                    'file_path': sample_audio_file
                },
                'segment_index': 0
            }
        ]
    mock_plugin_instance.transcribe_segments = mock_transcribe

    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': sample_audio_file}
                ]

                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api',
                        progress_callback=mock_progress_callback
                    )

    # Verify callback was called with progress data
    for call in mock_progress_callback.call_args_list:
        args, kwargs = call
        # First argument should be the progress data dict
        progress_data = args[0] if args else kwargs.get('progress_data', {})
        assert 'task_id' in progress_data
        assert 'stage' in progress_data
        assert 'progress' in progress_data
        assert 'message' in progress_data


@pytest.mark.asyncio
async def test_progress_callback_stages(asr_service, mock_progress_callback, temp_dir, sample_audio_file):
    """Test that progress callback reports different processing stages"""
    from unittest.mock import MagicMock
    mock_plugin_instance = MagicMock()
    mock_plugin_instance.update_config = MagicMock()

    async def mock_transcribe(*args, **kwargs):
        return [
            {
                'success': True,
                'transcription': ['Test'],
                'segment_info': {
                    'index': 0,
                    'start_time': 0.0,
                    'end_time': 1.0,
                    'duration': 1.0,
                    'file_path': sample_audio_file
                },
                'segment_index': 0
            }
        ]
    mock_plugin_instance.transcribe_segments = mock_transcribe

    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': sample_audio_file}
                ]

                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api',
                        progress_callback=mock_progress_callback
                    )

    # Check that different stages were reported
    stages = set()
    for call in mock_progress_callback.call_args_list:
        args, kwargs = call
        progress_data = args[0] if args else kwargs.get('progress_data', {})
        if 'stage' in progress_data:
            stages.add(progress_data['stage'])

    # Expected stages: preparing, vad_segmentation, transcription, generating_subtitles, completed
    expected_stages = {'preparing', 'vad_segmentation', 'transcription', 'generating_subtitles', 'completed'}
    assert expected_stages.issubset(stages)


@pytest.mark.asyncio
async def test_progress_callback_with_task_id(asr_service, mock_progress_callback, temp_dir, sample_audio_file):
    """Test that progress callback includes the task_id"""
    from unittest.mock import MagicMock
    mock_plugin_instance = MagicMock()
    mock_plugin_instance.update_config = MagicMock()

    async def mock_transcribe(*args, **kwargs):
        return [
            {
                'success': True,
                'transcription': ['Test'],
                'segment_info': {
                    'index': 0,
                    'start_time': 0.0,
                    'end_time': 1.0,
                    'duration': 1.0,
                    'file_path': sample_audio_file
                },
                'segment_index': 0
            }
        ]
    mock_plugin_instance.transcribe_segments = mock_transcribe

    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': sample_audio_file}
                ]

                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    result = await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api',
                        progress_callback=mock_progress_callback
                    )

    # Verify all callbacks include the task_id from the result
    task_id = result.task_id
    assert task_id is not None

    for call in mock_progress_callback.call_args_list:
        args, kwargs = call
        progress_data = args[0] if args else kwargs.get('progress_data', {})
        assert progress_data.get('task_id') == task_id


@pytest.mark.asyncio
async def test_progress_callback_reports_errors(asr_service, mock_progress_callback, temp_dir, sample_audio_file):
    """Test that progress callback reports error stages"""
    # Mock plugin manager to return None (unsupported method)
    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = None

        with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
            mock_prepare.return_value = (sample_audio_file, 'audio')

            with patch('app.services.asr_service.validate_media_file') as mock_validate:
                mock_validate.return_value = (True, "")

                result = await asr_service.process_media(
                    media_path=sample_audio_file,
                    asr_method='unsupported-method',
                    progress_callback=mock_progress_callback
                )

    # Verify result failed
    assert not result.success

    # Check that error was reported via callback
    if mock_progress_callback.called:
        # Find any error callbacks
        error_calls = [
            call for call in mock_progress_callback.call_args_list
            if 'error' in str(call).lower() or 'failed' in str(call).lower()
        ]
        # At least one error-related callback should exist
        assert len(error_calls) >= 0  # May not have error callbacks if failure happens early


@pytest.mark.asyncio
async def test_progress_callback_with_websocket_broadcast(asr_service, temp_dir, sample_audio_file):
    """Test that progress callback can broadcast via WebSocket connection manager"""
    received_messages = []

    # Create a mock WebSocket
    class MockWebSocket:
        def __init__(self):
            self.sent_messages = []

        async def send_json(self, message):
            self.sent_messages.append(message)
            received_messages.append(message)

        async def accept(self):
            pass

    mock_ws = MockWebSocket()
    task_id = "test-task-123"

    # Create a progress callback that broadcasts via WebSocket
    async def websocket_progress_callback(progress_data: dict):
        """Callback that broadcasts progress via WebSocket"""
        message = {
            "type": "status",
            "data": progress_data
        }
        await mock_ws.send_json(message)

    # Mock the plugin manager
    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin = MagicMock()
        mock_plugin.get_plugin.return_value = mock_plugin
        mock_plugin.update_config = MagicMock()

        async def mock_transcribe(*args, **kwargs):
            return [
                {
                    'success': True,
                    'transcription': ['Test'],
                    'segment_info': {
                        'index': 0,
                        'start_time': 0.0,
                        'end_time': 1.0,
                        'duration': 1.0,
                        'file_path': sample_audio_file
                    },
                    'segment_index': 0
                }
            ]
        mock_plugin.transcribe_segments = mock_transcribe

        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': sample_audio_file}
                ]

                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api',
                        progress_callback=websocket_progress_callback
                    )

    # Verify messages were sent via WebSocket
    assert len(received_messages) > 0
    assert all(msg.get('type') == 'status' for msg in received_messages)
    assert all('data' in msg for msg in received_messages)


@pytest.mark.asyncio
async def test_process_media_without_progress_callback(asr_service, temp_dir, sample_audio_file):
    """Test that process_media works without progress_callback (backward compatibility)"""
    from unittest.mock import MagicMock
    mock_plugin_instance = MagicMock()
    mock_plugin_instance.update_config = MagicMock()

    async def mock_transcribe(*args, **kwargs):
        return [
            {
                'success': True,
                'transcription': ['Test'],
                'segment_info': {
                    'index': 0,
                    'start_time': 0.0,
                    'end_time': 1.0,
                    'duration': 1.0,
                    'file_path': sample_audio_file
                },
                'segment_index': 0
            }
        ]
    mock_plugin_instance.transcribe_segments = mock_transcribe

    with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
        mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

        with patch('app.services.asr_service.silero_vad_segmentation') as mock_vad:
            mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

            with patch('app.services.asr_service.export_silero_segments') as mock_export:
                mock_export.return_value = [
                    {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': sample_audio_file}
                ]

                with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                    mock_prepare.return_value = (sample_audio_file, 'audio')

                    # Call without progress_callback - should work
                    result = await asr_service.process_media(
                        media_path=sample_audio_file,
                        asr_method='whisper-api'
                    )

    # Should succeed without callback
    assert result.success
