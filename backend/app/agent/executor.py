"""
Tool Executor - Executes validated tool calls
"""
from typing import List, Dict, Any
import asyncio

from app.mcp.client import MCPClient


class ToolExecutor:
    """
    Executes tool calls via MCP client
    """
    
    def __init__(self):
        self.mcp_client = MCPClient()
        
        # Map tools to MCP servers
        self.tool_to_server = {
            # Memory DB tools
            "save_conversation": "memory_db",
            "get_user_preferences": "memory_db",
            "log_interaction": "memory_db",
            "get_task_history": "memory_db",
            
            # Vector DB tools
            "store_embedding": "vector_db",
            "semantic_search": "vector_db",
            "retrieve_context": "vector_db",
            
            # Telegram tools
            "send_telegram_message": "telegram",
            "get_telegram_updates": "telegram",
            "send_telegram_notification": "telegram",
            
            # Calendar tools
            "list_calendar_events": "calendar",
            "create_calendar_event": "calendar",
            "update_calendar_event": "calendar",
            "delete_calendar_event": "calendar",
            
            # Gmail tools
            "list_emails": "gmail",
            "read_email": "gmail",
            "create_email_draft": "gmail",
            "send_email": "gmail",
            
            # Windows OS tools
            "open_application": "windows_os",
            "close_application": "windows_os",
            "run_powershell": "windows_os",
            "manage_files": "windows_os",
            
            # Voice tools
            "transcribe_audio": "voice",
            "synthesize_speech": "voice",
        }
    
    async def execute_tools(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls
        
        Args:
            tool_calls: List of validated tool calls
            
        Returns:
            List of execution results
        """
        tasks = [
            self._execute_single_tool(call)
            for call in tool_calls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            {
                "tool": tool_calls[i]["tool"],
                "success": not isinstance(result, Exception),
                "result": str(result) if isinstance(result, Exception) else result,
                "error": str(result) if isinstance(result, Exception) else None
            }
            for i, result in enumerate(results)
        ]
    
    async def _execute_single_tool(
        self,
        tool_call: Dict[str, Any]
    ) -> Any:
        """
        Execute a single tool call
        
        Args:
            tool_call: Validated tool call
            
        Returns:
            Tool execution result
        """
        tool_name = tool_call["tool"]
        parameters = tool_call["parameters"]
        
        # Get MCP server for this tool
        server_name = self.tool_to_server.get(tool_name)
        
        if not server_name:
            raise ValueError(f"No MCP server found for tool: {tool_name}")
        
        try:
            # Execute via MCP client
            result = await self.mcp_client.call_tool(
                server=server_name,
                tool=tool_name,
                parameters=parameters
            )
            return result
            
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            raise
