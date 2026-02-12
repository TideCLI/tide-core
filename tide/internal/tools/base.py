"""
Base tool classes
"""

from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional


@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    output: str
    error: Optional[str] = None
    
    def __str__(self):
        if self.success:
            return self.output
        return f"Error: {self.error}"


@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable
    requires_confirmation: bool = False
    category: str = "general"
    
    def to_dict(self) -> Dict:
        """Convert to dict for LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def execute(self, params: Dict) -> ToolResult:
        """Execute tool"""
        try:
            return self.func(params)
        except Exception as e:
            return ToolResult(False, "", str(e))
