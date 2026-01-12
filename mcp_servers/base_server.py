"""
Base MCP Server Template
Provides common functionality for all MCP servers
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod


class ToolRequest(BaseModel):
    """Standard tool execution request"""
    tool: str
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    """Standard tool execution response"""
    success: bool
    result: Any
    error: Optional[str] = None


class ToolDefinition(BaseModel):
    """Tool definition for discovery"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]


class BaseMCPServer(ABC):
    """
    Base class for MCP servers
    Provides common FastAPI setup and tool registration
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        port: int = 8000
    ):
        """
        Initialize MCP server
        
        Args:
            name: Server name
            description: Server description
            version: Server version
            port: Port to run on
        """
        self.name = name
        self.description = description
        self.version = version
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(
            title=name,
            description=description,
            version=version
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Tool registry
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[ToolDefinition] = []
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup standard MCP routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "name": self.name,
                "version": self.version
            }
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            return {
                "tools": [tool.dict() for tool in self.tool_definitions]
            }
        
        @self.app.post("/execute")
        async def execute_tool(request: ToolRequest):
            """Execute a tool"""
            try:
                if request.tool not in self.tools:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Tool '{request.tool}' not found"
                    )
                
                # Execute tool
                result = await self.tools[request.tool](request.parameters)
                
                return ToolResponse(
                    success=True,
                    result=result
                )
                
            except Exception as e:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=str(e)
                )
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        handler: Callable
    ):
        """
        Register a tool
        
        Args:
            name: Tool name
            description: Tool description
            parameters: List of parameter definitions
            handler: Async function to handle tool execution
        """
        self.tools[name] = handler
        self.tool_definitions.append(
            ToolDefinition(
                name=name,
                description=description,
                parameters=parameters
            )
        )
    
    @abstractmethod
    def setup_tools(self):
        """
        Setup server-specific tools
        Must be implemented by subclasses
        """
        pass
    
    def run(self):
        """Run the MCP server"""
        import uvicorn
        
        # Setup tools before running
        self.setup_tools()
        
        print(f"🚀 Starting {self.name} on port {self.port}")
        print(f"📝 {len(self.tools)} tools registered")
        
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
