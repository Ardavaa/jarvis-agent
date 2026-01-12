"""
Enhanced Agent Core - Plan-Act-Observe Loop with Memory Integration
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import uuid

from app.llm.ollama_client import OllamaClient
from app.agent.planner import Planner
from app.agent.parser import ToolCallParser
from app.agent.executor import ToolExecutor
from app.agent.observer import Observer
from app.agent.error_handling import retry_with_backoff, ToolExecutionError, PlanningError
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.semantic import SemanticMemory


@dataclass
class AgentState:
    """Agent state representation"""
    conversation_id: str
    user_id: str = "default_user"
    user_message: str = ""
    plan: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    final_response: Optional[str] = None
    iteration: int = 0
    max_iterations: int = 5
    db_conversation_id: Optional[int] = None


class EnhancedAgent:
    """
    Enhanced Agent class with memory integration and error handling
    Implements Plan-Act-Observe loop with three-tier memory system
    """
    
    def __init__(
        self,
        llm_client: OllamaClient,
        max_iterations: int = 5,
        enable_semantic_memory: bool = True
    ):
        """
        Initialize enhanced agent
        
        Args:
            llm_client: Ollama LLM client
            max_iterations: Maximum iterations for agent loop
            enable_semantic_memory: Whether to use semantic memory (RAG)
        """
        self.llm = llm_client
        self.planner = Planner(llm_client)
        self.parser = ToolCallParser()
        self.executor = ToolExecutor()
        self.observer = Observer(llm_client)
        self.max_iterations = max_iterations
        
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(max_messages=20)
        self.long_term_memory = LongTermMemory()
        self.semantic_memory = SemanticMemory() if enable_semantic_memory else None
        
        print("✅ Enhanced Agent initialized with memory systems")
    
    async def run(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_id: str = "default_user",
        use_semantic_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the enhanced agent loop with memory integration
        
        Args:
            user_message: User's input message
            conversation_id: Optional conversation identifier
            user_id: User identifier
            use_semantic_memory: Whether to use semantic memory for this query
            
        Returns:
            Dict containing response and metadata
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Initialize state
        state = AgentState(
            conversation_id=conversation_id,
            user_id=user_id,
            user_message=user_message,
            max_iterations=self.max_iterations
        )
        
        try:
            # Create or get database conversation
            state.db_conversation_id = self.long_term_memory.create_conversation(user_id)
            
            # Add user message to short-term memory
            self.short_term_memory.add_message(
                conversation_id,
                role="user",
                content=user_message
            )
            
            # Save user message to long-term memory
            self.long_term_memory.save_message(
                state.db_conversation_id,
                role="user",
                content=user_message
            )
            
            # Get conversation context
            context = self.short_term_memory.format_for_llm(conversation_id)
            
            # Get semantic context if enabled
            semantic_context = None
            if use_semantic_memory and self.semantic_memory:
                semantic_context = await self._get_semantic_context(
                    user_message,
                    conversation_id
                )
            
            # Agent loop: Plan -> Act -> Observe
            while state.iteration < state.max_iterations:
                state.iteration += 1
                
                print(f"\n🔄 Iteration {state.iteration}/{state.max_iterations}")
                
                # PLAN: Generate plan with retry
                try:
                    plan_result = await retry_with_backoff(
                        lambda: self.planner.create_plan(
                            user_message=state.user_message,
                            context=context,
                            observations=state.observations,
                            semantic_context=semantic_context
                        ),
                        max_retries=2,
                        on_retry=lambda attempt, max_retries, e: print(
                            f"⚠️  Planning retry {attempt}/{max_retries}: {e}"
                        )
                    )
                except Exception as e:
                    raise PlanningError(f"Planning failed: {e}") from e
                
                state.plan = plan_result.get("plan")
                print(f"📋 Plan: {state.plan[:100]}...")
                
                # Check if task is complete
                if plan_result.get("is_complete", False):
                    state.final_response = plan_result.get("response")
                    print("✅ Task complete (no tools needed)")
                    break
                
                # PARSE: Extract tool calls
                tool_calls = self.parser.parse(plan_result.get("tool_calls", []))
                
                if not tool_calls:
                    # No tools needed, generate final response
                    state.final_response = plan_result.get("response")
                    print("✅ Task complete (direct response)")
                    break
                
                print(f"🔧 Tools to execute: {[tc['tool'] for tc in tool_calls]}")
                state.tool_calls.extend(tool_calls)
                
                # ACT: Execute tool calls with retry
                try:
                    execution_results = await retry_with_backoff(
                        lambda: self.executor.execute_tools(tool_calls),
                        max_retries=2,
                        exceptions=(ToolExecutionError,),
                        on_retry=lambda attempt, max_retries, e: print(
                            f"⚠️  Tool execution retry {attempt}/{max_retries}: {e}"
                        )
                    )
                except Exception as e:
                    # Tool execution failed, but continue with error info
                    execution_results = [{
                        "tool": tc["tool"],
                        "success": False,
                        "error": str(e)
                    } for tc in tool_calls]
                    print(f"❌ Tool execution failed: {e}")
                
                # OBSERVE: Process results
                observation = await self.observer.observe(
                    plan=state.plan,
                    tool_calls=tool_calls,
                    execution_results=execution_results
                )
                
                state.observations.append(observation.get("observation", ""))
                print(f"👁️  Observation: {observation.get('observation', '')[:100]}...")
                
                # Check if we should finish
                if observation.get("should_finish", False):
                    state.final_response = observation.get("response")
                    print("✅ Task complete (after tool execution)")
                    break
            
            # If max iterations reached without completion
            if not state.final_response:
                state.final_response = (
                    "I apologize, but I couldn't complete the task within the allowed iterations. "
                    "Please try rephrasing your request or breaking it into smaller tasks."
                )
                print("⚠️  Max iterations reached")
            
            # Add assistant response to short-term memory
            self.short_term_memory.add_message(
                conversation_id,
                role="assistant",
                content=state.final_response
            )
            
            # Save assistant response to long-term memory
            self.long_term_memory.save_message(
                state.db_conversation_id,
                role="assistant",
                content=state.final_response
            )
            
            # Save task history
            if state.tool_calls:
                self.long_term_memory.save_task(
                    state.db_conversation_id,
                    task_description=state.user_message,
                    tools_used=state.tool_calls,
                    status="completed" if state.final_response else "failed",
                    result={"response": state.final_response}
                )
            
            # Add conversation to semantic memory
            if self.semantic_memory:
                await self._save_to_semantic_memory(state, context)
            
            # Log interaction
            self.long_term_memory.log_interaction(
                user_id=user_id,
                interaction_type="chat",
                metadata={
                    "conversation_id": conversation_id,
                    "iterations": state.iteration,
                    "tools_used": len(state.tool_calls)
                }
            )
            
            return {
                "response": state.final_response,
                "conversation_id": conversation_id,
                "iterations": state.iteration,
                "plan": state.plan,
                "tool_calls": state.tool_calls,
                "observations": state.observations,
                "memory_stats": self._get_memory_stats(conversation_id)
            }
            
        except Exception as e:
            print(f"❌ Agent error: {e}")
            # Save error to memory
            error_response = f"I encountered an error: {str(e)}"
            
            self.short_term_memory.add_message(
                conversation_id,
                role="assistant",
                content=error_response
            )
            
            if state.db_conversation_id:
                self.long_term_memory.save_message(
                    state.db_conversation_id,
                    role="assistant",
                    content=error_response,
                    metadata={"error": str(e)}
                )
            
            return {
                "response": error_response,
                "conversation_id": conversation_id,
                "iterations": state.iteration,
                "error": str(e)
            }
    
    async def _get_semantic_context(
        self,
        query: str,
        conversation_id: str
    ) -> Optional[str]:
        """Get relevant context from semantic memory"""
        try:
            context = await self.semantic_memory.retrieve_context(
                query=query,
                limit=3,
                filter_metadata={"conversation_id": conversation_id}
            )
            return context if context != "No relevant context found." else None
        except Exception as e:
            print(f"⚠️  Semantic memory retrieval failed: {e}")
            return None
    
    async def _save_to_semantic_memory(
        self,
        state: AgentState,
        context: List[Dict[str, str]]
    ) -> None:
        """Save conversation to semantic memory"""
        try:
            await self.semantic_memory.add_conversation_to_memory(
                conversation_id=state.conversation_id,
                messages=context,
                user_id=state.user_id
            )
        except Exception as e:
            print(f"⚠️  Failed to save to semantic memory: {e}")
    
    def _get_memory_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {
            "short_term": self.short_term_memory.get_conversation_summary(conversation_id),
        }
        
        if self.semantic_memory:
            stats["semantic"] = {
                "total_memories": self.semantic_memory.get_memory_count()
            }
        
        return stats
    
    def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation from short-term memory"""
        self.short_term_memory.clear_context(conversation_id)
