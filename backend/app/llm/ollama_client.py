"""
Ollama Client - Interface to Ollama LLM
"""
from typing import Optional, List, Dict, Any
import aiohttp
import json

from app.config import settings


class OllamaClient:
    """
    Client for interacting with Ollama LLM
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                
                if stream:
                    # Handle streaming response
                    full_response = ""
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                full_response += data["response"]
                    return full_response
                else:
                    # Handle non-streaming response
                    data = await response.json()
                    return data.get("response", "")
                    
        except aiohttp.ClientError as e:
            print(f"Ollama API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response
        """
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                
                if stream:
                    full_response = ""
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                full_response += data["message"]["content"]
                    return full_response
                else:
                    data = await response.json()
                    return data.get("message", {}).get("content", "")
                    
        except aiohttp.ClientError as e:
            print(f"Ollama API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        session = await self._get_session()
        
        payload = {
            "model": settings.ollama_embedding_model,
            "prompt": text
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("embedding", [])
                
        except aiohttp.ClientError as e:
            print(f"Ollama API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def check_health(self) -> bool:
        """
        Check if Ollama is running and accessible
        
        Returns:
            True if healthy, False otherwise
        """
        session = await self._get_session()
        
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception:
            return False
