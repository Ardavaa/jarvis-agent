"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.llm.ollama_client import OllamaClient
from app.agent.core import Agent

router = APIRouter()

# Global instances (will be properly initialized in lifespan)
llm_client = OllamaClient()
agent = Agent(llm_client)


class Message(BaseModel):
    """Message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_id: Optional[str] = None
    context: Optional[List[Message]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    conversation_id: str
    iterations: int
    plan: Optional[str] = None


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to JARVIS
    
    Args:
        request: Chat request with message and optional context
        
    Returns:
        Chat response with agent's reply
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Convert context to dict format
        context = None
        if request.context:
            context = [
                {"role": msg.role, "content": msg.content}
                for msg in request.context
            ]
        
        # Run agent
        result = await agent.run(
            user_message=request.message,
            conversation_id=conversation_id,
            context=context
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            iterations=result["iterations"],
            plan=result.get("plan")
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health():
    """Check chat service health"""
    ollama_healthy = await llm_client.check_health()
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama": ollama_healthy
    }
