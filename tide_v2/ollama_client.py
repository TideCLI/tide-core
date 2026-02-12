"""
Ollama Client - Optimized for Tide
"""

import requests
import json
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, field
import re


@dataclass
class Message:
    """Chat message"""
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_calls: List[Dict] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role, "content": self.content}
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class ToolCall:
    """Tool call from assistant"""
    id: str
    name: str
    arguments: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ToolCall':
        return cls(
            id=data.get('id', ''),
            name=data.get('function', {}).get('name', ''),
            arguments=json.loads(data.get('function', {}).get('arguments', '{}'))
        )


class OllamaClient:
    """Client for Ollama API"""
    
    def __init__(self, model: str = "qwen3:latest", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.chat_url = f"{host}/api/chat"
        self.generate_url = f"{host}/api/generate"
    
    def chat(self, messages: List[Message], tools: Optional[List[Dict]] = None, stream: bool = False) -> Dict[str, Any]:
        """Send chat request to Ollama"""
        
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "num_ctx": 8192,
            }
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out after 120 seconds"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Cannot connect to Ollama at {self.host}. Is it running?"}
        except Exception as e:
            return {"error": str(e)}
    
    def generate(self, prompt: str, system: str = "") -> str:
        """Simple generation"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error: {e}"
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except:
            return []
    
    def parse_tool_calls(self, response: Dict) -> List[ToolCall]:
        """Parse tool calls from response"""
        tool_calls = []
        
        message = response.get("message", {})
        
        # Ollama format
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                tool_calls.append(ToolCall.from_dict(tc))
        
        # Fallback: try to parse from content
        content = message.get("content", "")
        tool_calls.extend(self._extract_tool_calls_from_content(content))
        
        return tool_calls
    
    def _extract_tool_calls_from_content(self, content: str) -> List[ToolCall]:
        """Extract tool calls from content if not in proper format"""
        tool_calls = []
        
        # Pattern: <tool_name>({args})
        pattern = r'<tool>(\w+)</tool>\s*({[^}]+})'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for name, args_str in matches:
            try:
                args = json.loads(args_str)
                tool_calls.append(ToolCall(
                    id=f"call_{len(tool_calls)}",
                    name=name,
                    arguments=args
                ))
            except:
                pass
        
        return tool_calls
    
    def check_connection(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
