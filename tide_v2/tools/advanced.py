"""
Advanced Tools from crush
MultiEdit, Search, References, Web tools
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from difflib import unified_diff

from .base import Tool, ToolResult, ToolParameter


class MultiEditTool(Tool):
    """
    Apply multiple edits to a file at once.
    Based on crush's multiedit.go
    """
    name = "multiedit"
    description = "Apply multiple edits to a file in a single operation"
    category = "filesystem"
    requires_confirmation = True
    
    parameters = [
        ToolParameter("file_path", "string", "Path to the file to edit", True),
        ToolParameter("edits", "array", "List of edits to apply, each with 'old_string' and 'new_string'", True)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            edits = params.get("edits", [])
            
            if not file_path or not edits:
                result.error = "file_path and edits are required"
                result.success = False
                return result
            
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            # Read original content
            with open(path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            applied = 0
            failed = []
            
            # Apply each edit
            for i, edit in enumerate(edits):
                old_str = edit.get("old_string", "")
                new_str = edit.get("new_string", "")
                
                if not old_str:
                    failed.append(f"Edit {i+1}: old_string is empty")
                    continue
                
                if old_str in content:
                    content = content.replace(old_str, new_str, 1)
                    applied += 1
                else:
                    failed.append(f"Edit {i+1}: old_string not found")
            
            # Generate diff
            diff = list(unified_diff(
                original_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}"
            ))
            
            # Write if any edits applied
            if applied > 0:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Build output
            output_parts = [f"Applied {applied}/{len(edits)} edits to {file_path}"]
            
            if diff:
                output_parts.append("\nDiff:")
                output_parts.append("".join(diff[:100]))  # Limit diff size
            
            if failed:
                output_parts.append(f"\nFailed ({len(failed)}):")
                output_parts.extend(failed[:5])
            
            result.output = "\n".join(output_parts)
            result.metadata = {
                "applied": applied,
                "total": len(edits),
                "failed": len(failed)
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result


class SearchTool(Tool):
    """
    Advanced file search with content preview.
    Based on crush's search.go
    """
    name = "search"
    description = "Search for files containing specific content with context"
    category = "code"
    
    parameters = [
        ToolParameter("query", "string", "Search query (regex supported)", True),
        ToolParameter("path", "string", "Directory to search", False, "."),
        ToolParameter("include", "string", "File pattern (e.g., '*.py')", False, "*"),
        ToolParameter("exclude", "array", "Patterns to exclude", False, [".git", "node_modules"]),
        ToolParameter("max_results", "integer", "Maximum results", False, 50)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            query = params.get("query", "")
            path = params.get("path", ".")
            include = params.get("include", "*")
            exclude = params.get("exclude", [".git", "node_modules"])
            max_results = params.get("max_results", 50)
            
            if not query:
                result.error = "query is required"
                result.success = False
                return result
            
            search_path = Path(self.working_dir) / path
            
            # Try ripgrep first
            try:
                cmd = ["rg", "-n", "--json", "-C", "2", query]
                if include != "*":
                    cmd.extend(["-g", include])
                for e in exclude:
                    cmd.extend(["-g", f"!{e}"])
                cmd.append(str(search_path))
                
                output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=30)
                
                # Parse ripgrep JSON output
                matches = []
                for line in output.strip().split('\n'):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("type") == "match":
                            m = data.get("data", {})
                            matches.append({
                                "file": m.get("path", {}).get("text", ""),
                                "line": m.get("line_number", 0),
                                "text": m.get("lines", {}).get("text", "")
                            })
                    except:
                        pass
                
                if matches:
                    output_lines = [f"🔍 Found {len(matches)} matches for '{query}':\n"]
                    for m in matches[:max_results]:
                        output_lines.append(f"\n📄 {m['file']}:{m['line']}")
                        output_lines.append(f"   {m['text'][:100]}")
                    
                    result.output = "\n".join(output_lines)
                    result.metadata = {"matches": len(matches), "query": query}
                    return result
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            # Fallback to Python search
            matches = []
            pattern = re.compile(query, re.IGNORECASE)
            
            for root, dirs, files in os.walk(search_path):
                # Exclude directories
                dirs[:] = [d for d in dirs if d not in exclude]
                
                for file in files:
                    if not self._match_pattern(file, include):
                        continue
                    
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                if pattern.search(line):
                                    matches.append({
                                        "file": str(file_path.relative_to(self.working_dir)),
                                        "line": i,
                                        "text": line.strip()[:100]
                                    })
                                    if len(matches) >= max_results:
                                        break
                    except:
                        pass
                    
                    if len(matches) >= max_results:
                        break
                
                if len(matches) >= max_results:
                    break
            
            if matches:
                output_lines = [f"🔍 Found {len(matches)} matches for '{query}':\n"]
                for m in matches:
                    output_lines.append(f"\n📄 {m['file']}:{m['line']}")
                    output_lines.append(f"   {m['text']}")
                result.output = "\n".join(output_lines)
            else:
                result.output = f"No matches found for: {query}"
            
            result.metadata = {"matches": len(matches), "query": query}
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)


class ReferencesTool(Tool):
    """
    Find references to symbols in code.
    Based on crush's references.go
    """
    name = "references"
    description = "Find all references to a function, class, or variable in the codebase"
    category = "code"
    
    parameters = [
        ToolParameter("symbol", "string", "Symbol name to search for", True),
        ToolParameter("path", "string", "Directory to search", False, "."),
        ToolParameter("language", "string", "Language (python, javascript, go, etc.)", False, "")
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            symbol = params.get("symbol", "")
            path = params.get("path", ".")
            language = params.get("language", "")
            
            if not symbol:
                result.error = "symbol is required"
                result.success = False
                return result
            
            search_path = Path(self.working_dir) / path
            
            # Determine file patterns
            patterns = self._get_patterns(language)
            
            # Search patterns
            reference_patterns = [
                rf'\b{re.escape(symbol)}\b',  # Word boundary
                rf'\.{re.escape(symbol)}\b',  # Method call
                rf'\b{re.escape(symbol)}\s*\(',  # Function call
                rf'\b{re.escape(symbol)}\s*=',  # Assignment
            ]
            
            references = []
            
            for root, dirs, files in os.walk(search_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                
                for file in files:
                    if not any(file.endswith(ext) for ext in patterns):
                        continue
                    
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for i, line in enumerate(lines, 1):
                                for pattern in reference_patterns:
                                    if re.search(pattern, line):
                                        # Determine context
                                        context = self._get_context(line, symbol)
                                        references.append({
                                            "file": str(file_path.relative_to(self.working_dir)),
                                            "line": i,
                                            "context": context,
                                            "code": line.strip()[:80]
                                        })
                                        break
                    except:
                        pass
            
            # Format output
            if references:
                output = f"📎 Found {len(references)} references to '{symbol}':\n\n"
                
                # Group by file
                by_file = {}
                for ref in references:
                    f = ref["file"]
                    if f not in by_file:
                        by_file[f] = []
                    by_file[f].append(ref)
                
                for file, refs in sorted(by_file.items()):
                    output += f"📄 {file}\n"
                    for r in refs[:5]:  # Limit per file
                        output += f"  Line {r['line']}: {r['code']}\n"
                    if len(refs) > 5:
                        output += f"  ... and {len(refs) - 5} more\n"
                    output += "\n"
            else:
                output = f"No references found for: {symbol}"
            
            result.output = output
            result.metadata = {
                "symbol": symbol,
                "total_references": len(references),
                "files": len(by_file) if references else 0
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _get_patterns(self, language: str) -> List[str]:
        """Get file patterns for language"""
        patterns = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "go": [".go"],
            "rust": [".rs"],
            "java": [".java"],
            "c": [".c", ".h"],
            "cpp": [".cpp", ".hpp"],
            "ruby": [".rb"],
        }
        return patterns.get(language, [".py", ".js", ".ts", ".go", ".rs", ".java"])
    
    def _get_context(self, line: str, symbol: str) -> str:
        """Determine the context of the reference"""
        line = line.strip()
        if re.search(rf'\bdef\s+{re.escape(symbol)}\b', line):
            return "definition"
        elif re.search(rf'\bclass\s+{re.escape(symbol)}\b', line):
            return "class"
        elif re.search(rf'\.{re.escape(symbol)}\s*\(', line):
            return "method_call"
        elif re.search(rf'\b{re.escape(symbol)}\s*=', line):
            return "assignment"
        elif re.search(rf'\b{re.escape(symbol)}\s*\(', line):
            return "function_call"
        else:
            return "reference"


class WebFetchTool(Tool):
    """
    Fetch content from web URLs.
    Based on crush's web_fetch.go
    """
    name = "web_fetch"
    description = "Fetch and extract content from a web URL"
    category = "web"
    
    parameters = [
        ToolParameter("url", "string", "URL to fetch", True),
        ToolParameter("max_length", "integer", "Maximum content length", False, 10000)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            url = params.get("url", "")
            max_length = params.get("max_length", 10000)
            
            if not url:
                result.error = "url is required"
                result.success = False
                return result
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                result.error = "URL must start with http:// or https://"
                result.success = False
                return result
            
            import urllib.request
            import ssl
            
            # Create SSL context that allows us to fetch
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Fetch with timeout
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; TideOS/2.0)'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/html' in content_type:
                    html = response.read().decode('utf-8', errors='ignore')
                    # Extract text from HTML (basic)
                    text = self._extract_text(html)
                else:
                    text = response.read().decode('utf-8', errors='ignore')
                
                # Truncate
                if len(text) > max_length:
                    text = text[:max_length] + "\n\n[Content truncated...]"
                
                result.output = f"🌐 Fetched: {url}\n\n{text}"
                result.metadata = {
                    "url": url,
                    "content_type": content_type,
                    "length": len(text)
                }
                
        except Exception as e:
            result.error = f"Failed to fetch URL: {str(e)}"
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML"""
        # Remove script and style
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()


