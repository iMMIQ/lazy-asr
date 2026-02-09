from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from app.core.websocket import connection_manager
from app.core.exceptions import ValidationError
from app.services.scan_service import scan_service
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Message type constants
WS_MSG_TYPE_STATUS = "status"
WS_MSG_TYPE_ERROR = "error"
WS_MSG_TYPE_PING = "ping"
WS_MSG_TYPE_PONG = "pong"

# Validation constants
MIN_SCAN_ID_LENGTH = 1
MAX_SCAN_ID_LENGTH = 100


def _validate_scan_id(scan_id: str) -> None:
    """
    Validate scan_id parameter.

    Args:
        scan_id: The scan ID to validate

    Raises:
        ValidationError: If scan_id is invalid
    """
    if not scan_id:
        raise ValidationError("scan_id cannot be empty", field="scan_id")
    if not (MIN_SCAN_ID_LENGTH <= len(scan_id) <= MAX_SCAN_ID_LENGTH):
        raise ValidationError(
            f"scan_id must be between {MIN_SCAN_ID_LENGTH} and {MAX_SCAN_ID_LENGTH} characters",
            field="scan_id"
        )
    # Check for potentially malicious characters
    if any(char in scan_id for char in ['\n', '\r', '\0', '<', '>', '&']):
        raise ValidationError("scan_id contains invalid characters", field="scan_id")


async def _handle_scan_websocket(websocket: WebSocket, scan_id: str) -> None:
    """
    Common WebSocket handler logic for scan updates.

    This helper function contains the shared logic for handling WebSocket connections
    that subscribe to scan updates. It handles initial status sending, message receiving,
    and connection lifecycle.

    Args:
        websocket: The WebSocket connection
        scan_id: The scan ID to subscribe to updates for

    Raises:
        WebSocketDisconnect: If the client disconnects
    """
    await connection_manager.connect(websocket, scan_id)

    try:
        # Send initial status
        initial_status = scan_service.get_scan_status(scan_id)
        if initial_status:
            await websocket.send_json({
                "type": WS_MSG_TYPE_STATUS,
                "data": initial_status.model_dump(mode='json')
            })
        else:
            await websocket.send_json({
                "type": WS_MSG_TYPE_ERROR,
                "message": f"Scan {scan_id} not found"
            })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                message = await websocket.receive_json()
                # Handle ping/heartbeat
                if message.get("type") == WS_MSG_TYPE_PING:
                    await websocket.send_json({"type": WS_MSG_TYPE_PONG})
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected during receive for scan {scan_id}")
                break
            except ValueError as e:
                # Invalid JSON received
                logger.warning(f"Invalid JSON received from WebSocket client for scan {scan_id}: {e}")
                await websocket.send_json({
                    "type": WS_MSG_TYPE_ERROR,
                    "message": "Invalid JSON message format"
                })
            except Exception as e:
                logger.warning(f"Error receiving WebSocket message for scan {scan_id}: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scan {scan_id}")
    finally:
        await connection_manager.disconnect(websocket, scan_id)


@router.websocket("/ws/scan/{scan_id}")
async def websocket_scan_updates(websocket: WebSocket, scan_id: str) -> None:
    """
    WebSocket endpoint for real-time scan status updates.

    Subscribe to updates for a specific scan by scan_id.
    Sends status updates as JSON messages.

    Args:
        websocket: The WebSocket connection
        scan_id: The scan ID to subscribe to (path parameter)
    """
    try:
        _validate_scan_id(scan_id)
    except ValidationError as e:
        await websocket.accept()
        await websocket.send_json({
            "type": WS_MSG_TYPE_ERROR,
            "message": e.message
        })
        await websocket.close()
        return

    await _handle_scan_websocket(websocket, scan_id)


@router.websocket("/ws")
async def websocket_general(websocket: WebSocket, scan_id: Optional[str] = Query(None)) -> None:
    """
    General WebSocket endpoint with scan_id as query parameter.

    Alternative to /ws/scan/{scan_id} for clients that prefer query params.

    Args:
        websocket: The WebSocket connection
        scan_id: The scan ID to subscribe to (query parameter)
    """
    if not scan_id:
        await websocket.accept()
        await websocket.send_json({
            "type": WS_MSG_TYPE_ERROR,
            "message": "scan_id query parameter is required"
        })
        await websocket.close()
        return

    try:
        _validate_scan_id(scan_id)
    except ValidationError as e:
        await websocket.accept()
        await websocket.send_json({
            "type": WS_MSG_TYPE_ERROR,
            "message": e.message
        })
        await websocket.close()
        return

    await _handle_scan_websocket(websocket, scan_id)
