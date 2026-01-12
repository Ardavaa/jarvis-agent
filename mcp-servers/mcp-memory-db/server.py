"""
MCP Memory Database Server
Provides tools for conversation storage, preferences, and interaction logging
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mcp_servers.base_server import BaseMCPServer
from backend.app.memory.long_term import LongTermMemory
from typing import Dict, Any


class MemoryDBServer(BaseMCPServer):
    """
    MCP server for memory database operations
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Memory Database Server",
            description="Provides access to long-term memory storage",
            version="1.0.0",
            port=8001
        )
        
        # Initialize long-term memory
        self.memory = LongTermMemory()
    
    def setup_tools(self):
        """Register all memory database tools"""
        
        # Conversation tools
        self.register_tool(
            name="save_conversation",
            description="Save a conversation with messages",
            parameters=[
                {"name": "user_id", "type": "string", "required": True},
                {"name": "messages", "type": "array", "required": True}
            ],
            handler=self.save_conversation
        )
        
        self.register_tool(
            name="get_conversation_messages",
            description="Get messages from a conversation",
            parameters=[
                {"name": "conversation_id", "type": "integer", "required": True},
                {"name": "limit", "type": "integer", "required": False}
            ],
            handler=self.get_conversation_messages
        )
        
        self.register_tool(
            name="get_user_conversations",
            description="Get user's recent conversations",
            parameters=[
                {"name": "user_id", "type": "string", "required": True},
                {"name": "limit", "type": "integer", "required": False}
            ],
            handler=self.get_user_conversations
        )
        
        # Preference tools
        self.register_tool(
            name="get_user_preferences",
            description="Get user preferences",
            parameters=[
                {"name": "user_id", "type": "string", "required": True}
            ],
            handler=self.get_user_preferences
        )
        
        self.register_tool(
            name="save_user_preferences",
            description="Save user preferences",
            parameters=[
                {"name": "user_id", "type": "string", "required": True},
                {"name": "preferences", "type": "object", "required": True}
            ],
            handler=self.save_user_preferences
        )
        
        # Task history tools
        self.register_tool(
            name="get_task_history",
            description="Get task execution history",
            parameters=[
                {"name": "user_id", "type": "string", "required": False},
                {"name": "conversation_id", "type": "integer", "required": False},
                {"name": "limit", "type": "integer", "required": False}
            ],
            handler=self.get_task_history
        )
        
        # Interaction logging tools
        self.register_tool(
            name="log_interaction",
            description="Log a user interaction",
            parameters=[
                {"name": "user_id", "type": "string", "required": True},
                {"name": "interaction_type", "type": "string", "required": True},
                {"name": "metadata", "type": "object", "required": False}
            ],
            handler=self.log_interaction
        )
        
        self.register_tool(
            name="get_interaction_logs",
            description="Get interaction logs",
            parameters=[
                {"name": "user_id", "type": "string", "required": True},
                {"name": "interaction_type", "type": "string", "required": False},
                {"name": "limit", "type": "integer", "required": False}
            ],
            handler=self.get_interaction_logs
        )
    
    # Tool handlers
    
    async def save_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save a conversation with messages"""
        user_id = params["user_id"]
        messages = params["messages"]
        
        # Create conversation
        conv_id = self.memory.create_conversation(user_id)
        
        # Save messages
        message_ids = []
        for msg in messages:
            msg_id = self.memory.save_message(
                conversation_id=conv_id,
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                metadata=msg.get("metadata")
            )
            message_ids.append(msg_id)
        
        return {
            "conversation_id": conv_id,
            "message_ids": message_ids,
            "message_count": len(message_ids)
        }
    
    async def get_conversation_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages from a conversation"""
        conversation_id = params["conversation_id"]
        limit = params.get("limit")
        
        messages = self.memory.get_conversation_messages(conversation_id, limit)
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "count": len(messages)
        }
    
    async def get_user_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user's recent conversations"""
        user_id = params["user_id"]
        limit = params.get("limit", 10)
        
        conversations = self.memory.get_user_conversations(user_id, limit)
        
        return {
            "user_id": user_id,
            "conversations": conversations,
            "count": len(conversations)
        }
    
    async def get_user_preferences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user preferences"""
        user_id = params["user_id"]
        
        preferences = self.memory.get_user_preferences(user_id)
        
        return {
            "user_id": user_id,
            "preferences": preferences
        }
    
    async def save_user_preferences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save user preferences"""
        user_id = params["user_id"]
        preferences = params["preferences"]
        
        self.memory.save_user_preferences(user_id, preferences)
        
        return {
            "user_id": user_id,
            "status": "saved",
            "preferences": preferences
        }
    
    async def get_task_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get task execution history"""
        conversation_id = params.get("conversation_id")
        limit = params.get("limit", 10)
        
        tasks = self.memory.get_task_history(conversation_id, limit)
        
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
    
    async def log_interaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Log a user interaction"""
        user_id = params["user_id"]
        interaction_type = params["interaction_type"]
        metadata = params.get("metadata")
        
        log_id = self.memory.log_interaction(user_id, interaction_type, metadata)
        
        return {
            "log_id": log_id,
            "user_id": user_id,
            "interaction_type": interaction_type,
            "status": "logged"
        }
    
    async def get_interaction_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get interaction logs"""
        user_id = params["user_id"]
        interaction_type = params.get("interaction_type")
        limit = params.get("limit", 50)
        
        logs = self.memory.get_interaction_logs(user_id, interaction_type, limit)
        
        return {
            "user_id": user_id,
            "logs": logs,
            "count": len(logs)
        }


if __name__ == "__main__":
    server = MemoryDBServer()
    server.run()
