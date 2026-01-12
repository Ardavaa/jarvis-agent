"""
MCP Client - Communicates with MCP servers
"""
from typing import Dict, Any, Optional
import aiohttp

from app.config import settings


class MCPClient:
    """
    Client for communicating with MCP servers
    """
    
    def __init__(self):
        self.server_urls = {
            "memory_db": settings.mcp_memory_db_url,
            "vector_db": settings.mcp_vector_db_url,
            "telegram": settings.mcp_telegram_url,
            "calendar": settings.mcp_calendar_url,
            "gmail": settings.mcp_gmail_url,
            "windows_os": settings.mcp_windows_os_url,
            "voice": settings.mcp_voice_url,
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def call_tool(
        self,
        server: str,
        tool: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        Call a tool on an MCP server
        
        Args:
            server: Server name (e.g., 'memory_db', 'telegram')
            tool: Tool name
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        if server not in self.server_urls:
            raise ValueError(f"Unknown MCP server: {server}")
        
        server_url = self.server_urls[server]
        session = await self._get_session()
        
        payload = {
            "tool": tool,
            "parameters": parameters
        }
        
        try:
            async with session.post(
                f"{server_url}/execute",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result")
                
        except aiohttp.ClientError as e:
            print(f"MCP server error ({server}): {e}")
            raise
        except Exception as e:
            print(f"Unexpected error calling {server}: {e}")
            raise
    
    async def list_tools(self, server: str) -> list[Dict[str, Any]]:
        """
        List available tools on an MCP server
        
        Args:
            server: Server name
            
        Returns:
            List of available tools
        """
        if server not in self.server_urls:
            raise ValueError(f"Unknown MCP server: {server}")
        
        server_url = self.server_urls[server]
        session = await self._get_session()
        
        try:
            async with session.get(f"{server_url}/tools") as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("tools", [])
                
        except aiohttp.ClientError as e:
            print(f"MCP server error ({server}): {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    async def check_server_health(self, server: str) -> bool:
        """
        Check if an MCP server is healthy
        
        Args:
            server: Server name
            
        Returns:
            True if healthy, False otherwise
        """
        if server not in self.server_urls:
            return False
        
        server_url = self.server_urls[server]
        session = await self._get_session()
        
        try:
            async with session.get(f"{server_url}/health") as response:
                return response.status == 200
        except Exception:
            return False
