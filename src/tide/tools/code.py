"""
Code Analysis Tools
"""

import os
import ast
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base import Tool, ToolResult


class AnalyzeCodeTool(Tool):
    """Analyze code structure"""
    
    name = "analyze_code"
    description = "Analyze Python code structure (AST-based)"
    category = "code"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to Python file"
            }
        },
        "required": ["file_path"]
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        file_path = os.path.expanduser(kwargs.get("file_path", ""))
        
        if not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}"
            )
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                
            tree = ast.parse(source)
            
            info = {
                "file": file_path,
                "lines": len(source.splitlines()),
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            # Parse AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    info["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    info["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            info["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            info["imports"].append(f"{module}.{alias.name}" if module else alias.name)
                            
            # Format output
            output = f"📊 Code Analysis: {file_path}\n"
            output += f"Lines: {info['lines']}\n\n"
            
            output += f"📦 Imports ({len(info['imports'])}):\n"
            for imp in info["imports"][:10]:
                output += f"  • {imp}\n"
            if len(info["imports"]) > 10:
                output += f"  ... and {len(info['imports']) - 10} more\n"
                
            output += f"\n🔧 Functions ({len(info['functions'])}):\n"
            for func in info["functions"][:10]:
                output += f"  • {func['name']}({', '.join(func['args'])}) @ line {func['line']}\n"
            if len(info["functions"]) > 10:
                output += f"  ... and {len(info['functions']) - 10} more\n"
                
            output += f"\n🏛️ Classes ({len(info['classes'])}):\n"
            for cls in info["classes"]:
                output += f"  • {cls['name']} @ line {cls['line']}\n"
                for method in cls["methods"][:5]:
                    output += f"      - {method}()\n"
                    
            return ToolResult(
                success=True,
                output=output
            )
        except SyntaxError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Syntax error: {e}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class FindTodosTool(Tool):
    """Find TODO/FIXME markers"""
    
    name = "find_todos"
    description = "Find TODO, FIXME, and other markers in code"
    category = "code"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory or file to search"
            },
            "markers": {
                "type": "string",
                "description": "Comma-separated markers (default: TODO,FIXME,HACK,XXX)"
            }
        }
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        path = os.path.expanduser(kwargs.get("path", "."))
        markers_str = kwargs.get("markers", "TODO,FIXME,HACK,XXX")
        markers = [m.strip() for m in markers_str.split(",")]
        
        results = []
        
        try:
            if os.path.isfile(path):
                files = [path]
            else:
                files = []
                for root, _, filenames in os.walk(path):
                    for f in filenames:
                        if f.endswith((".py", ".js", ".ts", ".go", ".rs", ".md")):
                            files.append(os.path.join(root, f))
                            
            for filepath in files[:50]:
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            for marker in markers:
                                if marker in line:
                                    results.append(f"{filepath}:{i}: {line.strip()}")
                except:
                    continue
                    
            if not results:
                return ToolResult(
                    success=True,
                    output="No TODO/FIXME markers found"
                )
                
            output = f"🔍 Found {len(results)} markers:\n\n"
            output += "\n".join(results[:50])
            
            return ToolResult(
                success=True,
                output=output,
                metadata={"count": len(results)}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class ProjectStructureTool(Tool):
    """Show project structure"""
    
    name = "project_structure"
    description = "Show project directory structure"
    category = "code"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project root directory"
            },
            "exclude": {
                "type": "string",
                "description": "Comma-separated patterns to exclude"
            }
        }
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        path = os.path.expanduser(kwargs.get("path", "."))
        exclude_str = kwargs.get("exclude", "__pycache__,.git,node_modules,venv,.venv")
        exclude = exclude_str.split(",")
        
        if not os.path.exists(path):
            return ToolResult(
                success=False,
                output="",
                error=f"Path not found: {path}"
            )
            
        lines = [path]
        
        def walk_tree(dir_path: str, prefix: str = "", depth: int = 0):
            if depth > 3:
                return
                
            try:
                entries = sorted(
                    os.listdir(dir_path),
                    key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x)
                )
                    
                for i, entry in enumerate(entries):
                    if entry in exclude or entry.startswith("."):
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
                        
                    if is_dir:
                        walk_tree(full_path, new_prefix, depth + 1)
            except PermissionError:
                pass
                
        walk_tree(path)
        
        return ToolResult(
            success=True,
            output="\n".join(lines)
        )


class ExplainErrorTool(Tool):
    """Explain error messages"""
    
    name = "explain_error"
    description = "Explain error messages"
    category = "code"
    parameters = {
        "type": "object",
        "properties": {
            "error": {
                "type": "string",
                "description": "Error message to explain"
            }
        },
        "required": ["error"]
    }
    requires_confirmation = False
    
    ERROR_EXPLANATIONS = {
        "SyntaxError": "The code has invalid syntax that Python cannot parse.",
        "IndentationError": "There are incorrect indentation levels.",
        "NameError": "A variable or function name is not defined.",
        "TypeError": "An operation was performed on the wrong data type.",
        "AttributeError": "An object does not have the specified attribute.",
        "ImportError": "A module could not be imported.",
        "FileNotFoundError": "The specified file does not exist.",
        "PermissionError": "You don't have permission to access this.",
        "IndexError": "An index is out of range.",
        "KeyError": "A dictionary key was not found.",
        "ValueError": "A function received an inappropriate value.",
        "ZeroDivisionError": "Division by zero attempted.",
    }
    
    def execute(self, **kwargs) -> ToolResult:
        error = kwargs.get("error", "")
        
        # Try to identify error type
        for error_type, explanation in self.ERROR_EXPLANATIONS.items():
            if error_type in error:
                return ToolResult(
                    success=True,
                    output=f"🔴 {error_type}\n\n{explanation}\n\nFull error: {error}"
                )
                
        return ToolResult(
            success=True,
            output=f"I couldn't identify the specific error type.\n\nError: {error}\n\nPlease provide more context for a better explanation."
        )
