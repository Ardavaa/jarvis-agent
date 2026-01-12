"""
Error handling utilities for agent operations
"""
from typing import Callable, Any, Optional, Type
from functools import wraps
import asyncio
import time


class AgentError(Exception):
    """Base exception for agent errors"""
    pass


class ToolExecutionError(AgentError):
    """Error during tool execution"""
    pass


class PlanningError(AgentError):
    """Error during planning phase"""
    pass


class ObservationError(AgentError):
    """Error during observation phase"""
    pass


class MaxRetriesExceeded(AgentError):
    """Maximum retry attempts exceeded"""
    pass


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
) -> Any:
    """
    Retry a function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch
        on_retry: Optional callback function called on each retry
        
    Returns:
        Function result
        
    Raises:
        MaxRetriesExceeded: If all retries are exhausted
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                raise MaxRetriesExceeded(
                    f"Failed after {max_retries} retries: {str(e)}"
                ) from e
            
            # Call retry callback if provided
            if on_retry:
                on_retry(attempt + 1, max_retries, e)
            
            # Wait before retrying
            await asyncio.sleep(delay)
            delay *= backoff_factor
    
    # Should never reach here, but just in case
    raise last_exception


def handle_agent_errors(error_handler: Optional[Callable] = None):
    """
    Decorator for handling agent errors
    
    Args:
        error_handler: Optional custom error handler function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AgentError as e:
                # Agent-specific errors
                if error_handler:
                    return error_handler(e)
                else:
                    print(f"Agent error in {func.__name__}: {e}")
                    raise
            except Exception as e:
                # Unexpected errors
                print(f"Unexpected error in {func.__name__}: {e}")
                if error_handler:
                    return error_handler(e)
                raise
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            # Check if we should attempt recovery
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset if we were in half-open state
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"
