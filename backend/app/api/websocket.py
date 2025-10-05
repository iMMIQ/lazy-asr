import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections and broadcast messages"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Store WebSocket connection (acceptance already handled by endpoint)"""
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to {client_id}: {e}")
                    self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

# Global connection manager instance
connection_manager = ConnectionManager()

class ProgressPublisher:
    """Publish progress updates to WebSocket clients"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
    
    async def send_progress(self, 
                          step: str, 
                          message: str, 
                          progress: Optional[float] = None,
                          details: Optional[Dict[str, Any]] = None):
        """Send progress update to client"""
        progress_message = {
            "type": "progress",
            "task_id": self.task_id,
            "step": step,
            "message": message,
            "progress": progress,
            "details": details or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await connection_manager.send_personal_message(progress_message, self.task_id)
        logger.info(f"Progress update for {self.task_id}: {step} - {message}")
    
    async def send_log(self, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Send log message to client"""
        log_message = {
            "type": "log",
            "task_id": self.task_id,
            "level": level,
            "message": message,
            "details": details or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await connection_manager.send_personal_message(log_message, self.task_id)
    
    async def send_error(self, error_message: str, error_details: Optional[Dict[str, Any]] = None):
        """Send error message to client"""
        error_msg = {
            "type": "error",
            "task_id": self.task_id,
            "message": error_message,
            "details": error_details or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await connection_manager.send_personal_message(error_msg, self.task_id)
        logger.error(f"Error for {self.task_id}: {error_message}")
    
    async def send_completion(self, result: Dict[str, Any]):
        """Send completion message to client"""
        completion_message = {
            "type": "completion",
            "task_id": self.task_id,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await connection_manager.send_personal_message(completion_message, self.task_id)
        logger.info(f"Task completed: {self.task_id}")
