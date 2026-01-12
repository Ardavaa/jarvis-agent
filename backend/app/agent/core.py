"""
Agent Core - Plan-Act-Observe Loop
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from app.llm.ollama_client import OllamaClient
from app.agent.planner import Planner
from app.agent.parser import ToolCallParser
from app.agent.executor import ToolExecutor
from app.agent.observer import Observer


@dataclass
class AgentState:
    """Agent state representation"""
    conversation_id: str
    user_message: str
    plan: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = None
    observations: List[str] = None
    final_response: Optional[str] = None
    iteration: int = 0
    max_iterations: int = 5
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.observations is None:
            self.observations = []


class Agent:
    """
    Main Agent class implementing Plan-Act-Observe loop
    """
    
    def __init__(
        self,
        llm_client: OllamaClient,
        max_iterations: int = 5
    ):
        self.llm = llm_client
        self.planner = Planner(llm_client)
        self.parser = ToolCallParser()
        self.executor = ToolExecutor()
        self.observer = Observer(llm_client)
        self.max_iterations = max_iterations
    
    async def run(
        self,
        user_message: str,
        conversation_id: str,
        context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent loop
        
        Args:
            user_message: User's input message
            conversation_id: Unique conversation identifier
            context: Optional conversation history
            
        Returns:
            Dict containing final response and metadata
        """
        state = AgentState(
            conversation_id=conversation_id,
            user_message=user_message,
            max_iterations=self.max_iterations
        )
        
        # Agent loop: Plan -> Act -> Observe
        while state.iteration < state.max_iterations:
            state.iteration += 1
            
            # PLAN: Generate plan and identify tools needed
            plan_result = await self.planner.create_plan(
                user_message=state.user_message,
                context=context,
                observations=state.observations
            )
            
            state.plan = plan_result.get("plan")
            
            # Check if task is complete
            if plan_result.get("is_complete", False):
                state.final_response = plan_result.get("response")
                break
            
            # PARSE: Extract tool calls from plan
            tool_calls = self.parser.parse(plan_result.get("tool_calls", []))
            
            if not tool_calls:
                # No tools needed, generate final response
                state.final_response = plan_result.get("response")
                break
            
            state.tool_calls.extend(tool_calls)
            
            # ACT: Execute tool calls
            execution_results = await self.executor.execute_tools(tool_calls)
            
            # OBSERVE: Process results and decide next action
            observation = await self.observer.observe(
                plan=state.plan,
                tool_calls=tool_calls,
                execution_results=execution_results
            )
            
            state.observations.append(observation)
            
            # Check if we should continue or finish
            if observation.get("should_finish", False):
                state.final_response = observation.get("response")
                break
        
        # If max iterations reached without completion
        if not state.final_response:
            state.final_response = (
                "I apologize, but I couldn't complete the task within the allowed iterations. "
                "Please try rephrasing your request or breaking it into smaller tasks."
            )
        
        return {
            "response": state.final_response,
            "conversation_id": state.conversation_id,
            "iterations": state.iteration,
            "plan": state.plan,
            "tool_calls": state.tool_calls,
            "observations": state.observations
        }
