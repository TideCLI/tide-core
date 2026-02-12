"""
Optimized Tool Base - Based on crush architecture
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import json


@dataclass
class ToolResult:
    """Tool execution result with metadata"""
    output: str = ""
    error: str = ""
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tool_name: str = ""
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def set_finished(self):
        """Mark tool execution as finished"""
        self.end_time = datetime.now()
    
    @property
    def duration_ms(self) -> float:
        """Get execution duration in milliseconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "output": self.output,
            "error": self.error,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata
        }


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required
        }
        if self.default is not None:
            result["default"] = self.default
        return result


class Tool(ABC):
    """Base tool class - optimized like crush"""
    
    # Tool metadata
    name: str = ""
    description: str = ""
    parameters: List[ToolParameter] = []
    category: str = "general"
    
    # Limits and safety
    max_output_length: int = 30000
    timeout_seconds: int = 30
    requires_confirmation: bool = False
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self._validate_tool()
    
    def _validate_tool(self):
        """Validate tool configuration"""
        assert self.name, "Tool must have a name"
        assert self.description, "Tool must have a description"
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool"""
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> Optional[str]:
        """Validate parameters before execution"""
        for param in self.parameters:
            if param.required and param.name not in params:
                return f"Missing required parameter: {param.name}"
            if param.name in params:
                value = params[param.name]
                if not self._validate_type(value, param.type):
                    return f"Parameter {param.name} must be of type {param.type}"
        return None
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type"""
        type_map = {
            "string": str,
            "str": str,
            "integer": int,
            "int": int,
            "boolean": bool,
            "bool": bool,
            "array": list,
            "list": list,
            "object": dict,
            "dict": dict
        }
        expected = type_map.get(expected_type.lower())
        if expected:
            return isinstance(value, expected)
        return True
    
    def truncate_output(self, output: str, limit: int = None) -> str:
        """Truncate output if too long"""
        if limit is None:
            limit = self.max_output_length
        if len(output) > limit:
            truncated = output[:limit]
            return truncated + f"\n\n[Output truncated. Total length: {len(output)} characters]"
        return output
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "category": self.category,
            "requires_confirmation": self.requires_confirmation
        }
    
    def to_ollama_format(self) -> Dict[str, Any]:
        """Convert to Ollama function calling format"""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


class PermissionRequiredError(Exception):
    """Raised when permission is required for a tool"""
    pass


class ToolExecutionError(Exception):
    """Raised when tool execution fails"""
    pass
