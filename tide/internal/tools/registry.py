"""
Tool Registry - Manages all available tools
"""

from typing import Dict, List, Optional
from internal.tools.base import Tool, ToolResult
from internal.tools.filesystem import FileSystemTools
from internal.tools.system import SystemTools
from internal.tools.code import CodeTools


class ToolRegistry:
    """Registry of all tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[str, List[str]] = {
            "filesystem": [],
            "system": [],
            "code": [],
            "git": [],
            "advanced": []
        }
        self._register_all_tools()
    
    def register(self, tool: Tool, category: str = "general"):
        """Register a tool"""
        self.tools[tool.name] = tool
        if category in self.categories:
            self.categories[category].append(tool.name)
    
    def get(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_all(self) -> List[str]:
        """List all tool names"""
        return list(self.tools.keys())
    
    def list_by_category(self, category: str) -> List[str]:
        """List tools in category"""
        return self.categories.get(category, [])
    
    def to_schema(self) -> List[Dict]:
        """Convert to JSON schema for LLM"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def _register_all_tools(self):
        """Register all tools"""
        # Filesystem tools
        fs = FileSystemTools()
        for tool in fs.get_tools():
            self.register(tool, "filesystem")
        
        # System tools
        sys = SystemTools()
        for tool in sys.get_tools():
            self.register(tool, "system")
        
        # Code tools
        code = CodeTools()
        for tool in code.get_tools():
            self.register(tool, "code")
