"""
Base Tool Class
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Tool:
    """Base class for all tools"""
    
    name: str = ""
    description: str = ""
    category: str = "general"
    parameters: Dict[str, Any] = {}
    requires_confirmation: bool = False
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool - override in subclasses"""
        raise NotImplementedError
        
    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters - override in subclasses"""
        return True, None
        
    def to_dict(self) -> Dict:
        """Convert tool to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": self.parameters,
            "requires_confirmation": self.requires_confirmation
        }
        
    def to_ollama_tool(self) -> Dict:
        """Convert to Ollama tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters.get("properties", {}),
                    "required": self.parameters.get("required", [])
                }
            }
        }
