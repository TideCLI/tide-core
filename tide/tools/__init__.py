"""Tool system - inspired by crush's tool architecture + Claude Code"""
from typing import Optional
from .base import Tool, ToolContext, ValidationResult
from .registry import ToolRegistry, ToolResult, get_registry, list_tools, register_tool
from . import advanced

# Register advanced tools (fast, like Claude Code/OpenCode)
_registry: Optional[ToolRegistry] = None

def _register_advanced_tools():
    """Register advanced function-based tools"""
    global _registry
    if _registry is None:
        _registry = get_registry()
    
    # Register advanced tools
    for name, func in advanced.TOOL_FUNCTIONS.items():
        _registry.register_function(name, func)

# Call this when initializing
_register_advanced_tools()

__all__ = ["Tool", "ToolContext", "ValidationResult", "ToolRegistry", "ToolResult", "get_registry", "list_tools", "register_tool", "advanced"]
