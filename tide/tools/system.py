"""
System tools - bash, python execution
Security-focused with timeouts and banned commands
"""
import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


class TimeoutError(Exception):
    pass


@contextmanager
def time_limit(seconds: int):
    """Context manager for timeouts"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Command timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


@register_tool
class BashTool(Tool):
    """Execute bash commands with safety controls"""
    
    name = "bash"
    description = "Execute a bash command"
    category = "system"
    require_confirmation = True
    
    parameters = {
        "command": Parameter(
            name="command",
            type=ParameterType.STRING,
            description="The bash command to execute",
            required=True
        ),
        "timeout": Parameter(
            name="timeout",
            type=ParameterType.INTEGER,
            description="Timeout in seconds (max 300)",
            required=False,
            default=30
        ),
        "working_dir": Parameter(
            name="working_dir",
            type=ParameterType.STRING,
            description="Working directory for the command",
            required=False,
            default=None
        )
    }
    
    # Banned dangerous commands
    BANNED_PATTERNS = [
        "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf ~/*",
        "mkfs", "mkfs.ext", "mkfs.xfs", "mkfs.btrfs",
        "dd if=/dev/zero", "dd if=/dev/random",
        "> /dev/sda", "> /dev/hda", "> /dev/nvme",
        ":(){ :|:& };:", "fork bomb", "while true",
        "shutdown", "reboot", "halt", "poweroff",
        "init 0", "init 6", "telinit 0",
    ]
    
    def _is_safe(self, command: str) -> tuple[bool, Optional[str]]:
        """Check if command is safe to execute"""
        cmd_lower = command.lower().strip()
        
        for banned in self.BANNED_PATTERNS:
            if banned.lower() in cmd_lower:
                return False, f"Command contains banned pattern: {banned}"
        
        return True, None
    
    def confirm(self, params: dict) -> bool:
        """Enhanced confirmation for bash commands"""
        command = params.get("command", "")
        timeout = params.get("timeout", 30)
        
        print(f"\n⚠️  BASH COMMAND (timeout: {timeout}s)")
        print("─" * 50)
        print(f"$ {command}")
        print("─" * 50)
        
        response = input("Execute? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, command: str, timeout: int = 30, working_dir: Optional[str] = None) -> ToolResult:
        # Security check
        is_safe, error_msg = self._is_safe(command)
        if not is_safe:
            return ToolResult.error_result(f"Security blocked: {error_msg}")
        
        # Cap timeout
        max_timeout = self.context.get_config("bash.timeout", 60)
        timeout = min(timeout, max_timeout, 300)
        
        # Determine working directory
        cwd = working_dir or self.context.working_dir
        
        try:
            with time_limit(timeout):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    timeout=timeout
                )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]:\n{result.stderr}"
            
            return ToolResult.success_result(
                output=output or "(no output)",
                exit_code=result.returncode,
                command=command
            )
            
        except TimeoutError:
            return ToolResult.error_result(f"Command timed out after {timeout} seconds")
        except subprocess.TimeoutExpired:
            return ToolResult.error_result(f"Command timed out after {timeout} seconds")
        except Exception as e:
            return ToolResult.error_result(f"Error executing command: {str(e)}")


@register_tool
class PythonTool(Tool):
    """Execute Python code in a restricted environment"""
    
    name = "python"
    description = "Execute Python code"
    category = "system"
    
    parameters = {
        "code": Parameter(
            name="code",
            type=ParameterType.STRING,
            description="Python code to execute",
            required=True
        ),
        "timeout": Parameter(
            name="timeout",
            type=ParameterType.INTEGER,
            description="Timeout in seconds",
            required=False,
            default=30
        )
    }
    
    # Restricted builtins
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'json', 're', 'string',
        'collections', 'itertools', 'functools', 'statistics',
        'decimal', 'fractions', 'typing', 'pathlib', 'hashlib',
        'base64', 'urllib.parse', 'time', 'os.path'
    }
    
    def _execute(self, code: str, timeout: int = 30) -> ToolResult:
        timeout = min(timeout, 60)
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
                'bin': bin, 'bool': bool, 'bytearray': bytearray,
                'bytes': bytes, 'callable': callable, 'chr': chr,
                'classmethod': classmethod, 'complex': complex,
                'dict': dict, 'dir': dir, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'hasattr': hasattr,
                'hash': hash, 'hex': hex, 'id': id, 'int': int,
                'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map,
                'max': max, 'min': min, 'next': next, 'object': object,
                'oct': oct, 'ord': ord, 'pow': pow, 'print': print,
                'property': property, 'range': range, 'repr': repr,
                'reversed': reversed, 'round': round, 'set': set,
                'setattr': setattr, 'slice': slice, 'sorted': sorted,
                'staticmethod': staticmethod, 'str': str, 'sum': sum,
                'super': super, 'tuple': tuple, 'type': type, 'zip': zip,
            }
        }
        
        # Add allowed modules
        import importlib
        for mod_name in self.ALLOWED_MODULES:
            try:
                restricted_globals[mod_name] = importlib.import_module(mod_name)
            except ImportError:
                pass
        
        # Capture output
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            with time_limit(timeout):
                exec(code, restricted_globals)
            
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            return ToolResult.success_result(
                output=output or "(no output)",
                executed=True
            )
            
        except TimeoutError:
            sys.stdout = old_stdout
            return ToolResult.error_result(f"Code execution timed out after {timeout} seconds")
        except Exception as e:
            sys.stdout = old_stdout
            return ToolResult.error_result(f"Error: {type(e).__name__}: {str(e)}")


@register_tool
class ReadTool(Tool):
    """Quick read file without line numbers (for agent use)"""
    
    name = "read"
    description = "Read a file's raw contents"
    category = "system"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to file",
            required=True
        )
    }
    
    def _execute(self, path: str) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return ToolResult.error_result(f"File not found: {path}")
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return ToolResult.success_result(
                output=content,
                size=len(content),
                lines=len(content.splitlines())
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error reading file: {str(e)}")
