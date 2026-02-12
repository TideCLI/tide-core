"""
Tide v2 - Professional AI Coding Agent
Optimized based on charmbracelet/crush architecture
"""

__version__ = "2.0.0"
__author__ = "Tide Team"

from .agent import TideAgent
from .tools import Tool, ToolResult
from .tool_registry import ToolRegistry

__all__ = ['TideAgent', 'Tool', 'ToolResult', 'ToolRegistry']
