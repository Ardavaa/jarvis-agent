"""
Task Planner - Creates execution plans
"""
from typing import Dict, List, Any, Optional
import json

from app.llm.ollama_client import OllamaClient
from app.llm.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE


class Planner:
    """
    Creates execution plans for user requests
    """
    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    async def create_plan(
        self,
        user_message: str,
        context: Optional[List[Dict[str, str]]] = None,
        observations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an execution plan for the user's request
        
        Args:
            user_message: User's input
            context: Conversation history
            observations: Previous observations from tool executions
            
        Returns:
            Dict containing plan, tool calls, and completion status
        """
        # Build context string
        context_str = ""
        if context:
            context_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in context[-5:]  # Last 5 messages
            ])
        
        # Build observations string
        observations_str = ""
        if observations:
            observations_str = "\n".join([
                f"Observation {i+1}: {obs}"
                for i, obs in enumerate(observations)
            ])
        
        # Format user prompt
        user_prompt = PLANNER_USER_TEMPLATE.format(
            user_message=user_message,
            context=context_str if context_str else "No previous context",
            observations=observations_str if observations_str else "No previous observations"
        )
        
        # Get plan from LLM
        response = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.7
        )
        
        # Parse response
        try:
            plan_data = self._parse_plan_response(response)
            return plan_data
        except Exception as e:
            print(f"Error parsing plan: {e}")
            return {
                "plan": "Unable to create plan",
                "is_complete": False,
                "tool_calls": [],
                "response": "I encountered an error while planning. Please try again."
            }
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured plan
        
        Expected format:
        {
            "plan": "Step-by-step plan",
            "is_complete": false,
            "tool_calls": [
                {
                    "tool": "tool_name",
                    "parameters": {...}
                }
            ],
            "response": "Optional response if complete"
        }
        """
        # Try to extract JSON from response
        try:
            # Look for JSON block
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            plan_data = json.loads(json_str)
            
            # Validate required fields
            if "plan" not in plan_data:
                plan_data["plan"] = "No plan provided"
            if "is_complete" not in plan_data:
                plan_data["is_complete"] = False
            if "tool_calls" not in plan_data:
                plan_data["tool_calls"] = []
            
            return plan_data
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            # Fallback: treat as simple response
            return {
                "plan": "Direct response",
                "is_complete": True,
                "tool_calls": [],
                "response": response
            }
