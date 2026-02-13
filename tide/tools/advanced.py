"""
Advanced tools for Tide OS - Like Claude Code, OpenCode, Codex
Fast, multi-file operations with proper analysis
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    output: str = ""
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, output: str) -> "ToolResult":
        return cls(success=True, output=output)
    
    @classmethod
    def err(cls, error: str) -> "ToolResult":
        return cls(success=False, error=error)


class FileTools:
    """Fast file operations - like Claude Code"""
    
    @staticmethod
    def read_file(path: str, lines: Optional[int] = None) -> ToolResult:
        """Read a file with optional line limit"""
        try:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                return ToolResult.err(f"File not found: {path}")
            
            content = p.read_text(encoding='utf-8')
            
            if lines:
                content = '\n'.join(content.splitlines()[:lines])
            
            return ToolResult.ok(f"File: {path}\nLines: {len(content.splitlines())}\n\n{content}")
        except Exception as e:
            return ToolResult.err(f"Error reading {path}: {e}")
    
    @staticmethod
    def read_multiple(paths: List[str]) -> ToolResult:
        """Read multiple files at once - fast!"""
        results = []
        for path in paths:
            try:
                p = Path(path).expanduser().resolve()
                if p.exists():
                    content = p.read_text(encoding='utf-8')
                    results.append(f"## {path}\n```\n{content}\n```")
                else:
                    results.append(f"## {path}\n[File not found]")
            except Exception as e:
                results.append(f"## {path}\n[Error: {e}]")
        
        return ToolResult.ok('\n\n'.join(results))
    
    @staticmethod
    def write_file(path: str, content: str) -> ToolResult:
        """Write content to file - creates if not exists"""
        try:
            p = Path(path).expanduser().resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return ToolResult.ok(f"✓ Written to {path}\n{len(content)} chars")
        except Exception as e:
            return ToolResult.err(f"Error writing {path}: {e}")
    
    @staticmethod
    def create_files(files: Dict[str, str]) -> ToolResult:
        """Create multiple files at once"""
        results = []
        for path, content in files.items():
            result = FileTools.write_file(path, content)
            if result.success:
                results.append(f"✓ {path}")
            else:
                results.append(f"✗ {path}: {result.error}")
        
        return ToolResult.ok('\n'.join(results))
    
    @staticmethod
    def list_files(directory: str = ".", pattern: str = "*", max_files: int = 50) -> ToolResult:
        """List files in directory matching pattern"""
        try:
            p = Path(directory).expanduser().resolve()
            if not p.exists():
                return ToolResult.err(f"Directory not found: {directory}")
            
            files = list(p.glob(pattern))[:max_files]
            file_list = []
            for f in files:
                if f.is_file():
                    size = f.stat().st_size
                    file_list.append(f"  {f.name} ({size} bytes)")
                elif f.is_dir():
                    file_list.append(f"  📁 {f.name}/")
            
            return ToolResult.ok(f"Files in {directory}:\n" + '\n'.join(file_list))
        except Exception as e:
            return ToolResult.err(f"Error listing: {e}")
    
    @staticmethod
    def search_directory(directory: str, query: str, file_pattern: str = "*.py") -> ToolResult:
        """Search for query in files - like grep but faster"""
        try:
            p = Path(directory).expanduser().resolve()
            if not p.exists():
                return ToolResult.err(f"Directory not found: {directory}")
            
            results = []
            for f in p.rglob(file_pattern):
                if f.is_file():
                    try:
                        content = f.read_text(encoding='utf-8', errors='ignore')
                        lines = content.splitlines()
                        for i, line in enumerate(lines, 1):
                            if query.lower() in line.lower():
                                results.append(f"{f}:{i}: {line.strip()}")
                    except:
                        pass
            
            if not results:
                return ToolResult.ok(f"No matches for '{query}' in {file_pattern}")
            
            return ToolResult.ok(f"Found {len(results)} matches:\n" + '\n'.join(results[:100]))
        except Exception as e:
            return ToolResult.err(f"Error searching: {e}")
    
    @staticmethod
    def analyze_code(path: str) -> ToolResult:
        """Quick code analysis - like Claude Code"""
        try:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                return ToolResult.err(f"File not found: {path}")
            
            content = p.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # Quick analysis
            analysis = {
                "path": str(p),
                "size": len(content),
                "lines": len(lines),
                "language": p.suffix[1:] if p.suffix else "unknown",
            }
            
            # Count functions/classes
            functions = re.findall(r'def\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'^\s*(?:from|import)\s+', content, re.MULTILINE)
            
            analysis["functions"] = functions
            analysis["classes"] = classes
            analysis["imports"] = len(imports)
            
            # Generate summary
            summary = f"""## Code Analysis: {p.name}

