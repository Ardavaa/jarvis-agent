"""
Long-term Memory - Persistent storage in relational database
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import (
    Conversation, Message, UserPreference,
    TaskHistory, InteractionLog, SessionLocal
)


class LongTermMemory:
    """
    Manages long-term memory using relational database
    Stores conversations, preferences, tasks, and interaction logs
    """
    
    def __init__(self):
        """Initialize long-term memory"""
        pass
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    # ==================== Conversation Management ====================
    
    def create_conversation(self, user_id: str) -> int:
        """
        Create a new conversation
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation ID
        """
        db = self._get_db()
        try:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation.id
        finally:
            db.close()
    
    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save a message to database
        
        Args:
            conversation_id: Conversation ID
            role: Message role
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Message ID
        """
        db = self._get_db()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                extra_data=metadata
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message.id
        finally:
            db.close()
    
    def get_conversation_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages
            
        Returns:
            List of messages
        """
        db = self._get_db()
        try:
            query = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            
            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.extra_data,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
        finally:
            db.close()
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user's recent conversations
        
        Args:
            user_id: User identifier
            limit: Number of conversations to return
            
        Returns:
            List of conversations
        """
        db = self._get_db()
        try:
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": conv.id,
                    "user_id": conv.user_id,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                    "message_count": len(conv.messages)
                }
                for conv in conversations
            ]
        finally:
            db.close()
    
    # ==================== User Preferences ====================
    
    def save_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """
        Save or update user preferences
        
        Args:
            user_id: User identifier
            preferences: User preferences dictionary
        """
        db = self._get_db()
        try:
            pref = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if pref:
                pref.preferences = preferences
            else:
                pref = UserPreference(
                    user_id=user_id,
                    preferences=preferences
                )
                db.add(pref)
            
            db.commit()
        finally:
            db.close()
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences dictionary
        """
        db = self._get_db()
        try:
            pref = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            return pref.preferences if pref and pref.preferences else {}
        finally:
            db.close()
    
    # ==================== Task History ====================
    
    def save_task(
        self,
        conversation_id: int,
        task_description: str,
        tools_used: List[Dict[str, Any]],
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save task execution history
        
        Args:
            conversation_id: Conversation ID
            task_description: Description of the task
            tools_used: List of tools that were used
            status: Task status (pending, completed, failed)
            result: Optional task result
            
        Returns:
            Task ID
        """
        db = self._get_db()
        try:
            task = TaskHistory(
                conversation_id=conversation_id,
                task_description=task_description,
                tools_used=tools_used,
                status=status,
                result=result
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task.id
        finally:
            db.close()
    
    def get_task_history(
        self,
        conversation_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get task execution history
        
        Args:
            conversation_id: Optional conversation ID filter
            limit: Number of tasks to return
            
        Returns:
            List of tasks
        """
        db = self._get_db()
        try:
            query = db.query(TaskHistory)
            
            if conversation_id:
                query = query.filter(TaskHistory.conversation_id == conversation_id)
            
            tasks = query.order_by(TaskHistory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": task.id,
                    "conversation_id": task.conversation_id,
                    "task_description": task.task_description,
                    "tools_used": task.tools_used,
                    "status": task.status,
                    "result": task.result,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ]
        finally:
            db.close()
    
    # ==================== Interaction Logs ====================
    
    def log_interaction(
        self,
        user_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log user interaction
        
        Args:
            user_id: User identifier
            interaction_type: Type of interaction (chat, voice, telegram)
            metadata: Optional metadata
            
        Returns:
            Log ID
        """
        db = self._get_db()
        try:
            log = InteractionLog(
                user_id=user_id,
                interaction_type=interaction_type,
                extra_data=metadata
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log.id
        finally:
            db.close()
    
    def get_interaction_logs(
        self,
        user_id: str,
        interaction_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get interaction logs
        
        Args:
            user_id: User identifier
            interaction_type: Optional interaction type filter
            limit: Number of logs to return
            
        Returns:
            List of interaction logs
        """
        db = self._get_db()
        try:
            query = db.query(InteractionLog).filter(
                InteractionLog.user_id == user_id
            )
            
            if interaction_type:
                query = query.filter(InteractionLog.interaction_type == interaction_type)
            
            logs = query.order_by(InteractionLog.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "interaction_type": log.interaction_type,
                    "metadata": log.extra_data,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        finally:
            db.close()
