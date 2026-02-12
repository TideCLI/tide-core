"""
Optimized Code Tools - Based on crush's grep and analysis
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import Tool, ToolResult, ToolParameter


class AnalyzeTool(Tool):
    """Analyze code using AST"""
    name = "analyze_code"
    description = "Analyze Python code structure using AST"
    category = "code"
    
    parameters = [
        ToolParameter("file_path", "string", "Path to Python file", True),
        ToolParameter("show_source", "boolean", "Show source for each item", False, False)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            show_source = params.get("show_source", False)
            
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            try:
                tree = ast.parse(source)
            except SyntaxError as e:
                result.error = f"Syntax error: {e}"
                result.success = False
                return result
            
            analysis = {
                "imports": [],
                "functions": [],
                "classes": [],
                "docstrings": {}
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis["imports"].append(f"{module}.{alias.name}")
                
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node)
                    }
                    analysis["functions"].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [],
                        "docstring": ast.get_docstring(node)
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)
                    analysis["classes"].append(class_info)
            
            # Format output
            output = f"📊 Code Analysis: {file_path}\n"
            output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Imports
            if analysis["imports"]:
                output += f"📦 Imports ({len(analysis['imports'])}):\n"
                for imp in sorted(set(analysis["imports"]))[:20]:
                    output += f"  • {imp}\n"
                output += "\n"
            
            # Functions
            if analysis["functions"]:
                output += f"🔧 Functions ({len(analysis['functions'])}):\n"
                for func in analysis["functions"][:15]:
                    output += f"  • {func['name']}() at line {func['line']}"
                    if func['docstring']:
                        output += f" - \"{func['docstring'][:50]}...\""
                    output += "\n"
                output += "\n"
            
            # Classes
            if analysis["classes"]:
                output += f"🏛️ Classes ({len(analysis['classes'])}):\n"
                for cls in analysis["classes"]:
                    output += f"  • {cls['name']} at line {cls['line']}"
                    if cls['methods']:
                        output += f" ({len(cls['methods'])} methods)"
                    output += "\n"
                output += "\n"
            
            result.output = output
            result.metadata = {
                "imports": len(analysis["imports"]),
                "functions": len(analysis["functions"]),
                "classes": len(analysis["classes"])
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result


class GrepTool(Tool):
    """Search files using grep/rg"""
    name = "grep"
    description = "Search for patterns in files using ripgrep"
    category = "code"
    
    parameters = [
        ToolParameter("pattern", "string", "Search pattern (regex)", True),
        ToolParameter("path", "string", "Directory to search", False, "."),
        ToolParameter("include", "string", "File glob pattern (e.g., '*.py')", False, ""),
        ToolParameter("context", "integer", "Lines of context", False, 2)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            pattern = params.get("pattern", "")
            path = params.get("path", ".")
            include = params.get("include", "")
            context = params.get("context", 2)
            
            if not pattern:
                result.error = "pattern is required"
                result.success = False
                return result
            
            search_path = Path(self.working_dir) / path
            
            # Try ripgrep first, fallback to grep
            cmd_parts = ["rg", "--smart-case", "-n", f"-C", str(context)]
            
            if include:
                cmd_parts.extend(["-g", include])
            
            cmd_parts.extend([pattern, str(search_path)])
            
            try:
                output = subprocess.check_output(
                    cmd_parts, stderr=subprocess.DEVNULL, text=True, timeout=10
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to grep
                cmd_parts = ["grep", "-r", "-n", f"-C", str(context), pattern, str(search_path)]
                if include:
                    cmd_parts.extend(["--include", include])
                
                try:
                    output = subprocess.check_output(
                        cmd_parts, stderr=subprocess.DEVNULL, text=True, timeout=10
                    )
                except subprocess.CalledProcessError:
                    output = ""
            
            # Format output
            if output:
                lines = output.strip().split('\n')
                formatted = []
                current_file = None
                
                for line in lines[:100]:  # Limit results
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            file_path, line_num, content = parts[0], parts[1], parts[2]
                            
                            if file_path != current_file:
                                current_file = file_path
                                formatted.append(f"\n📄 {file_path}")
                            
                            # Colorize match
                            content_colored = content.replace(pattern, f"\033[91m{pattern}\033[0m")
                            formatted.append(f"  {line_num:4}: {content_colored}")
                        else:
                            formatted.append(f"  {line}")
                    else:
                        formatted.append(f"  {line}")
                
                result.output = '\n'.join(formatted)
                result.metadata = {"matches": len(lines), "pattern": pattern}
            else:
                result.output = f"No matches found for: {pattern}"
                result.metadata = {"matches": 0}
            
        except subprocess.TimeoutExpired:
            result.error = "Search timed out"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result


class TodosTool(Tool):
    """Find TODOs and FIXMEs in code"""
    name = "find_todos"
    description = "Find TODO, FIXME, and other markers in code"
    category = "code"
    
    parameters = [
        ToolParameter("path", "string", "Directory to search", False, "."),
        ToolParameter("patterns", "array", "Patterns to search for", False, ["TODO", "FIXME", "HACK", "NOTE"])
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            path = params.get("path", ".")
            patterns = params.get("patterns", ["TODO", "FIXME", "HACK", "NOTE"])
            
            search_path = Path(self.working_dir) / path
            
            # Build regex pattern
            pattern_str = '|'.join(patterns)
            regex = re.compile(rf'({pattern_str})[:\s]+(.+)', re.IGNORECASE)
            
            findings = []
            
            # Walk directory
            for root, dirs, files in os.walk(search_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp', '.c', '.h', '.md')):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for i, line in enumerate(f, 1):
                                    match = regex.search(line)
                                    if match:
                                        findings.append({
                                            'file': str(file_path.relative_to(self.working_dir)),
                                            'line': i,
                                            'type': match.group(1).upper(),
                                            'text': match.group(2).strip()[:80]
                                        })
                        except:
                            pass
            
            # Format output
            if findings:
                output = f"🔍 Found {len(findings)} markers:\n\n"
                
                for item in sorted(findings, key=lambda x: x['type']):
                    emoji = {"TODO": "✅", "FIXME": "🔧", "HACK": "⚠️", "NOTE": "📝"}.get(item['type'], "📌")
                    output += f"{emoji} {item['type']}: {item['file']}:{item['line']}\n"
                    output += f"   {item['text']}\n\n"
            else:
                output = "No TODOs, FIXMEs, or other markers found."
            
            result.output = output
            result.metadata = {"total": len(findings), "by_type": {t: len([f for f in findings if f['type'] == t]) for t in patterns}}
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
