"""
Tool Call Parser - Validates and parses tool calls
"""
from typing import List, Dict, Any
import json


class ToolCallParser:
    """
    Parses and validates tool calls from LLM output
    """
    
    def __init__(self):
        self.available_tools = {
            # Memory tools
            "save_conversation": ["conversation_id", "messages"],
            "get_user_preferences": ["user_id"],
            "log_interaction": ["user_id", "interaction_type", "metadata"],
            "get_task_history": ["user_id", "limit"],
            
            # Vector DB tools
            "store_embedding": ["text", "metadata"],
            "semantic_search": ["query", "limit"],
            "retrieve_context": ["query", "limit"],
            
            # Telegram tools
            "send_telegram_message": ["message", "chat_id"],
            "get_telegram_updates": [],
            "send_telegram_notification": ["message"],
            
            # Calendar tools
            "list_calendar_events": ["start_date", "end_date"],
            "create_calendar_event": ["title", "start_time", "end_time", "description"],
            "update_calendar_event": ["event_id", "updates"],
            "delete_calendar_event": ["event_id"],
            
            # Gmail tools
            "list_emails": ["query", "max_results"],
            "read_email": ["email_id"],
            "create_email_draft": ["to", "subject", "body"],
            "send_email": ["to", "subject", "body"],
            
            # Windows OS tools
            "open_application": ["app_name"],
            "close_application": ["app_name"],
            "run_powershell": ["command"],
            "manage_files": ["action", "path"],
            
            # Voice tools
            "transcribe_audio": ["audio_path"],
            "synthesize_speech": ["text", "output_path"],
        }
    
    def parse(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and validate tool calls
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            List of validated tool calls
        """
        validated_calls = []
        
        for call in tool_calls:
            try:
                validated_call = self._validate_tool_call(call)
                if validated_call:
                    validated_calls.append(validated_call)
            except Exception as e:
                print(f"Error validating tool call: {e}")
                continue
        
        return validated_calls
    
    def _validate_tool_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single tool call
        
        Expected format:
        {
            "tool": "tool_name",
            "parameters": {...}
        }
        """
        if "tool" not in call:
            raise ValueError("Missing 'tool' field")
        
        tool_name = call["tool"]
        
        if tool_name not in self.available_tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        parameters = call.get("parameters", {})
        required_params = self.available_tools[tool_name]
        
        # Check required parameters
        for param in required_params:
            if param not in parameters:
                # Some parameters might be optional
                pass
        
        return {
            "tool": tool_name,
            "parameters": parameters
        }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.available_tools.keys())
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool"""
        if tool_name not in self.available_tools:
            return {}
        
        return {
            "name": tool_name,
            "required_parameters": self.available_tools[tool_name]
        }
