"""
MCP Vector Database Server
Provides tools for semantic search and RAG
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mcp_servers.base_server import BaseMCPServer
from backend.app.memory.semantic import SemanticMemory
from typing import Dict, Any


class VectorDBServer(BaseMCPServer):
    """
    MCP server for vector database operations
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Vector Database Server",
            description="Provides semantic search and RAG capabilities",
            version="1.0.0",
            port=8002
        )
        
        # Initialize semantic memory
        self.memory = SemanticMemory()
    
    def setup_tools(self):
        """Register all vector database tools"""
        
        self.register_tool(
            name="store_embedding",
            description="Store text with embedding in vector database",
            parameters=[
                {"name": "text", "type": "string", "required": True},
                {"name": "metadata", "type": "object", "required": False},
                {"name": "memory_id", "type": "string", "required": False}
            ],
            handler=self.store_embedding
        )
        
        self.register_tool(
            name="semantic_search",
            description="Search for semantically similar content",
            parameters=[
                {"name": "query", "type": "string", "required": True},
                {"name": "limit", "type": "integer", "required": False},
                {"name": "filter_metadata", "type": "object", "required": False}
            ],
            handler=self.semantic_search
        )
        
        self.register_tool(
            name="retrieve_context",
            description="Retrieve relevant context for RAG",
            parameters=[
                {"name": "query", "type": "string", "required": True},
                {"name": "limit", "type": "integer", "required": False},
                {"name": "filter_metadata", "type": "object", "required": False}
            ],
            handler=self.retrieve_context
        )
        
        self.register_tool(
            name="add_conversation_to_memory",
            description="Add entire conversation to semantic memory",
            parameters=[
                {"name": "conversation_id", "type": "string", "required": True},
                {"name": "messages", "type": "array", "required": True},
                {"name": "user_id", "type": "string", "required": False}
            ],
            handler=self.add_conversation_to_memory
        )
        
        self.register_tool(
            name="get_conversation_context",
            description="Get relevant context from a specific conversation",
            parameters=[
                {"name": "conversation_id", "type": "string", "required": True},
                {"name": "query", "type": "string", "required": True},
                {"name": "limit", "type": "integer", "required": False}
            ],
            handler=self.get_conversation_context
        )
        
        self.register_tool(
            name="delete_memory",
            description="Delete a specific memory",
            parameters=[
                {"name": "memory_id", "type": "string", "required": True}
            ],
            handler=self.delete_memory
        )
        
        self.register_tool(
            name="get_memory_count",
            description="Get total number of memories",
            parameters=[],
            handler=self.get_memory_count
        )
    
    # Tool handlers
    
    async def store_embedding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store text with embedding"""
        text = params["text"]
        metadata = params.get("metadata")
        memory_id = params.get("memory_id")
        
        result_id = await self.memory.add_memory(text, metadata, memory_id)
        
        return {
            "memory_id": result_id,
            "text_length": len(text),
            "status": "stored"
        }
    
    async def semantic_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for semantically similar content"""
        query = params["query"]
        limit = params.get("limit", 5)
        filter_metadata = params.get("filter_metadata")
        
        results = await self.memory.search(query, limit, filter_metadata)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def retrieve_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for RAG"""
        query = params["query"]
        limit = params.get("limit", 3)
        filter_metadata = params.get("filter_metadata")
        
        context = await self.memory.retrieve_context(query, limit, filter_metadata)
        
        return {
            "query": query,
            "context": context,
            "has_context": context != "No relevant context found."
        }
    
    async def add_conversation_to_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add entire conversation to semantic memory"""
        conversation_id = params["conversation_id"]
        messages = params["messages"]
        user_id = params.get("user_id")
        
        memory_ids = await self.memory.add_conversation_to_memory(
            conversation_id,
            messages,
            user_id
        )
        
        return {
            "conversation_id": conversation_id,
            "memory_ids": memory_ids,
            "count": len(memory_ids),
            "status": "stored"
        }
    
    async def get_conversation_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context from a specific conversation"""
        conversation_id = params["conversation_id"]
        query = params["query"]
        limit = params.get("limit", 3)
        
        context = await self.memory.get_conversation_context(
            conversation_id,
            query,
            limit
        )
        
        return {
            "conversation_id": conversation_id,
            "query": query,
            "context": context,
            "has_context": context != "No relevant context found."
        }
    
    async def delete_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a specific memory"""
        memory_id = params["memory_id"]
        
        self.memory.delete_memory(memory_id)
        
        return {
            "memory_id": memory_id,
            "status": "deleted"
        }
    
    async def get_memory_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get total number of memories"""
        count = self.memory.get_memory_count()
        
        return {
            "total_memories": count
        }


if __name__ == "__main__":
    server = VectorDBServer()
    server.run()
