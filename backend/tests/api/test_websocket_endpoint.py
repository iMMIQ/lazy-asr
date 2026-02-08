"""
Tests for WebSocket endpoint

Tests WebSocket connectivity and basic functionality.
"""
import pytest


@pytest.mark.asyncio
async def test_connection_manager_exists():
    """Test that connection_manager is properly instantiated"""
    from app.core.websocket import connection_manager
    assert connection_manager is not None
    assert hasattr(connection_manager, 'active_connections')
    assert hasattr(connection_manager, 'connect')
    assert hasattr(connection_manager, 'disconnect')
    assert hasattr(connection_manager, 'broadcast_to_scan')


@pytest.mark.asyncio
async def test_websocket_router_exists():
    """Test that WebSocket router is properly defined"""
    from app.api.endpoints.websocket import router
    assert router is not None
    assert router.prefix == ""
    # Check that routes are defined
    routes = [route for route in router.routes]
    assert len(routes) >= 2  # Should have at least 2 websocket routes
