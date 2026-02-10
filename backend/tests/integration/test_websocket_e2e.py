"""
End-to-end WebSocket integration tests

These tests verify the complete WebSocket flow from client connection
through message broadcasting to disconnection.
"""
import pytest
import asyncio
import os
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_websocket_scan_flow_e2e(temp_dir):
    """Test complete WebSocket flow for scan updates"""
    from app.services.scan_service import scan_service
    from app.core.websocket import connection_manager

    # Mock WebSocket client
    class MockWebSocketClient:
        def __init__(self):
            self.messages = []
            self.connected = False

        async def connect(self, scan_id: str):
            await connection_manager.connect(self, scan_id)
            self.connected = True

        async def disconnect(self, scan_id: str):
            await connection_manager.disconnect(self, scan_id)
            self.connected = False

        async def receive_message(self):
            # Simulate receiving a message (would normally wait)
            pass

        async def send_json(self, message: dict):
            self.messages.append(message)

        async def accept(self):
            pass

    # Simulate scan flow with WebSocket
    scan_id = "test-scan-e2e"

    # Create mock WebSocket client
    client = MockWebSocketClient()

    # Connect client to scan
    await client.connect(scan_id)

    # Verify connection
    assert client.connected
    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 1

    # Simulate scan progress updates
    progress_updates = [
        {"scan_id": scan_id, "status": "scanning", "progress": 0},
        {"scan_id": scan_id, "status": "scanning", "progress": 50},
        {"scan_id": scan_id, "status": "completed", "progress": 100},
    ]

    for update in progress_updates:
        await connection_manager.broadcast_to_scan(scan_id, {
            "type": "status",
            "data": update
        })

    # Verify client received updates
    # (In real scenario, this would be through WebSocket)
    # For this test, we verify the connection manager works

    # Disconnect client
    await client.disconnect(scan_id)

    # Verify disconnection
    assert not client.connected
    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 0


@pytest.mark.asyncio
async def test_websocket_asr_processing_flow_e2e(temp_dir):
    """Test complete WebSocket flow for ASR processing updates"""
    from app.services.asr_service import ASRService
    from app.core.websocket import connection_manager

    # Create test audio file
    import wave
    audio_path = os.path.join(temp_dir, "test_asr_e2e.wav")
    with wave.open(audio_path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        silence = b"\x00\x00" * 16000
        wav_file.writeframes(silence)

    # Track WebSocket broadcasts
    broadcast_messages = []

    async def capture_broadcast(channel_id: str, message: dict):
        broadcast_messages.append({
            'channel_id': channel_id,
            'message': message
        })

    with patch('app.core.websocket.connection_manager') as mock_cm:
        mock_cm.broadcast_to_scan = capture_broadcast

        # Mock dependencies
        with patch('app.services.asr_service.plugin_manager') as mock_plugin_mgr:
            mock_plugin_instance = MagicMock()
            mock_plugin_instance.update_config = MagicMock()

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
                            'file_path': audio_path
                        },
                        'segment_index': 0
                    }
                ]
            mock_plugin_instance.transcribe_segments = mock_transcribe
            mock_plugin_mgr.get_plugin.return_value = mock_plugin_instance

            with patch('app.services.asr_service.vad_segmentation_with_provider') as mock_vad:
                mock_vad.return_value = ([[0.0, 1.0]], b'audio_data', 16000)

                with patch('app.services.asr_service.export_silero_segments') as mock_export:
                    mock_export.return_value = [
                        {'index': 0, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0, 'file_path': audio_path}
                    ]

                    with patch('app.services.asr_service.prepare_media_for_asr') as mock_prepare:
                        mock_prepare.return_value = (audio_path, 'audio')

                        # Process with progress callback that broadcasts
                        async def progress_callback(progress_data: dict):
                            await capture_broadcast(progress_data.get('task_id', ''), {
                                "type": "status",
                                "data": progress_data
                            })

                        asr_service = ASRService()
                        result = await asr_service.process_media(
                            media_path=audio_path,
                            asr_method='whisper-api',
                            progress_callback=progress_callback
                        )

                        # Verify processing succeeded
                        assert result.success
                        assert result.task_id is not None

                        # Verify WebSocket broadcasts were made
                        assert len(broadcast_messages) > 0

                        # Verify broadcast structure
                        for broadcast in broadcast_messages:
                            if isinstance(broadcast, dict) and 'message' in broadcast:
                                msg = broadcast['message']
                                assert msg['type'] == 'status'
                                assert 'data' in msg
                                data = msg['data']
                                assert 'task_id' in data
                                assert 'stage' in data
                                assert 'progress' in data
                                assert 'message' in data


@pytest.mark.asyncio
async def test_websocket_multiple_clients_same_scan():
    """Test multiple clients subscribed to the same scan"""
    from app.core.websocket import connection_manager

    class MockWebSocketClient:
        def __init__(self, name: str):
            self.name = name
            self.messages = []

        async def send_json(self, message: dict):
            self.messages.append(message)

        async def accept(self):
            pass

    # Create multiple clients
    clients = [
        MockWebSocketClient(f"client{i}")
        for i in range(3)
    ]

    scan_id = "test-scan-multi"

    # Connect all clients
    for client in clients:
        await connection_manager.connect(client, scan_id)

    # Verify all connected
    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 3

    # Broadcast a message
    test_message = {
        "type": "status",
        "data": {
            "scan_id": scan_id,
            "status": "scanning",
            "progress": 25
        }
    }

    await connection_manager.broadcast_to_scan(scan_id, test_message)

    # Verify all clients received the message
    for client in clients:
        assert len(client.messages) == 1
        assert client.messages[0] == test_message

    # Disconnect one client
    await connection_manager.disconnect(clients[0], scan_id)

    # Verify remaining clients
    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 2

    # Broadcast again
    await connection_manager.broadcast_to_scan(scan_id, test_message)

    # Verify remaining clients received, disconnected did not
    assert len(clients[0].messages) == 1  # No new message
    assert len(clients[1].messages) == 2  # Got new message
    assert len(clients[2].messages) == 2  # Got new message

    # Cleanup
    await connection_manager.disconnect(clients[1], scan_id)
    await connection_manager.disconnect(clients[2], scan_id)


