"""
Observer - Processes tool execution results
"""
from typing import List, Dict, Any
import json

from app.llm.ollama_client import OllamaClient
from app.llm.prompts import OBSERVER_SYSTEM_PROMPT, OBSERVER_USER_TEMPLATE


class Observer:
    """
    Observes tool execution results and decides next actions
    """
    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    async def observe(
        self,
        plan: str,
        tool_calls: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process tool execution results and determine next action
        
        Args:
            plan: Original execution plan
            tool_calls: Tools that were called
            execution_results: Results from tool executions
            
        Returns:
            Dict containing observation and next action decision
        """
        # Format results for LLM
        results_str = self._format_results(tool_calls, execution_results)
        
        # Build prompt
        user_prompt = OBSERVER_USER_TEMPLATE.format(
            plan=plan,
            results=results_str
        )
        
        # Get observation from LLM
        response = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=OBSERVER_SYSTEM_PROMPT,
            temperature=0.5
        )
        
        # Parse observation
        try:
            observation_data = self._parse_observation(response)
            return observation_data
        except Exception as e:
            print(f"Error parsing observation: {e}")
            return {
                "observation": "Unable to process results",
                "should_finish": True,
                "response": "I encountered an error processing the results."
            }
    
    def _format_results(
        self,
        tool_calls: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]]
    ) -> str:
        """Format tool execution results for LLM"""
        formatted = []
        
        for i, (call, result) in enumerate(zip(tool_calls, execution_results)):
            status = "✓ Success" if result["success"] else "✗ Failed"
            formatted.append(
                f"{i+1}. Tool: {call['tool']}\n"
                f"   Status: {status}\n"
                f"   Result: {result.get('result', 'No result')}\n"
                f"   Error: {result.get('error', 'None')}"
            )
        
        return "\n\n".join(formatted)
    
    def _parse_observation(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM observation response
        
        Expected format:
        {
            "observation": "Analysis of results",
            "should_finish": true/false,
            "response": "Final response if should_finish is true",
            "next_action": "What to do next if should_finish is false"
        }
        """
        try:
            # Extract JSON
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
            
            observation_data = json.loads(json_str)
            
            # Validate fields
            if "observation" not in observation_data:
                observation_data["observation"] = "No observation"
            if "should_finish" not in observation_data:
                observation_data["should_finish"] = True
            
            return observation_data
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return {
                "observation": response,
                "should_finish": True,
                "response": response
            }
