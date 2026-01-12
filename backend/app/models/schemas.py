"""
Pydantic schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageSchema(BaseModel):
    """Message schema"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    """Conversation schema"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []
    
    class Config:
        from_attributes = True


class UserPreferenceSchema(BaseModel):
    """User preference schema"""
    user_id: str
    preferences: Dict[str, Any]
    
    class Config:
        from_attributes = True


class TaskHistorySchema(BaseModel):
    """Task history schema"""
    id: int
    conversation_id: int
    task_description: Optional[str] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InteractionLogSchema(BaseModel):
    """Interaction log schema"""
    user_id: str
    interaction_type: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
