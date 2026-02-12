"""
Tool Registry - Manage and execute tools
"""

from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime
import json

from .tools.base import Tool, ToolResult


@dataclass
class ToolExecution:
    """Record of tool execution"""
    tool_name: str
    params: Dict[str, Any]
    result: ToolResult
    timestamp: datetime
    duration_ms: float


class ToolRegistry:
    """Registry of available tools"""
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self._tools: Dict[str, Tool] = {}
        self._history: List[ToolExecution] = []
    
    def register(self, tool_class: Type[Tool]) -> 'ToolRegistry':
        """Register a tool class"""
        tool = tool_class(self.working_dir)
        self._tools[tool.name] = tool
        return self
    
    def register_all(self, tool_classes: List[Type[Tool]]) -> 'ToolRegistry':
        """Register multiple tool classes"""
        for tool_class in tool_classes:
            self.register(tool_class)
        return self
    
    def get(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self._tools.get(name)
    
    def list_all(self) -> List[str]:
        """List all tool names"""
        return sorted(self._tools.keys())
    
    def get_all(self) -> Dict[str, Tool]:
        """Get all tools"""
        return self._tools.copy()
    
    def get_by_category(self, category: str) -> Dict[str, Tool]:
        """Get tools by category"""
        return {
            name: tool for name, tool in self._tools.items()
            if tool.category == category
        }
    
    def execute(self, name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name"""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                error=f"Tool not found: {name}",
                success=False,
                tool_name=name
            )
        
        start_time = datetime.now()
        
        # Validate params
        validation_error = tool.validate_params(params)
        if validation_error:
            return ToolResult(
                error=validation_error,
                success=False,
                tool_name=name
            )
        
        # Execute tool
        try:
            result = tool.execute(params)
        except Exception as e:
            result = ToolResult(
                error=f"Execution error: {str(e)}",
                success=False,
                tool_name=name
            )
        
        # Record execution
        duration = (datetime.now() - start_time).total_seconds() * 1000
        execution = ToolExecution(
            tool_name=name,
            params=params,
            result=result,
            timestamp=start_time,
            duration_ms=duration
        )
        self._history.append(execution)
        
        return result
    
    def get_history(self) -> List[ToolExecution]:
        """Get execution history"""
        return self._history.copy()
    
    def clear_history(self):
        """Clear execution history"""
        self._history.clear()
    
    def to_ollama_tools(self) -> List[Dict]:
        """Convert all tools to Ollama format"""
        return [tool.to_ollama_format() for tool in self._tools.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_executions = len(self._history)
        successful = sum(1 for e in self._history if e.result.success)
        
        by_tool = {}
        for exec in self._history:
            if exec.tool_name not in by_tool:
                by_tool[exec.tool_name] = {"count": 0, "success": 0, "avg_duration": 0}
            by_tool[exec.tool_name]["count"] += 1
            if exec.result.success:
                by_tool[exec.tool_name]["success"] += 1
            by_tool[exec.tool_name]["avg_duration"] += exec.duration_ms
        
        # Calculate averages
        for tool_name in by_tool:
            count = by_tool[tool_name]["count"]
            by_tool[tool_name]["avg_duration"] /= count
        
        return {
            "total_tools": len(self._tools),
            "total_executions": total_executions,
            "successful": successful,
            "failed": total_executions - successful,
            "success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
            "by_tool": by_tool
        }
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def __getitem__(self, name: str) -> Tool:
        return self._tools[name]
    
    def __len__(self) -> int:
        return len(self._tools)
