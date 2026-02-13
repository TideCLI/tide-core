"""
Filesystem Tools
"""

import os
import glob as glob_module
from pathlib import Path
from typing import Dict, Any, Optional
from .base import Tool, ToolResult


class ViewTool(Tool):
    """View file contents"""
    
    name = "view"
    description = "Read and display file contents with line numbers"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to view"
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of lines to show"
            },
            "offset": {
                "type": "number",
                "description": "Line number to start from"
            }
        },
        "required": ["file_path"]
    }
    requires_confirmation = False
    
    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        if not kwargs.get("file_path"):
            return False, "file_path is required"
        return True, None
        
    def execute(self, **kwargs) -> ToolResult:
        file_path = os.path.expanduser(kwargs["file_path"])
        limit = kwargs.get("limit", 1000)
        offset = kwargs.get("offset", 1)
        
        if not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}"
            )
            
        if not os.path.isfile(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"Not a file: {file_path}"
            )
            
        # Check file size
        size = os.path.getsize(file_path)
        if size > 5 * 1024 * 1024:  # 5MB limit
            return ToolResult(
                success=False,
                output="",
                error=f"File too large: {size} bytes (max 5MB)"
            )
            
        try:
            lines = []
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if i >= offset:
                        lines.append(f"{i:6d}  {line.rstrip()}")
                    if len(lines) >= limit:
                        break
                        
            output = "\n".join(lines)
            return ToolResult(
                success=True,
                output=output,
                metadata={"lines": len(lines), "file": file_path}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class LsTool(Tool):
    """List directory contents"""
    
    name = "ls"
    description = "List directory contents in tree format"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory to list"
            },
            "all": {
                "type": "boolean",
                "description": "Show hidden files"
            },
            "max_depth": {
                "type": "number",
                "description": "Maximum depth for tree"
            }
        }
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        path = os.path.expanduser(kwargs.get("path", "."))
        show_all = kwargs.get("all", False)
        max_depth = kwargs.get("max_depth", 2)
        
        if not os.path.exists(path):
            return ToolResult(
                success=False,
                output="",
                error=f"Path not found: {path}"
            )
            
        if not os.path.isdir(path):
            return ToolResult(
                success=False,
                output="",
                error=f"Not a directory: {path}"
            )
            
        lines = []
        
        def list_dir(dir_path: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
                
            try:
                entries = sorted(os.listdir(dir_path), key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x))
                
                for i, entry in enumerate(entries):
                    if not show_all and entry.startswith("."):
                        continue
                        
                    full_path = os.path.join(dir_path, entry)
                    is_dir = os.path.isdir(full_path)
                    suffix = "/" if is_dir else ""
                    
                    if i == len(entries) - 1:
                        lines.append(f"{prefix}└── {entry}{suffix}")
                        new_prefix = prefix + "    "
                    else:
                        lines.append(f"{prefix}├── {entry}{suffix}")
                        new_prefix = prefix + "│   "
                        
                    if is_dir and depth < max_depth:
                        list_dir(full_path, new_prefix, depth + 1)
            except PermissionError:
                lines.append(f"{prefix}[Permission Denied]")
                
        lines.append(path + "/")
        list_dir(path)
        
        return ToolResult(
            success=True,
            output="\n".join(lines)
        )


class GlobTool(Tool):
    """Find files by pattern"""
    
    name = "glob"
    description = "Find files matching a glob pattern"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern (e.g., *.py, **/*.js)"
            },
            "path": {
                "type": "string",
                "description": "Base path to search"
            }
        },
        "required": ["pattern"]
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        pattern = kwargs.get("pattern", "*")
        base_path = os.path.expanduser(kwargs.get("path", "."))
        
        # Convert ** to **
        search_pattern = os.path.join(base_path, pattern)
        
        try:
            files = glob_module.glob(search_pattern, recursive=True)
            
            if not files:
                return ToolResult(
                    success=True,
                    output="No files found matching pattern"
                )
                
            # Limit results
            files = files[:100]
            
            output = "\n".join(files)
            return ToolResult(
                success=True,
                output=output,
                metadata={"count": len(files)}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class GrepTool(Tool):
    """Search file contents"""
    
    name = "grep"
    description = "Search for text in files"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Text pattern to search"
            },
            "path": {
                "type": "string",
                "description": "File or directory to search"
            },
            "ignore_case": {
                "type": "boolean",
                "description": "Case insensitive search"
            },
            "line_numbers": {
                "type": "boolean",
                "description": "Show line numbers"
            }
        },
        "required": ["pattern", "path"]
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        pattern = kwargs.get("pattern", "")
        path = os.path.expanduser(kwargs.get("path", "."))
        ignore_case = kwargs.get("ignore_case", True)
        show_lines = kwargs.get("line_numbers", True)
        
        if not pattern:
            return ToolResult(
                success=False,
                output="",
                error="Pattern is required"
            )
            
        import re
        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)
        
        results = []
        
        try:
            if os.path.isfile(path):
                files = [path]
            else:
                files = []
                for root, _, filenames in os.walk(path):
                    for f in filenames:
                        files.append(os.path.join(root, f))
                        
            for filepath in files[:50]:  # Limit files
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                prefix = f"{filepath}:{i}:" if show_lines else ""
                                results.append(f"{prefix}{line.rstrip()}")
                except:
                    continue
                    
            if not results:
                return ToolResult(
                    success=True,
                    output="No matches found"
                )
                
            output = "\n".join(results[:100])  # Limit results
            return ToolResult(
                success=True,
                output=output,
                metadata={"matches": len(results)}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


import glob as glob_module
