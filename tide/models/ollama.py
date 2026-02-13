"""
Ollama client for local LLM inference
"""
import json
import requests
from typing import AsyncGenerator, Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """A chat message"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict]] = None


@dataclass
class ChatResponse:
    """Response from chat completion"""
    content: str
    done: bool
    model: str
    tool_calls: Optional[List[Dict]] = None


class OllamaClient:
    """Client for Ollama API"""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        self.host = host.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = self.session.get(
                f"{self.host}/api/tags",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
    
    def pull_model(self, model: str) -> None:
        """Pull a model from Ollama"""
        try:
            response = self.session.post(
                f"{self.host}/api/pull",
                json={"name": model},
                stream=True,
                timeout=300
            )
            response.raise_for_status()
            # Consume stream
            for _ in response.iter_lines():
                pass
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to pull model: {e}")
    
    def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
        temperature: float = 0.1,
        num_predict: int = 500,
    ) -> ChatResponse:
        """
        Send a chat request to Ollama
        
        Args:
            model: Model name (e.g., "llama3.1:8b")
            messages: List of chat messages
            tools: Optional list of tool definitions
            stream: Whether to stream the response
            temperature: Sampling temperature (0.1 = more focused/faster)
            num_predict: Maximum tokens to generate (500 = faster responses)
        """
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_msg = {
                "role": msg.role,
                "content": msg.content
            }
            ollama_messages.append(ollama_msg)
        
        # Optimized options for speed
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,  # Limit response length
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
            }
        }
        
        # Add tools if provided (Ollama supports tools in newer versions)
        if tools:
            payload["tools"] = tools
        
        try:
            response = self.session.post(
                f"{self.host}/api/chat",
                json=payload,
                stream=stream,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                data = response.json()
                message = data.get("message", {})
                return ChatResponse(
                    content=message.get("content", ""),
                    done=data.get("done", True),
                    model=model,
                    tool_calls=message.get("tool_calls")
                )
                
        except requests.RequestException as e:
            raise ConnectionError(f"Chat request failed: {e}")
    
    def _handle_stream(self, response) -> ChatResponse:
        """Handle streaming response"""
        content_parts = []
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    message = data.get("message", {})
                    content = message.get("content", "")
                    if content:
                        content_parts.append(content)
                    if data.get("done"):
                        return ChatResponse(
                            content="".join(content_parts),
                            done=True,
                            model=data.get("model", ""),
                            tool_calls=message.get("tool_calls")
                        )
                except json.JSONDecodeError:
                    continue
        return ChatResponse(content="".join(content_parts), done=True, model="")
    
    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """Generate text from a prompt"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        if system:
            payload["system"] = system
        
        try:
            response = self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                stream=stream,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                parts = []
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            parts.append(data.get("response", ""))
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                return "".join(parts)
            else:
                data = response.json()
                return data.get("response", "")
                
        except requests.RequestException as e:
            raise ConnectionError(f"Generation failed: {e}")
    
    def check_connection(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(
                f"{self.host}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
