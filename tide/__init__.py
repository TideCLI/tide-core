"""
🌊 Tide OS - Professional AI Coding Agent

A clean, crush-inspired coding assistant that works offline with local LLMs.

Usage:
    tide chat              # Start interactive chat
    tide tools             # List available tools
    tide --help            # Show help
"""

__version__ = "3.0.0"
__author__ = "Tide Team"
__license__ = "MIT"

from .agent import Agent
from .tools.base import Tool
from .tools.registry import ToolResult

__all__ = ["Agent", "Tool", "ToolResult", "__version__"]
