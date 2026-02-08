"""
WebSocket connection manager for real-time updates
"""
from typing import Dict, Set
from fastapi import WebSocket
from app.core.logger import get_logger


logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # scan_id -> set of connected websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, scan_id: str):
        """Connect a new websocket client to subscribe to scan updates"""
        # Accept the WebSocket connection if it's not already accepted
        if hasattr(websocket, 'accept'):
            try:
                await websocket.accept()
            except Exception:
                # Already accepted or mock object for testing
                pass

        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = set()
        self.active_connections[scan_id].add(websocket)
        logger.info(f"WebSocket connected for scan {scan_id}. Total subscribers: {len(self.active_connections[scan_id])}")

    async def disconnect(self, websocket: WebSocket, scan_id: str):
        """Disconnect a websocket client"""
        if scan_id in self.active_connections:
            self.active_connections[scan_id].discard(websocket)
            # Clean up empty sets
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]
            logger.info(f"WebSocket disconnected for scan {scan_id}")

    async def broadcast_to_scan(self, scan_id: str, message: dict):
        """Broadcast a message to all subscribers of a specific scan"""
        if scan_id not in self.active_connections:
            return

        # Create a copy to avoid modification during iteration
        websockets = list(self.active_connections[scan_id])
        disconnected = []

        for websocket in websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.append(websocket)

        # Remove disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws, scan_id)

    async def get_scan_subscriber_count(self, scan_id: str) -> int:
        """Get the number of subscribers for a scan"""
        return len(self.active_connections.get(scan_id, set()))

    def is_scan_active(self, scan_id: str) -> bool:
        """Check if a scan has any active subscribers"""
        return scan_id in self.active_connections and len(self.active_connections[scan_id]) > 0


# Global connection manager instance
connection_manager = ConnectionManager()
