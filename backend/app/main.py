"""
FastAPI main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import chat, voice, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📡 Ollama URL: {settings.ollama_base_url}")
    print(f"🤖 Model: {settings.ollama_model}")
    
    # TODO: Initialize database connections
    # TODO: Initialize MCP client
    # TODO: Verify Ollama connection
    
    yield
    
    # Shutdown
    print("👋 Shutting down JARVIS")
    # TODO: Close database connections
    # TODO: Close MCP connections


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multimodal Agentic AI Assistant",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama_url": settings.ollama_base_url,
        "model": settings.ollama_model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
