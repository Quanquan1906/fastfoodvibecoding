"""WebSocket handlers - moved from old websocket/manager.py"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict
import json


class ConnectionManager:
    """Manage WebSocket connections for order tracking"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, order_id: str, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        if order_id not in self.active_connections:
            self.active_connections[order_id] = set()
        
        self.active_connections[order_id].add(websocket)
        print(f"✅ WebSocket connected: {order_id}")

    def disconnect(self, order_id: str, websocket: WebSocket):
        """Disconnect WebSocket"""
        if order_id in self.active_connections:
            self.active_connections[order_id].discard(websocket)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]
        print(f"❌ WebSocket disconnected: {order_id}")

    async def broadcast_order_update(self, order_id: str, order_data: dict):
        """Broadcast order update to all connected clients"""
        if order_id in self.active_connections:
            for connection in list(self.active_connections[order_id]):
                try:
                    await connection.send_json(order_data)
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
                    self.disconnect(order_id, connection)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)


# Global connection manager
manager = ConnectionManager()