**Language:** {analysis['language']}
**Size:** {analysis['size']} bytes
**Lines:** {analysis['lines']}

**Classes:** {len(classes)}
{chr(10).join(f'  - {c}' for c in classes[:10])}

**Functions:** {len(functions)}
{chr(10).join(f'  - {f}()' for f in functions[:10])}

**Imports:** {len(imports)}

"""
            return ToolResult.ok(summary)
        except Exception as e:
            return ToolResult.err(f"Error analyzing: {e}")
    
    @staticmethod
    def find_files(directory: str, extensions: List[str] = None) -> ToolResult:
        """Find all files with specific extensions"""
        try:
            p = Path(directory).expanduser().resolve()
            if not p.exists():
                return ToolResult.err(f"Directory not found: {directory}")
            
            if not extensions:
                extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.yaml', '.yml']
            
            files = []
            for ext in extensions:
                files.extend(p.rglob(f"*{ext}"))
            
            # Sort by size
            files = sorted(files, key=lambda x: x.stat().st_size, reverse=True)
            
            file_list = [f"  {f.relative_to(p)} ({f.stat().st_size}b)" for f in files[:50]]
            
            return ToolResult.ok(f"Found {len(files)} files:\n" + '\n'.join(file_list))
        except Exception as e:
            return ToolResult.err(f"Error finding files: {e}")


class GitTools:
    """Git operations - like Claude Code"""
    
    @staticmethod
    def status() -> ToolResult:
        """Get git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return ToolResult.err("Not a git repository")
            
            if not result.stdout.strip():
                return ToolResult.ok("✓ Clean working directory")
            
            return ToolResult.ok(f"Git Status:\n{result.stdout}")
        except Exception as e:
            return ToolResult.err(f"Git error: {e}")
    
    @staticmethod
    def diff(file_path: Optional[str] = None) -> ToolResult:
        """Get git diff"""
        try:
            cmd = ["git", "diff"]
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=30
            )
            
            if not result.stdout.strip():
                return ToolResult.ok("No changes")
            
            return ToolResult.ok(result.stdout[:5000])
        except Exception as e:
            return ToolResult.err(f"Git diff error: {e}")
    
    @staticmethod
    def commit(message: str) -> ToolResult:
        """Git commit all changes"""
        try:
            # Add all
            subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10)
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return ToolResult.err(f"Commit failed: {result.stderr}")
            
            return ToolResult.ok(f"✓ Committed: {message}")
        except Exception as e:
            return ToolResult.err(f"Git error: {e}")
    
    @staticmethod
    def log(limit: int = 5) -> ToolResult:
        """Get recent commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--oneline"],
                capture_output=True, text=True, timeout=10
            )
            
            return ToolResult.ok(f"Recent commits:\n{result.stdout}")
        except Exception as e:
            return ToolResult.err(f"Git error: {e}")


class ShellTools:
    """Shell commands - fast execution"""
    
    @staticmethod
    def run(command: str, timeout: int = 30) -> ToolResult:
        """Run shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            
            return ToolResult.ok(output[:5000])
        except subprocess.TimeoutExpired:
            return ToolResult.err(f"Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult.err(f"Error: {e}")
    
    @staticmethod
    def run_python(code: str) -> ToolResult:
        """Run Python code directly"""
        try:
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            
            return ToolResult.ok(output[:5000])
        except Exception as e:
            return ToolResult.err(f"Error: {e}")


class WebTools:
    """Web operations"""
    
    @staticmethod
    def fetch_url(url: str) -> ToolResult:
        """Fetch content from URL"""
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return ToolResult.ok(f"Fetched from {url}\n\n{content[:10000]}")
        except Exception as e:
            return ToolResult.err(f"Fetch error: {e}")
    
    @staticmethod
    def search(query: str) -> ToolResult:
        """Web search"""
        # Simple search using duckduckgo
        try:
            import urllib.parse
            from urllib.request import urlopen
            import json
            
            encoded = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json"
            
            with urlopen(url, timeout=15) as response:
                data = json.loads(response.read())
                
            results = data.get('RelatedTopics', [])
            if not results:
                return ToolResult.ok("No results found")
            
            output = f"Search results for: {query}\n\n"
            for r in results[:5]:
                if 'Text' in r:
                    output += f"• {r['Text']}\n"
            
            return ToolResult.ok(output)
        except Exception as e:
            return ToolResult.err(f"Search error: {e}")


# Map to function calls - like Claude Code/OpenCode
TOOL_FUNCTIONS = {
    # File operations
    "read_file": FileTools.read_file,
    "read_multiple": FileTools.read_multiple,
    "write_file": FileTools.write_file,
    "create_files": FileTools.create_files,
    "list_files": FileTools.list_files,
    "search": FileTools.search_directory,
    "analyze_code": FileTools.analyze_code,
    "find_files": FileTools.find_files,
    
    # Git operations
    "git_status": GitTools.status,
    "git_diff": GitTools.diff,
    "git_commit": GitTools.commit,
    "git_log": GitTools.log,
    
    # Shell
    "bash": ShellTools.run,
    "python": ShellTools.run_python,
    
    # Web
    "fetch_url": WebTools.fetch_url,
    "web_search": WebTools.search,
}


def execute_tool(name: str, **params) -> ToolResult:
    """Execute a tool by name"""
    if name not in TOOL_FUNCTIONS:
        return ToolResult.err(f"Unknown tool: {name}")
    
    func = TOOL_FUNCTIONS[name]
    
    try:
        return func(**params)
    except TypeError as e:
        # Wrong parameters
        return ToolResult.err(f"Wrong parameters: {e}")
    except Exception as e:
        return ToolResult.err(f"Error: {e}")


def get_tool_schemas() -> List[Dict]:
    """Get OpenAI function schemas for all tools"""
    schemas = []
    
    # File tools schema
    schemas.extend([
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file's content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"},
                        "lines": {"type": "integer", "description": "Max lines to read (optional)"}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file (creates or overwrites)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to write"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search for text in files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory to search"},
                        "query": {"type": "string", "description": "Text to search for"},
                        "file_pattern": {"type": "string", "description": "File pattern (e.g., *.py)"}
                    },
                    "required": ["directory", "query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_code",
                "description": "Analyze code file structure (functions, classes)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to analyze"}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_files",
                "description": "Find all files with specific extensions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory to search"},
                        "extensions": {"type": "array", "items": {"type": "string"}, "description": "File extensions to find"}
                    },
                    "required": ["directory"]
                }
            }
        },
    ])
    
    # Git tools schema
    schemas.extend([
        {
            "type": "function",
            "function": {
                "name": "git_status",
                "description": "Get git repository status",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "git_diff",
                "description": "Get git diff of changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Specific file to diff (optional)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "git_commit",
                "description": "Commit all changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Commit message"}
                    },
                    "required": ["message"]
                }
            }
        },
    ])
    
    # Shell tools schema
    schemas.extend([
        {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Run a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to run"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds"}
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "python",
                "description": "Run Python code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to run"}
                    },
                    "required": ["code"]
                }
            }
        },
    ])
    
    # Web tools schema
    schemas.extend([
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_url",
                "description": "Fetch content from a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"}
                    },
                    "required": ["url"]
                }
            }
        },
    ])
    
    return schemas
