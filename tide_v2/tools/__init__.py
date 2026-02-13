"""
Tide Tools - Professional tool system
Based on charmbracelet/crush
"""

from .base import Tool, ToolResult, ToolParameter
from .filesystem import ViewTool, LSTool, EditTool, WriteTool, GlobTool
from .system import BashTool, PythonTool
from .code import AnalyzeTool, GrepTool, TodosTool
from .advanced import (
    MultiEditTool, SearchTool, ReferencesTool,
    WebFetchTool, DiagnosticsTool
)

__all__ = [
    # Base
    'Tool', 'ToolResult', 'ToolParameter',
    # Filesystem
    'ViewTool', 'LSTool', 'EditTool', 'WriteTool', 'GlobTool',
    # System
    'BashTool', 'PythonTool',
    # Code
    'AnalyzeTool', 'GrepTool', 'TodosTool',
    # Advanced
    'MultiEditTool', 'SearchTool', 'ReferencesTool',
    'WebFetchTool', 'DiagnosticsTool',
]

# All tools for registration
ALL_TOOLS = [
    # Filesystem (5)
    ViewTool, LSTool, EditTool, WriteTool, GlobTool,
    # System (2)
    BashTool, PythonTool,
    # Code (3)
    AnalyzeTool, GrepTool, TodosTool,
    # Advanced (5)
    MultiEditTool, SearchTool, ReferencesTool,
    WebFetchTool, DiagnosticsTool,
]
