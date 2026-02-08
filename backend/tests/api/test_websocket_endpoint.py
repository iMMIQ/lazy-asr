"""
Tests for WebSocket endpoint

Tests WebSocket connectivity, validation, and basic functionality.
"""
import pytest
from app.core.exceptions import ValidationError
from app.api.endpoints.websocket import (
    _validate_scan_id,
    WS_MSG_TYPE_STATUS,
    WS_MSG_TYPE_ERROR,
    WS_MSG_TYPE_PING,
    WS_MSG_TYPE_PONG,
    MIN_SCAN_ID_LENGTH,
    MAX_SCAN_ID_LENGTH,
)


class TestValidateScanId:
    """Test scan_id validation function"""

    def test_validate_scan_id_valid(self):
        """Test validation with valid scan IDs"""
        # Valid UUID-like string
        _validate_scan_id("abc123-def456-ghi789")
        # Valid simple string
        _validate_scan_id("my-scan-123")
        # Minimum length
        _validate_scan_id("a")
        # Maximum length
        _validate_scan_id("a" * MAX_SCAN_ID_LENGTH)

    def test_validate_scan_id_empty(self):
        """Test validation fails with empty scan_id"""
        with pytest.raises(ValidationError) as exc_info:
            _validate_scan_id("")
        assert "cannot be empty" in exc_info.value.message
        assert exc_info.value.field == "scan_id"

    def test_validate_scan_id_too_long(self):
        """Test validation fails with too long scan_id"""
        with pytest.raises(ValidationError) as exc_info:
            _validate_scan_id("a" * (MAX_SCAN_ID_LENGTH + 1))
        assert "between" in exc_info.value.message.lower()
        assert exc_info.value.field == "scan_id"

    def test_validate_scan_id_invalid_characters(self):
        """Test validation fails with potentially malicious characters"""
        invalid_chars = ['\n', '\r', '\0', '<', '>', '&']
        for char in invalid_chars:
            with pytest.raises(ValidationError) as exc_info:
                _validate_scan_id(f"valid{char}content")
            assert "invalid characters" in exc_info.value.message.lower()


class TestMessageConstants:
    """Test WebSocket message type constants"""

    def test_status_constant(self):
        """Test status message constant"""
        assert WS_MSG_TYPE_STATUS == "status"

    def test_error_constant(self):
        """Test error message constant"""
        assert WS_MSG_TYPE_ERROR == "error"

    def test_ping_constant(self):
        """Test ping message constant"""
        assert WS_MSG_TYPE_PING == "ping"

    def test_pong_constant(self):
        """Test pong message constant"""
        assert WS_MSG_TYPE_PONG == "pong"


class TestConnectionManagerExists:
    """Test that connection_manager is properly instantiated"""

    @pytest.mark.asyncio
    async def test_connection_manager_exists(self):
        """Test that connection_manager is properly instantiated"""
        from app.core.websocket import connection_manager
        assert connection_manager is not None
        assert hasattr(connection_manager, 'active_connections')
        assert hasattr(connection_manager, 'connect')
        assert hasattr(connection_manager, 'disconnect')
        assert hasattr(connection_manager, 'broadcast_to_scan')


class TestWebsocketRouterExists:
    """Test that WebSocket router is properly defined"""

    @pytest.mark.asyncio
    async def test_websocket_router_exists(self):
        """Test that WebSocket router is properly defined"""
        from app.api.endpoints.websocket import router
        assert router is not None
        assert router.prefix == ""
        # Check that routes are defined
        routes = [route for route in router.routes]
        assert len(routes) >= 2  # Should have at least 2 websocket routes

    @pytest.mark.asyncio
    async def test_websocket_router_has_helper_function(self):
        """Test that the helper function exists and is callable"""
        from app.api.endpoints.websocket import _handle_scan_websocket
        assert _handle_scan_websocket is not None
        assert callable(_handle_scan_websocket)


class TestValidationConstants:
    """Test validation constants"""

    def test_min_scan_id_length(self):
        """Test minimum scan ID length constant"""
        assert isinstance(MIN_SCAN_ID_LENGTH, int)
        assert MIN_SCAN_ID_LENGTH >= 1

    def test_max_scan_id_length(self):
        """Test maximum scan ID length constant"""
        assert isinstance(MAX_SCAN_ID_LENGTH, int)
        assert MAX_SCAN_ID_LENGTH > MIN_SCAN_ID_LENGTH
