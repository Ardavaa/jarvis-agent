"""
Short-term Memory - Conversation context management
"""
from typing import List, Dict, Any, Optional
from collections import deque


class ShortTermMemory:
    """
    Manages short-term conversation context
    Uses in-memory storage with configurable window size
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize short-term memory
        
        Args:
            max_messages: Maximum number of messages to keep in context
        """
        self.max_messages = max_messages
        self.conversations: Dict[str, deque] = {}
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to conversation context
        
        Args:
            conversation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = deque(maxlen=self.max_messages)
        
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.conversations[conversation_id].append(message)
    
    def get_context(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation context
        
        Args:
            conversation_id: Unique conversation identifier
            max_messages: Optional limit on number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        if conversation_id not in self.conversations:
            return []
        
        messages = list(self.conversations[conversation_id])
        
        if max_messages:
            messages = messages[-max_messages:]
        
        return messages
    
    def clear_context(self, conversation_id: str) -> None:
        """
        Clear conversation context
        
        Args:
            conversation_id: Unique conversation identifier
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_last_message(
        self,
        conversation_id: str,
        role: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the last message in conversation
        
        Args:
            conversation_id: Unique conversation identifier
            role: Optional role filter
            
        Returns:
            Last message or None
        """
        messages = self.get_context(conversation_id)
        
        if not messages:
            return None
        
        if role:
            # Find last message with specified role
            for message in reversed(messages):
                if message["role"] == role:
                    return message
            return None
        
        return messages[-1]
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation summary statistics
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Summary statistics
        """
        messages = self.get_context(conversation_id)
        
        if not messages:
            return {
                "message_count": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "system_messages": 0
            }
        
        role_counts = {}
        for message in messages:
            role = message["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "message_count": len(messages),
            "user_messages": role_counts.get("user", 0),
            "assistant_messages": role_counts.get("assistant", 0),
            "system_messages": role_counts.get("system", 0),
            "roles": role_counts
        }
    
    def format_for_llm(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Format conversation context for LLM input
        
        Args:
            conversation_id: Unique conversation identifier
            max_messages: Optional limit on messages
            
        Returns:
            List of messages formatted for LLM (role + content only)
        """
        messages = self.get_context(conversation_id, max_messages)
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
