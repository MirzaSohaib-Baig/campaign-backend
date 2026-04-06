# app/core/websocket_manager.py
from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        # user_id -> list of active WebSocket connections
        self.active: Dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active:
            self.active[user_id] = []
        self.active[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active:
            self.active[user_id].remove(websocket)
            if not self.active[user_id]:
                del self.active[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        connections = self.active.get(user_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        # Clean up dead connections
        for ws in dead:
            connections.remove(ws)

# Single shared instance
ws_manager = WebSocketManager()