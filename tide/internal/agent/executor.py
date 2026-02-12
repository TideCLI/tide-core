"""
Tool Executor - Executes tool calls
"""

from typing import Dict
from internal.tools.registry import ToolRegistry
from internal.tools.base import ToolResult


class ToolExecutor:
    """Executes tool calls"""
    
    def __init__(self, tools: ToolRegistry):
        self.tools = tools
    
    def execute(self, tool_call: Dict) -> ToolResult:
        """Execute a tool call"""
        name = tool_call.get("name")
        parameters = tool_call.get("parameters", {})
        
        tool = self.tools.get(name)
        if not tool:
            return ToolResult(False, "", f"Unknown tool: {name}")
        
        return tool.execute(parameters)
