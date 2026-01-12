"""
Semantic Memory - RAG with ChromaDB and embeddings
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import os

from app.llm.ollama_client import OllamaClient
from app.config import settings as app_settings


class SemanticMemory:
    """
    Manages semantic memory using ChromaDB for vector storage
    Implements Retrieval-Augmented Generation (RAG)
    """
    
    def __init__(
        self,
        collection_name: str = "jarvis_memory",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize semantic memory
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist vector database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or app_settings.vector_db_path
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "JARVIS semantic memory"}
        )
        
        # Initialize Ollama client for embeddings
        self.llm_client = OllamaClient()
    
    async def add_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to semantic storage
        
        Args:
            text: Text content to store
            metadata: Optional metadata (conversation_id, timestamp, source, etc.)
            memory_id: Optional custom ID, auto-generated if not provided
            
        Returns:
            Memory ID
        """
        # Generate embedding
        embedding = await self.llm_client.embed(text)
        
        # Generate ID if not provided
        if not memory_id:
            import uuid
            memory_id = str(uuid.uuid4())
        
        # Prepare metadata
        meta = metadata or {}
        meta["text_length"] = len(text)
        
        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[meta],
            ids=[memory_id]
        )
        
        return memory_id
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories
        
        Args:
            query: Search query
            limit: Maximum number of results
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant memories with scores
        """
        # Generate query embedding
        query_embedding = await self.llm_client.embed(query)
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=filter_metadata
        )
        
        # Format results
        memories = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                memory = {
                    "id": results["ids"][0][i],
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                }
                memories.append(memory)
        
        return memories
    
    async def retrieve_context(
        self,
        query: str,
        limit: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Retrieve relevant context for RAG
        
        Args:
            query: Query to find relevant context for
            limit: Maximum number of memories to retrieve
            filter_metadata: Optional metadata filters
            
        Returns:
            Formatted context string
        """
        memories = await self.search(query, limit, filter_metadata)
        
        if not memories:
            return "No relevant context found."
        
        # Format context
        context_parts = []
        for i, memory in enumerate(memories, 1):
            context_parts.append(f"[Context {i}]\n{memory['text']}")
        
        return "\n\n".join(context_parts)
    
    def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory
        
        Args:
            memory_id: Memory ID to delete
        """
        self.collection.delete(ids=[memory_id])
    
    def delete_by_metadata(self, filter_metadata: Dict[str, Any]) -> None:
        """
        Delete memories by metadata filter
        
        Args:
            filter_metadata: Metadata filter
        """
        self.collection.delete(where=filter_metadata)
    
    def get_memory_count(self) -> int:
        """
        Get total number of memories
        
        Returns:
            Number of memories in collection
        """
        return self.collection.count()
    
    def clear_all(self) -> None:
        """
        Clear all memories (use with caution!)
        """
        # Delete and recreate collection
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "JARVIS semantic memory"}
        )
    
    async def add_conversation_to_memory(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None
    ) -> List[str]:
        """
        Add entire conversation to semantic memory
        
        Args:
            conversation_id: Conversation identifier
            messages: List of messages (role + content)
            user_id: Optional user identifier
            
        Returns:
            List of memory IDs
        """
        memory_ids = []
        
        for i, message in enumerate(messages):
            # Create searchable text
            text = f"{message['role']}: {message['content']}"
            
            # Metadata
            metadata = {
                "conversation_id": conversation_id,
                "message_index": i,
                "role": message["role"]
            }
            
            if user_id:
                metadata["user_id"] = user_id
            
            # Add to memory
            memory_id = await self.add_memory(text, metadata)
            memory_ids.append(memory_id)
        
        return memory_ids
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        query: str,
        limit: int = 3
    ) -> str:
        """
        Get relevant context from a specific conversation
        
        Args:
            conversation_id: Conversation identifier
            query: Query to search for
            limit: Maximum number of results
            
        Returns:
            Formatted context string
        """
        filter_metadata = {"conversation_id": conversation_id}
        return await self.retrieve_context(query, limit, filter_metadata)
