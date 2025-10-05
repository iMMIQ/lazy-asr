import uuid
from fastapi import WebSocket, WebSocketDisconnect
from app.api.websocket import connection_manager
import logging

# Configure logging
logger = logging.getLogger(__name__)

# WebSocket endpoint function - to be registered directly in main.py
async def websocket_progress_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time progress updates
    
    Args:
        websocket: WebSocket connection
        task_id: Unique task identifier for this processing session
    """
    await websocket.accept()
    await connection_manager.connect(websocket, task_id)
    
    try:
        # Send connection confirmation
        await connection_manager.send_personal_message({
            "type": "connection",
            "message": "WebSocket connection established",
            "task_id": task_id
        }, task_id)
        
        logger.info(f"WebSocket connection established for task: {task_id}")
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for any incoming messages (client can send keep-alive or control messages)
            data = await websocket.receive_text()
            logger.debug(f"Received message from {task_id}: {data}")
            
            # Handle client messages if needed
            # Currently just keep connection alive
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {task_id}")
        connection_manager.disconnect(task_id)
    except Exception as e:
        logger.error(f"WebSocket error for {task_id}: {e}")
        connection_manager.disconnect(task_id)
