"""
WebSocket connection manager tests - TDD First Cycle
"""
import pytest
import asyncio
from app.core.websocket import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connection_manager_connect(manager):
    """Test connecting a client"""
    websocket = "mock_ws"
    scan_id = "test-scan-1"
    await manager.connect(websocket, scan_id)
    assert scan_id in manager.active_connections
    assert websocket in manager.active_connections[scan_id]


@pytest.mark.asyncio
async def test_connection_manager_disconnect(manager):
    """Test disconnecting a client"""
    websocket = "mock_ws"
    scan_id = "test-scan-2"
    await manager.connect(websocket, scan_id)
    await manager.disconnect(websocket, scan_id)
    # Should not raise error
    assert scan_id not in manager.active_connections or len(manager.active_connections.get(scan_id, [])) == 0


@pytest.mark.asyncio
async def test_broadcast_to_scan(manager):
    """Test broadcasting message to specific scan subscribers"""
    # Mock websockets that track received messages
    received = []

    class MockWS:
        def __init__(self, name):
            self.name = name
        async def accept(self):
            pass
        async def send_json(self, message):
            received.append((self.name, message))

    ws1 = MockWS("ws1")
    ws2 = MockWS("ws2")
    ws3 = MockWS("ws3")

    scan_id = "test-scan-3"
    await manager.connect(ws1, scan_id)
    await manager.connect(ws2, scan_id)
    await manager.connect(ws3, "other-scan")

    message = {"type": "status", "data": "test message"}
    await manager.broadcast_to_scan(scan_id, message)

    await asyncio.sleep(0.1)  # Let async tasks complete

    # ws1 and ws2 should receive, ws3 should not
    assert ("ws1", message) in received
    assert ("ws2", message) in received
    assert ("ws3", message) not in received


@pytest.mark.asyncio
async def test_get_scan_subscriber_count(manager):
    """Test getting subscriber count for a scan"""
    ws1 = "mock1"
    ws2 = "mock2"
    scan_id = "test-scan-4"
    await manager.connect(ws1, scan_id)
    await manager.connect(ws2, scan_id)
    count = await manager.get_scan_subscriber_count(scan_id)
    assert count == 2
