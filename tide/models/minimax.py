"""
MiniMax API Client - Updated for MiniMax API v2
Supports MiniMax chat completion API with Coding Plan support
Docs: https://www.minimaxi.com/en/document
"""
import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import urllib.request
import urllib.error


@dataclass
class ChatMessage:
    """A chat message"""
    role: str  # system, user, assistant
    content: str
    tool_calls: Optional[List[Dict]] = None


@dataclass
class ChatResponse:
    """Response from chat completion"""
    content: str
    model: str = ""
    usage: Dict = field(default_factory=dict)
    raw_response: Dict = field(default_factory=dict)


class MiniMaxClient:
    """MiniMax API client - Supports Coding Plan via Anthropic-compatible API"""
    
    # Use Anthropic-compatible endpoint (for coding tools like Claude Code)
    API_BASE = "https://api.minimax.io/anthropic/v1"
    USE_ANTHROPIC_API = True
    
    # MiniMax model IDs - M2.5 is the coding model
    DEFAULT_MODELS = {
        "MiniMax-M2.5": {
            "name": "MiniMax-M2.5",
            "description": "MiniMax M2.5 - AI Coding Optimized",
            "size": "API",
            "speed": "fast"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        # Group ID might be needed for coding plan
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID", "")
        self.timeout = timeout
        
        # Try to extract group_id from API key if not provided
        # Some API keys contain group info
        if not self.group_id and self.api_key:
            # Format might be: sk-cp-<group_id>-<rest>
            parts = self.api_key.split('-')
            if len(parts) >= 3 and parts[1] == 'cp':
                # The part after 'cp' might be group_id
                potential_gid = parts[2]
                if len(potential_gid) > 5:  # Likely a group ID
                    self.group_id = potential_gid
    
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request to MiniMax"""
        if not self.api_key:
            raise ValueError("MiniMax API key not set. Set MINIMAX_API_KEY env var.")
        
        url = f"{self.API_BASE}/{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Add group_id to the request body if available (required for some plans)
        if self.group_id and "group_id" not in data:
            data["group_id"] = self.group_id
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise Exception(f"MiniMax API error {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection error: {e.reason}")
        except TimeoutError:
            raise Exception(f"Request timed out after {self.timeout}s")
    
    def _make_request_anthropic(self, data: Dict) -> Dict:
        """Make request using Anthropic-compatible API"""
        if not self.api_key:
            raise ValueError("MiniMax API key not set. Set MINIMAX_API_KEY env var.")
        
        url = f"{self.API_BASE}/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise Exception(f"MiniMax API error {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection error: {e.reason}")
        except TimeoutError:
            raise Exception(f"Request timed out after {self.timeout}s")
    
    def chat(self, model: str, messages: List[ChatMessage]) -> ChatResponse:
        """Send chat completion request to MiniMax using Anthropic-compatible API"""
        # Convert messages to Anthropic format
        formatted_messages = []
        for msg in messages:
            role = msg.role
            if role == "system":
                role = "user"  # Anthropic doesn't have system role
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
        
        # Use Anthropic-compatible API format
        data = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": 2048
        }
        
        try:
            # Use Anthropic-compatible endpoint
            response = self._make_request_anthropic(data)
            
            # Parse Anthropic response format
            # Response has "content" array with type: "text" or "thinking"
            content_array = response.get("content", [])
            content_parts = []
            
            for item in content_array:
                if item.get("type") == "text":
                    content_parts.append(item.get("text", ""))
                # Skip "thinking" type - it's reasoning, not the answer
            
            content = "\n".join(content_parts)
            
            if not content:
                content = "No response"
            
            return ChatResponse(
                content=content,
                model=model,
                usage=response.get("usage", {}),
                raw_response=response
            )
            
        except Exception as e:
            raise Exception(f"MiniMax chat failed: {e}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available MiniMax models"""
        return [
            {"name": key, **info}
            for key, info in self.DEFAULT_MODELS.items()
        ]
    
    def is_available(self) -> bool:
        """Check if MiniMax API is available (has API key)"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def test_connection(self) -> bool:
        """Test API connection with a simple request"""
        try:
            test_messages = [
                ChatMessage(role="user", content="Hi")
            ]
            response = self.chat("MiniMax-M2.5", test_messages)
            return len(response.content) > 0
        except Exception as e:
            print(f"MiniMax connection test failed: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account information (if API supports it)"""
        # This is a placeholder - MiniMax might have an account endpoint
        return {
            "api_key_present": bool(self.api_key),
            "group_id_present": bool(self.group_id),
            "group_id": self.group_id[:10] + "..." if self.group_id else None
        }


def create_minimax_client(timeout: int = 60) -> Optional[MiniMaxClient]:
    """Factory function to create MiniMax client if API key is available"""
    client = MiniMaxClient(timeout=timeout)
    if client.is_available():
        return client
    return None
