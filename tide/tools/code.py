"""
Code analysis tools - grep, analyze, find_todos
"""
import re
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


@register_tool
class GrepTool(Tool):
    """Search file contents using patterns (like ripgrep)"""
    
    name = "grep"
    description = "Search for patterns in files"
    category = "code"
    
    parameters = {
        "pattern": Parameter(
            name="pattern",
            type=ParameterType.STRING,
            description="Pattern to search for (regex supported)",
            required=True
        ),
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Directory or file to search in",
            required=False,
            default="."
        ),
        "file_pattern": Parameter(
            name="file_pattern",
            type=ParameterType.STRING,
            description="Only search files matching this pattern (e.g., '*.py')",
            required=False,
            default=None
        )
    }
    
    def _execute(self, pattern: str, path: str = ".", file_pattern: str = None) -> ToolResult:
        try:
            search_path = Path(path).expanduser().resolve()
            max_results = self.context.get_config("grep.max_results", 100)
            context_lines = self.context.get_config("grep.context_lines", 2)
            
            results = []
            count = 0
            
            # Determine files to search
            if search_path.is_file():
                files = [search_path]
            else:
                if file_pattern:
                    files = list(search_path.rglob(file_pattern))
                else:
                    files = list(search_path.rglob("*"))
                files = [f for f in files if f.is_file()]
            
            # Search each file
            for file_path in files:
                if count >= max_results:
                    break
                
                # Skip binary/large files
                try:
                    if file_path.stat().st_size > 1024 * 1024:  # 1MB
                        continue
                    with open(file_path, 'rb') as f:
                        if b'\x00' in f.read(1024):  # Binary check
                            continue
                except:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()
                except:
                    continue
                
                for i, line in enumerate(lines):
                    try:
                        if re.search(pattern, line):
                            # Build context
                            start = max(0, i - context_lines)
                            end = min(len(lines), i + context_lines + 1)
                            
                            context = []
                            for j in range(start, end):
                                prefix = ">>> " if j == i else "    "
                                context.append(f"{prefix}{j + 1:4d}: {lines[j].rstrip()}")
                            
                            results.append({
                                "file": str(file_path.relative_to(search_path) if search_path.is_dir() else file_path),
                                "line": i + 1,
                                "match": line.strip(),
                                "context": '\n'.join(context)
                            })
                            count += 1
                            
                            if count >= max_results:
                                break
                    except re.error as e:
                        return ToolResult.error_result(f"Invalid regex pattern: {e}")
            
            # Format output
            output_parts = [f"🔍 Pattern: '{pattern}'"]
            output_parts.append(f"📁 Path: {search_path}")
            output_parts.append(f"📄 Results: {len(results)}\n")
            output_parts.append("─" * 60)
            
            for r in results:
                output_parts.append(f"\n{r['file']}:{r['line']}")
                output_parts.append(r['context'])
            
            if not results:
                output_parts.append("\n(no matches found)")
            
            return ToolResult.success_result(
                output='\n'.join(output_parts),
                pattern=pattern,
                results=results,
                count=len(results)
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error searching: {str(e)}")


@register_tool
class AnalyzeTool(Tool):
    """Analyze code using AST for Python files"""
    
    name = "analyze_code"
    description = "Analyze code structure (imports, functions, classes)"
    category = "code"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to code file or directory",
            required=True
        )
    }
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                "file": str(file_path),
                "imports": [],
                "functions": [],
                "classes": [],
                "docstrings": 0,
                "lines": len(content.splitlines())
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    names = [alias.name for alias in node.names]
                    analysis["imports"].append(f"{module}: {', '.join(names)}")
                elif isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    analysis["functions"].append({
                        "name": node.name,
                        "args": args,
                        "docstring": ast.get_docstring(node) is not None
                    })
                    if ast.get_docstring(node):
                        analysis["docstrings"] += 1
                elif isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body 
                        if isinstance(n, ast.FunctionDef)
                    ]
                    analysis["classes"].append({
                        "name": node.name,
                        "methods": methods,
                        "docstring": ast.get_docstring(node) is not None
                    })
                    if ast.get_docstring(node):
                        analysis["docstrings"] += 1
            
            return analysis
            
        except SyntaxError as e:
            return {"file": str(file_path), "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"file": str(file_path), "error": str(e)}
    
    def _execute(self, path: str) -> ToolResult:
        try:
            target_path = Path(path).expanduser().resolve()
            
            if not target_path.exists():
                return ToolResult.error_result(f"Path not found: {path}")
            
            # Collect files
            if target_path.is_file():
                files = [target_path] if target_path.suffix == '.py' else []
            else:
                files = list(target_path.rglob("*.py"))
                # Exclude common non-project paths
                files = [
                    f for f in files 
                    if not any(x in str(f) for x in ['__pycache__', '.venv', 'node_modules', '.git'])
                ][:20]  # Limit files
            
            if not files:
                return ToolResult.error_result("No Python files found")
            
            # Analyze each file
            all_analysis = [self._analyze_file(f) for f in files]
            
            # Aggregate stats
            total_functions = sum(len(a.get("functions", [])) for a in all_analysis)
            total_classes = sum(len(a.get("classes", [])) for a in all_analysis)
            total_imports = sum(len(a.get("imports", [])) for a in all_analysis)
            total_docstrings = sum(a.get("docstrings", 0) for a in all_analysis)
            total_lines = sum(a.get("lines", 0) for a in all_analysis)
            
            # Build output
            output_parts = [
                "📊 Code Analysis Report",
                f"   Files: {len(files)}",
                f"   Lines: {total_lines}",
                f"   Classes: {total_classes}",
                f"   Functions: {total_functions}",
                f"   Imports: {total_imports}",
                f"   Docstrings: {total_docstrings}",
                ""
            ]
            
            for analysis in all_analysis:
                if "error" in analysis:
                    output_parts.append(f"⚠️  {analysis['file']}: {analysis['error']}")
                    continue
                
                output_parts.append(f"📄 {analysis['file']}")
                
                if analysis['classes']:
                    output_parts.append(f"   Classes ({len(analysis['classes'])}):")
                    for cls in analysis['classes']:
                        doc = " 📝" if cls['docstring'] else ""
                        output_parts.append(f"      • {cls['name']}{doc}")
                
                if analysis['functions']:
                    output_parts.append(f"   Functions ({len(analysis['functions'])}):")
                    for func in analysis['functions'][:5]:  # Limit displayed
                        args = ', '.join(func['args'][:4])  # Limit args
                        if len(func['args']) > 4:
                            args += ', ...'
                        doc = " 📝" if func['docstring'] else ""
                        output_parts.append(f"      • {func['name']}({args}){doc}")
                    if len(analysis['functions']) > 5:
                        output_parts.append(f"      ... and {len(analysis['functions']) - 5} more")
                
                output_parts.append("")
            
            return ToolResult.success_result(
                output='\n'.join(output_parts),
                files_analyzed=len(files),
                total_functions=total_functions,
                total_classes=total_classes,
                total_lines=total_lines
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error analyzing code: {str(e)}")


@register_tool
class TodosTool(Tool):
    """Find TODO, FIXME, XXX markers in code"""
    
    name = "find_todos"
    description = "Find TODO, FIXME, and other markers in code"
    category = "code"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Directory to search",
            required=False,
            default="."
        ),
        "pattern": Parameter(
            name="pattern",
            type=ParameterType.STRING,
            description="Marker pattern (TODO, FIXME, or ALL)",
            required=False,
            default="ALL",
            enum=["TODO", "FIXME", "XXX", "HACK", "ALL"]
        )
    }
    
    MARKERS = {
        "TODO": r'#\s*TODO[:\s]',
        "FIXME": r'#\s*FIXME[:\s]',
        "XXX": r'#\s*XXX[:\s]',
        "HACK": r'#\s*HACK[:\s]'
    }
    
    def _execute(self, path: str = ".", pattern: str = "ALL") -> ToolResult:
        try:
            search_path = Path(path).expanduser().resolve()
            
            # Determine patterns to search
            if pattern == "ALL":
                patterns = self.MARKERS
            else:
                patterns = {pattern: self.MARKERS.get(pattern, r'#\s*' + pattern)}
            
            todos = []
            
            # Find code files
            code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.c', '.cpp', '.h'}
            
            if search_path.is_file():
                files = [search_path] if search_path.suffix in code_extensions else []
            else:
                files = [
                    f for f in search_path.rglob("*") 
                    if f.is_file() and f.suffix in code_extensions
                    and not any(x in str(f) for x in ['__pycache__', '.venv', 'node_modules'])
                ][:50]
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        for i, line in enumerate(f, 1):
                            for marker, regex in patterns.items():
                                if re.search(regex, line, re.IGNORECASE):
                                    todos.append({
                                        "file": str(file_path.relative_to(search_path) if search_path.is_dir() else file_path),
                                        "line": i,
                                        "marker": marker,
                                        "text": line.strip()
                                    })
                                    break
                except:
                    continue
            
            # Sort by marker type
            todos.sort(key=lambda x: (x['marker'], x['file'], x['line']))
            
            # Build output
            output_parts = [f"📝 Code Markers ({pattern})\n"]
            
            current_marker = None
            for todo in todos:
                if todo['marker'] != current_marker:
                    current_marker = todo['marker']
                    emoji = {"TODO": "☐", "FIXME": "🔧", "XXX": "⚠️", "HACK": "🔨"}.get(current_marker, "•")
                    output_parts.append(f"\n{emoji} {current_marker}:")
                
                output_parts.append(f"  {todo['file']}:{todo['line']} {todo['text'][:60]}")
            
            if not todos:
                output_parts.append("(no markers found)")
            else:
                output_parts.append(f"\nTotal: {len(todos)} markers")
            
            return ToolResult.success_result(
                output='\n'.join(output_parts),
                todos=todos,
                count=len(todos)
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error finding todos: {str(e)}")
