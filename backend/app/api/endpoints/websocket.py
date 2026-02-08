from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from app.core.websocket import connection_manager
from app.services.scan_service import scan_service
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/scan/{scan_id}")
async def websocket_scan_updates(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for real-time scan status updates.

    Subscribe to updates for a specific scan by scan_id.
    Sends status updates as JSON messages.
    """
    await connection_manager.connect(websocket, scan_id)

    try:
        # Send initial status
        initial_status = scan_service.get_scan_status(scan_id)
        if initial_status:
            await websocket.send_json({
                "type": "status",
                "data": initial_status.dict()
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Scan {scan_id} not found"
            })

        # Keep connection alive and handle incoming messages
        while True:
            # Receive and handle any client messages (e.g., ping)
            try:
                message = await websocket.receive_json()
                # Handle ping/heartbeat
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"Error receiving WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scan {scan_id}")
    finally:
        await connection_manager.disconnect(websocket, scan_id)


@router.websocket("/ws")
async def websocket_general(websocket: WebSocket, scan_id: Optional[str] = Query(None)):
    """
    General WebSocket endpoint with scan_id as query parameter.
    Alternative to /ws/scan/{scan_id} for clients that prefer query params.
    """
    if not scan_id:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": "scan_id query parameter is required"
        })
        await websocket.close()
        return

    # Delegate to the scan-specific handler
    # We need to handle this differently since we can't call another websocket handler
    await connection_manager.connect(websocket, scan_id)

    try:
        # Send initial status
        initial_status = scan_service.get_scan_status(scan_id)
        if initial_status:
            await websocket.send_json({
                "type": "status",
                "data": initial_status.dict()
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Scan {scan_id} not found"
            })

        while True:
            try:
                message = await websocket.receive_json()
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"Error receiving WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scan {scan_id}")
    finally:
        await connection_manager.disconnect(websocket, scan_id)
