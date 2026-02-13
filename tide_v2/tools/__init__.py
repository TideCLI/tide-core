"""
Tide Tools - Professional tool system
Based on charmbracelet/crush
"""

from .base import Tool, ToolResult, ToolParameter
from .filesystem import ViewTool, LSTool, EditTool, WriteTool, GlobTool, FileMoveTool, FileDeleteTool
from .system import BashTool, PythonTool
from .code import AnalyzeTool, GrepTool, TodosTool
from .advanced import (
    MultiEditTool, SearchTool, ReferencesTool,
    WebFetchTool, DiagnosticsTool
)
from .git import GitStatusTool, GitDiffTool, GitCommitTool, GitLogTool
from .planning import PlannerTool, ContextManagerTool
from .memory import UndoTool, SessionMemoryTool, ProjectIndexTool
from .testing import RunTestsTool, DiffPreviewTool, CodeTransformTool, ErrorRecoveryTool

__all__ = [
    # Base
    'Tool', 'ToolResult', 'ToolParameter',
    # Filesystem
    'ViewTool', 'LSTool', 'EditTool', 'WriteTool', 'GlobTool',
    'FileMoveTool', 'FileDeleteTool',
    # System
    'BashTool', 'PythonTool',
    # Code
    'AnalyzeTool', 'GrepTool', 'TodosTool',
    # Advanced
    'MultiEditTool', 'SearchTool', 'ReferencesTool',
    'WebFetchTool', 'DiagnosticsTool',
    # Git
    'GitStatusTool', 'GitDiffTool', 'GitCommitTool', 'GitLogTool',
    # Planning
    'PlannerTool', 'ContextManagerTool',
    # Memory
    'UndoTool', 'SessionMemoryTool', 'ProjectIndexTool',
    # Testing & Validation
    'RunTestsTool', 'DiffPreviewTool', 'CodeTransformTool', 'ErrorRecoveryTool',
]

# All tools for registration (30 total)
ALL_TOOLS = [
    # Filesystem (7)
    ViewTool, LSTool, EditTool, WriteTool, GlobTool,
    FileMoveTool, FileDeleteTool,
    # System (2)
    BashTool, PythonTool,
    # Code (3)
    AnalyzeTool, GrepTool, TodosTool,
    # Advanced (5)
    MultiEditTool, SearchTool, ReferencesTool,
    WebFetchTool, DiagnosticsTool,
    # Git (4)
    GitStatusTool, GitDiffTool, GitCommitTool, GitLogTool,
    # Planning (2)
    PlannerTool, ContextManagerTool,
    # Memory (3)
    UndoTool, SessionMemoryTool, ProjectIndexTool,
    # Testing & Validation (4)
    RunTestsTool, DiffPreviewTool, CodeTransformTool, ErrorRecoveryTool,
]
