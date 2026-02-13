"""
Ollama Client - Local LLM Integration
"""

import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import urllib.request
import urllib.error


@dataclass
class Message:
    """Chat message"""
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None


@dataclass
class ToolCall:
    """Tool call from LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    DEFAULT_HOST = "http://localhost:11434"
    TIMEOUT = 120
    
    RECOMMENDED_MODELS = {
        "qwen3:latest": {
            "name": "Qwen 3",
            "description": "Fast, capable multilingual model",
            "size": "~4.7GB",
            "recommended": True
        },
        "llama3.1:8b": {
            "name": "Llama 3.1 8B",
            "description": "Meta's latest instruction model",
            "size": "~4.9GB",
            "recommended": True
        },
        "codellama:7b": {
            "name": "CodeLlama 7B",
            "description": "Specialized for code generation",
            "size": "~3.8GB",
            "recommended": False
        },
        "mistral:7b": {
            "name": "Mistral 7B",
            "description": "Balanced performance",
            "size": "~4.1GB",
            "recommended": False
        },
        "phi3:mini": {
            "name": "Phi-3 Mini",
            "description": "Lightweight, efficient",
            "size": "~2.3GB",
            "recommended": False
        },
    }
    
    def __init__(self, host: str = None, model: str = "qwen3:latest"):
        self.host = host or os.environ.get("OLLAMA_HOST", self.DEFAULT_HOST)
        self.model = model
        self.base_url = f"{self.host}/api"
        
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
            
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def pull_model(self, model_name: str, callback=None) -> Dict:
        """Pull a model from Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/pull",
                json={"name": model_name, "stream": False},
                timeout=600  # 10 minutes for download
            )
            if response.status_code == 200:
                return {"success": True, "model": model_name}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate(self, prompt: str, **kwargs) -> Dict:
        """Generate completion"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=self.TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, messages: List[Message], tools: List[Dict] = None, **kwargs) -> Dict:
        """Chat with the model"""
        # Convert messages to dict format
        msg_list = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_results:
                msg_dict["tool_results"] = msg.tool_results
            msg_list.append(msg_dict)
        
        payload = {
            "model": self.model,
            "messages": msg_list,
            "stream": False,
            **kwargs
        }
        
        # Add tools if available
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def parse_tool_calls(self, response: Dict) -> List[ToolCall]:
        """Parse tool calls from response"""
        tool_calls = []
        
        try:
            message = response.get("message", {})
            calls = message.get("tool_calls", [])
            
            for call in calls:
                func = call.get("function", {})
                args = json.loads(func.get("arguments", "{}"))
                
                tool_calls.append(ToolCall(
                    id=call.get("id", ""),
                    name=func.get("name", ""),
                    arguments=args
                ))
        except Exception:
            pass
            
        return tool_calls


# Import os for environment variable
import os
