"""
WebSocket API for real-time chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import uuid

from app.llm.ollama_client import OllamaClient
from app.agent.core import Agent

router = APIRouter()

# Active connections
active_connections: Set[WebSocket] = set()

# Global instances
llm_client = OllamaClient()
agent = Agent(llm_client)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Remove connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    """
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        await manager.send_message(client_id, {
            "type": "connection",
            "status": "connected",
            "client_id": client_id
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "chat":
                # Process chat message
                user_message = data.get("message")
                conversation_id = data.get("conversation_id", str(uuid.uuid4()))
                context = data.get("context", [])
                
                # Send acknowledgment
                await manager.send_message(client_id, {
                    "type": "processing",
                    "status": "processing"
                })
                
                try:
                    # Run agent
                    result = await agent.run(
                        user_message=user_message,
                        conversation_id=conversation_id,
                        context=context
                    )
                    
                    # Send response
                    await manager.send_message(client_id, {
                        "type": "response",
                        "response": result["response"],
                        "conversation_id": result["conversation_id"],
                        "iterations": result["iterations"],
                        "plan": result.get("plan")
                    })
                    
                except Exception as e:
                    # Send error
                    await manager.send_message(client_id, {
                        "type": "error",
                        "error": str(e)
                    })
            
            elif message_type == "ping":
                # Respond to ping
                await manager.send_message(client_id, {
                    "type": "pong"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client {client_id} disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)
