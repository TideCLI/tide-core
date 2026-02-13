"""
Tool Registry - Manages all available tools
"""

from typing import Dict, List, Any, Optional
from .base import Tool, ToolResult


class ToolRegistry:
    """Registry for all Tide tools"""
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self._tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool):
        """Register a tool"""
        tool.working_dir = self.working_dir
        self._tools[tool.name] = tool
        
    def register_all(self, tools: List[Tool]):
        """Register multiple tools"""
        for tool in tools:
            self.register(tool)
            
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)
        
    def execute(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool"""
        tool = self.get(name)
        
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{name}' not found"
            )
            
        # Validate
        valid, error = tool.validate(**arguments)
        if not valid:
            return ToolResult(
                success=False,
                output="",
                error=error or "Invalid parameters"
            )
            
        # Execute
        try:
            return tool.execute(**arguments)
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
            
    def list_all(self) -> List[str]:
        """List all tool names"""
        return list(self._tools.keys())
        
    def get_stats(self) -> Dict[str, Any]:
        """Get tool statistics"""
        categories = {}
        for tool in self._tools.values():
            cat = tool.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool.name)
            
        return {
            "total_tools": len(self._tools),
            "categories": {k: len(v) for k, v in categories.items()},
            "tools": list(self._tools.keys())
        }
        
    def to_ollama_tools(self) -> List[Dict]:
        """Convert all tools to Ollama format"""
        return [tool.to_ollama_tool() for tool in self._tools.values()]
