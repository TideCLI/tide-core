"""
Code analysis tools - AST parsing and code understanding
"""

import ast
import re
import difflib
from pathlib import Path
from typing import List, Dict
from internal.tools.base import Tool, ToolResult


class CodeTools:
    """Code analysis tool collection"""
    
    def get_tools(self) -> List[Tool]:
        """Get all code tools"""
        return [
            Tool(
                name="analyze_code",
                description="Analyze Python code structure (imports, functions, classes)",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"]
                },
                func=self.analyze_code,
                category="code"
            ),
            Tool(
                name="grep",
                description="Search pattern in files with context",
                parameters={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"},
                        "include": {"type": "string"},
                        "context": {"type": "integer"}
                    },
                    "required": ["pattern", "path"]
                },
                func=self.grep,
                category="code"
            ),
            Tool(
                name="view_diff",
                description="Show diff between two files",
                parameters={
                    "type": "object",
                    "properties": {
                        "file1": {"type": "string"},
                        "file2": {"type": "string"}
                    },
                    "required": ["file1", "file2"]
                },
                func=self.view_diff,
                category="code"
            ),
            Tool(
                name="count_lines",
                description="Count lines of code by file type",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"]
                },
                func=self.count_lines,
                category="code"
            ),
            Tool(
                name="find_todos",
                description="Find TODO, FIXME, XXX comments",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "include": {"type": "string"}
                    },
                    "required": ["path"]
                },
                func=self.find_todos,
                category="code"
            ),
            Tool(
                name="git_status",
                description="Show git repository status",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"]
                },
                func=self.git_status,
                category="git"
            ),
        ]
    
    def analyze_code(self, params: Dict) -> ToolResult:
        """Analyze Python code with AST"""
        try:
            path = Path(params["path"]).expanduser()
            
            with open(path, 'r') as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return ToolResult(False, "", f"Syntax error: {e}")
            
            analysis = {
                "imports": [],
                "functions": [],
                "classes": [],
                "docstrings": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    analysis["imports"].append(module)
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node)[:50] if ast.get_docstring(node) else None
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis["classes"].append({
                        "name": node.name,
                        "methods": methods,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node)[:50] if ast.get_docstring(node) else None
                    })
            
            # Format output
            result = f"📊 Code Analysis: {path.name}\n\n"
            
            result += f"📦 Imports ({len(analysis['imports'])}):\n"
            for imp in analysis["imports"][:15]:
                result += f"  • {imp}\n"
            
            result += f"\n🔧 Functions ({len(analysis['functions'])}):\n"
            for func in analysis["functions"][:15]:
                doc = f" - {func['docstring']}" if func['docstring'] else ""
                result += f"  • {func['name']}() at line {func['line']}{doc}\n"
            
            result += f"\n🏛️ Classes ({len(analysis['classes'])}):\n"
            for cls in analysis["classes"][:10]:
                doc = f" - {cls['docstring']}" if cls['docstring'] else ""
                result += f"  • {cls['name']} ({len(cls['methods'])} methods) at line {cls['line']}{doc}\n"
            
            return ToolResult(True, result)
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def grep(self, params: Dict) -> ToolResult:
        """Grep with context"""
        try:
            pattern = params["pattern"]
            path = Path(params["path"]).expanduser()
            include = params.get("include", "*")
            context = params.get("context", 2)
            
            matches = []
            files = list(path.rglob(include)) if path.is_dir() else [path]
            
            for f in files:
                if not f.is_file():
                    continue
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        lines = file.readlines()
                        for i, line in enumerate(lines):
                            if re.search(pattern, line):
                                start = max(0, i - context)
                                end = min(len(lines), i + context + 1)
                                
                                match_text = f"\n[File: {f}:{i+1}]\n"
                                for j in range(start, end):
                                    marker = ">>> " if j == i else "    "
                                    match_text += f"{marker}{j+1:4}: {lines[j]}"
                                matches.append(match_text)
                                
                                if len(matches) >= 20:
                                    break
                except:
                    continue
                if len(matches) >= 20:
                    break
            
            return ToolResult(True, "\n".join(matches) or "No matches found")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def view_diff(self, params: Dict) -> ToolResult:
        """Show diff between files"""
        try:
            file1 = Path(params["file1"]).expanduser()
            file2 = Path(params["file2"]).expanduser()
            
            with open(file1, 'r') as f1, open(file2, 'r') as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()
            
            diff = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=str(file1.name),
                tofile=str(file2.name),
                lineterm=''
            ))
            
            return ToolResult(True, "\n".join(diff) if diff else "Files are identical")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def count_lines(self, params: Dict) -> ToolResult:
        """Count lines by type"""
        try:
            path = Path(params["path"]).expanduser()
            
            stats = {}
            total_lines = 0
            
            for f in path.rglob("*"):
                if f.is_file():
                    ext = f.suffix or "no_ext"
                    try:
                        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                            lines = len(file.readlines())
                            stats[ext] = stats.get(ext, {"files": 0, "lines": 0})
                            stats[ext]["files"] += 1
                            stats[ext]["lines"] += lines
                            total_lines += lines
                    except:
                        pass
            
            result = f"📊 Lines of Code\n"
            result += f"Total: {total_lines:,} lines\n\n"
            
            sorted_stats = sorted(stats.items(), key=lambda x: x[1]["lines"], reverse=True)
            for ext, data in sorted_stats[:10]:
                result += f"{ext:10} {data['files']:4} files  {data['lines']:8,} lines\n"
            
            return ToolResult(True, result)
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def find_todos(self, params: Dict) -> ToolResult:
        """Find TODO comments"""
        try:
            path = Path(params["path"]).expanduser()
            include = params.get("include", "*")
            
            todos = []
            files = list(path.rglob(include))
            
            for f in files:
                if not f.is_file():
                    continue
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        for i, line in enumerate(file, 1):
                            if re.search(r'(TODO|FIXME|XXX|HACK|BUG|NOTE|WARNING)', line, re.IGNORECASE):
                                todos.append(f"{f}:{i}: {line.strip()}")
                                if len(todos) >= 50:
                                    break
                except:
                    continue
                if len(todos) >= 50:
                    break
            
            return ToolResult(True, "\n".join(todos) or "No TODOs found")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def git_status(self, params: Dict) -> ToolResult:
        """Git status"""
        try:
            import subprocess
            path = Path(params["path"]).expanduser()
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=path,
                capture_output=True,
                text=True
            )
            return ToolResult(True, result.stdout or "No changes")
        except Exception as e:
            return ToolResult(False, "", str(e))
