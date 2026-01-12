"""
Enhanced Chat API endpoints with memory integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.llm.ollama_client import OllamaClient
from app.agent.enhanced_core import EnhancedAgent

router = APIRouter()

# Global instances (will be properly initialized in lifespan)
llm_client = OllamaClient()
agent = EnhancedAgent(llm_client, enable_semantic_memory=True)


class Message(BaseModel):
    """Message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "default_user"
    use_semantic_memory: bool = True


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    conversation_id: str
    iterations: int
    plan: Optional[str] = None
    memory_stats: Optional[dict] = None


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to JARVIS with memory integration
    
    Args:
        request: Chat request with message and optional context
        
    Returns:
        Chat response with agent's reply and memory stats
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Run enhanced agent
        result = await agent.run(
            user_message=request.message,
            conversation_id=conversation_id,
            user_id=request.user_id,
            use_semantic_memory=request.use_semantic_memory
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            iterations=result["iterations"],
            plan=result.get("plan"),
            memory_stats=result.get("memory_stats")
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear a conversation from short-term memory
    
    Args:
        conversation_id: Conversation ID to clear
        
    Returns:
        Success message
    """
    try:
        agent.clear_conversation(conversation_id)
        return {"message": f"Conversation {conversation_id} cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health():
    """Check chat service health"""
    ollama_healthy = await llm_client.check_health()
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama": ollama_healthy,
        "memory_systems": {
            "short_term": "active",
            "long_term": "active",
            "semantic": "active" if agent.semantic_memory else "disabled"
        }
    }