@pytest.mark.asyncio
async def test_websocket_client_disconnect_handling():
    """Test graceful handling of client disconnections"""
    from app.core.websocket import connection_manager

    class FlakyWebSocketClient:
        def __init__(self, name: str, fail_on_send: bool = False):
            self.name = name
            self.messages = []
            self.fail_on_send = fail_on_send

        async def send_json(self, message: dict):
            if self.fail_on_send:
                raise Exception("Network error")
            self.messages.append(message)

        async def accept(self):
            pass

    scan_id = "test-scan-flaky"

    # Create a flaky client
    flaky_client = FlakyWebSocketClient("flaky", fail_on_send=True)
    normal_client = FlakyWebSocketClient("normal", fail_on_send=False)

    # Connect clients
    await connection_manager.connect(flaky_client, scan_id)
    await connection_manager.connect(normal_client, scan_id)

    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 2

    # Broadcast - should handle flaky client gracefully
    test_message = {
        "type": "status",
        "data": {"scan_id": scan_id, "status": "scanning", "progress": 50}
    }

    await connection_manager.broadcast_to_scan(scan_id, test_message)

    # Flaky client should be disconnected after failed send
    # Normal client should receive the message
    assert len(flaky_client.messages) == 0
    assert len(normal_client.messages) == 1

    # Verify flaky client was removed
    count = await connection_manager.get_scan_subscriber_count(scan_id)
    assert count == 1

    # Cleanup
    await connection_manager.disconnect(normal_client, scan_id)


@pytest.mark.asyncio
async def test_websocket_scan_lifecycle():
    """Test complete scan lifecycle with WebSocket updates"""
    from app.core.websocket import connection_manager
    from app.models.schemas import ScanStatus

    class MockWebSocketClient:
        def __init__(self):
            self.messages = []

        async def send_json(self, message: dict):
            self.messages.append(message)

        async def accept(self):
            pass

    scan_id = "test-scan-lifecycle"
    client = MockWebSocketClient()

    # Connect
    await connection_manager.connect(client, scan_id)
    assert await connection_manager.get_scan_subscriber_count(scan_id) == 1

    # Simulate scan lifecycle
    lifecycle_messages = [
        {"scan_id": scan_id, "status": "pending", "progress": 0},
        {"scan_id": scan_id, "status": "scanning", "progress": 10},
        {"scan_id": scan_id, "status": "scanning", "progress": 50},
        {"scan_id": scan_id, "status": "scanning", "progress": 90},
        {"scan_id": scan_id, "status": "completed", "progress": 100},
    ]

    for status_update in lifecycle_messages:
        await connection_manager.broadcast_to_scan(scan_id, {
            "type": "status",
            "data": status_update
        })

    # Verify all messages received
    assert len(client.messages) == len(lifecycle_messages)

    # Disconnect
    await connection_manager.disconnect(client, scan_id)
    assert await connection_manager.get_scan_subscriber_count(scan_id) == 0


@pytest.mark.asyncio
async def test_websocket_concurrent_scans():
    """Test multiple scans with separate WebSocket channels"""
    from app.core.websocket import connection_manager

    class MockWebSocketClient:
        def __init__(self):
            self.messages = []

        async def send_json(self, message: dict):
            self.messages.append(message)

        async def accept(self):
            pass

    # Create multiple scans
    scans = ["scan-1", "scan-2", "scan-3"]
    clients = {scan_id: MockWebSocketClient() for scan_id in scans}

    # Connect each client to its scan
    for scan_id, client in clients.items():
        await connection_manager.connect(client, scan_id)

    # Verify each scan has one subscriber
    for scan_id in scans:
        count = await connection_manager.get_scan_subscriber_count(scan_id)
        assert count == 1

    # Broadcast to each scan independently
    for scan_id in scans:
        await connection_manager.broadcast_to_scan(scan_id, {
            "type": "status",
            "data": {"scan_id": scan_id, "status": "scanning", "progress": 50}
        })

    # Verify each client received only its scan's message
    for scan_id, client in clients.items():
        assert len(client.messages) == 1
        assert client.messages[0]["data"]["scan_id"] == scan_id

    # Cleanup
    for scan_id, client in clients.items():
        await connection_manager.disconnect(client, scan_id)


@pytest.mark.asyncio
async def test_websocket_invalid_scan_id():
    """Test handling of invalid scan IDs"""
    from app.core.websocket import connection_manager

    class MockWebSocketClient:
        async def send_json(self, message: dict):
            pass

        async def accept(self):
            pass

    # Test with invalid characters
    invalid_scan_ids = [
        "",  # Empty
        "scan\nwith\nnewlines",  # Newlines
        "scan\x00null",  # Null byte
        "scan<script>",  # HTML tags
        "a" * 101,  # Too long (>100 chars)
    ]

    client = MockWebSocketClient()

    for invalid_id in invalid_scan_ids:
        # Connection should still work for tracking
        # but validation should happen at endpoint level
        # This test documents expected behavior
        await connection_manager.connect(client, invalid_id)

        # Cleanup
        await connection_manager.disconnect(client, invalid_id)
