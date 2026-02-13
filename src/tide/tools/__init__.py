"""
Tide Tools - All available tools
"""

from .base import Tool, ToolResult
from .registry import ToolRegistry
from .filesystem import ViewTool, LsTool, GlobTool, GrepTool
from .system import BashTool, PythonTool, SystemInfoTool, EnvTool
from .code import AnalyzeCodeTool, FindTodosTool, ProjectStructureTool, ExplainErrorTool


# All available tools
ALL_TOOLS = [
    # Filesystem tools
    ViewTool(),
    LsTool(),
    GlobTool(),
    GrepTool(),
    
    # System tools
    BashTool(),
    PythonTool(),
    SystemInfoTool(),
    EnvTool(),
    
    # Code tools
    AnalyzeCodeTool(),
    FindTodosTool(),
    ProjectStructureTool(),
    ExplainErrorTool(),
]


__all__ = [
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "ViewTool",
    "LsTool", 
    "GlobTool",
    "GrepTool",
    "BashTool",
    "PythonTool",
    "SystemInfoTool",
    "EnvTool",
    "AnalyzeCodeTool",
    "FindTodosTool",
    "ProjectStructureTool",
    "ExplainErrorTool",
    "ALL_TOOLS",
]