class DiagnosticsTool(Tool):
    """
    Run diagnostics on code.
    Based on crush's diagnostics.go
    """
    name = "diagnostics"
    description = "Run code diagnostics and linting on a file"
    category = "code"
    
    parameters = [
        ToolParameter("file_path", "string", "Path to file to analyze", True),
        ToolParameter("language", "string", "Language (python, javascript, etc.)", False, "")
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            language = params.get("language", "")
            
            if not file_path:
                result.error = "file_path is required"
                result.success = False
                return result
            
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            # Detect language
            if not language:
                language = self._detect_language(file_path)
            
            diagnostics = []
            
            if language == "python":
                diagnostics = self._check_python(path)
            elif language in ["javascript", "typescript"]:
                diagnostics = self._check_javascript(path)
            else:
                diagnostics = self._check_generic(path)
            
            # Format output
            if diagnostics:
                output = f"🔍 Diagnostics for {file_path}:\n\n"
                for d in diagnostics[:20]:
                    severity = d.get("severity", "info")
                    emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
                    output += f"{emoji} Line {d.get('line', '?')}: {d.get('message')}\n"
            else:
                output = f"✅ No issues found in {file_path}"
            
            result.output = output
            result.metadata = {
                "file": file_path,
                "language": language,
                "issues": len(diagnostics)
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
        }
        return mapping.get(ext, "generic")
    
    def _check_python(self, path: Path) -> List[Dict]:
        """Check Python file for issues"""
        issues = []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                # Check for print statements
                if 'print(' in line and 'def ' not in line:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": "Consider using logging instead of print"
                    })
                
                # Check for bare except
                if 'except:' in line and 'except ' not in line:
                    issues.append({
                        "line": i,
                        "severity": "warning",
                        "message": "Bare except clause - should catch specific exceptions"
                    })
                
                # Check line length
                if len(line) > 120:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": f"Line too long ({len(line)} chars)"
                    })
            
            # Try parsing with AST
            import ast
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    "line": e.lineno or 1,
                    "severity": "error",
                    "message": f"Syntax error: {e.msg}"
                })
                
        except Exception as e:
            issues.append({
                "line": 1,
                "severity": "error",
                "message": str(e)
            })
        
        return issues
    
    def _check_javascript(self, path: Path) -> List[Dict]:
        """Check JavaScript file"""
        issues = []
        
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if 'console.log' in line:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": "Consider removing console.log"
                    })
                if len(line) > 120:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": f"Line too long ({len(line)} chars)"
                    })
        
        return issues
    
    def _check_generic(self, path: Path) -> List[Dict]:
        """Generic file checks"""
        issues = []
        
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if len(line) > 120:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": f"Line too long ({len(line)} chars)"
                    })
                if '\t' in line:
                    issues.append({
                        "line": i,
                        "severity": "info",
                        "message": "Contains tabs - consider using spaces"
                    })
        
        return issues
