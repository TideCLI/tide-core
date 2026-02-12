"""
Optimized System Tools - Based on crush's bash.go implementation
"""

import subprocess
import sys
import shlex
import time
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from .base import Tool, ToolResult, ToolParameter


class BashTool(Tool):
    """
    Execute bash commands with safety features.
    Based on crush's bash.go implementation.
    """
    name = "bash"
    description = "Execute a bash command in the specified working directory"
    category = "system"
    requires_confirmation = True
    
    # Safety limits
    timeout_seconds = 60
    max_output_length = 30000
    
    # Banned commands (from crush)
    BANNED_COMMANDS = [
        # Network/Download
        "curl", "wget", "nc", "netcat", "telnet", "ssh", "scp",
        "http", "fetch", "download",
        # Package managers (destructive)
        "apt", "apt-get", "yum", "dnf", "pacman", "brew",
        "apk", "npm", "pip", "pip3", "gem", "cargo",
        # System administration
        "sudo", "su", "doas", "pkexec",
        # Dangerous
        "rm -rf /", ":(){ :|:& };:", "dd if=/dev/zero",
        "mkfs", "fdisk", "parted",
        # Shell escapes
        "bash -i", "sh -i", "zsh -i",
    ]
    
    parameters = [
        ToolParameter("command", "string", "The bash command to execute", True),
        ToolParameter("working_dir", "string", "Working directory (default: current)", False, "."),
        ToolParameter("description", "string", "Brief description of what the command does", False, ""),
        ToolParameter("timeout", "integer", "Timeout in seconds (max 60)", False, 30)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        start_time = time.time()
        
        try:
            command = params.get("command", "").strip()
            working_dir = params.get("working_dir", ".")
            description = params.get("description", "")
            timeout = min(params.get("timeout", 30), self.timeout_seconds)
            
            if not command:
                result.error = "command is required"
                result.success = False
                return result
            
            # Security check
            security_error = self._check_security(command)
            if security_error:
                result.error = security_error
                result.success = False
                return result
            
            # Resolve working directory
            work_path = Path(self.working_dir) / working_dir
            work_path = work_path.resolve()
            
            # Execute command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(work_path),
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                # Build output
                output_parts = []
                if description:
                    output_parts.append(f"$ # {description}")
                output_parts.append(f"$ {command}")
                
                if stdout:
                    output_parts.append(stdout.rstrip())
                if stderr:
                    output_parts.append(f"[stderr]:\n{stderr.rstrip()}")
                
                output = "\n\n".join(output_parts)
                
                # Truncate if too long
                output = self.truncate_output(output, self.max_output_length)
                
                # Determine success
                success = process.returncode == 0
                
                result.output = output
                result.success = success
                if not success:
                    result.error = f"Command exited with code {process.returncode}"
                
                result.metadata = {
                    "return_code": process.returncode,
                    "working_dir": str(work_path),
                    "duration_ms": (time.time() - start_time) * 1000,
                    "stdout_lines": stdout.count('\n') if stdout else 0,
                    "stderr_lines": stderr.count('\n') if stderr else 0
                }
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                result.error = f"Command timed out after {timeout} seconds"
                result.success = False
                result.metadata = {"timeout": True, "timeout_seconds": timeout}
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _check_security(self, command: str) -> Optional[str]:
        """Check if command is safe to execute"""
        command_lower = command.lower()
        
        # Check banned commands
        for banned in self.BANNED_COMMANDS:
            if banned.lower() in command_lower:
                return f"Command contains banned pattern: {banned}"
        
        # Check for suspicious patterns
        suspicious = [
            "$(", "`",  # Command substitution
            "| bash", "| sh",  # Piping to shell
            "eval(", "exec(",  # Dangerous functions
            "__import__",  # Python import
        ]
        
        for pattern in suspicious:
            if pattern in command:
                return f"Command contains suspicious pattern: {pattern}"
        
        return None


class PythonTool(Tool):
    """Execute Python code safely"""
    name = "python"
    description = "Execute Python code and return the result"
    category = "system"
    requires_confirmation = False
    
    timeout_seconds = 10
    max_output_length = 10000
    
    parameters = [
        ToolParameter("code", "string", "Python code to execute", True)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            code = params.get("code", "")
            
            if not code:
                result.error = "code is required"
                result.success = False
                return result
            
            # Security: Check for dangerous imports
            dangerous = ['os.system', 'subprocess', 'open(', '__import__', 'eval(', 'exec(']
            for d in dangerous:
                if d in code:
                    result.error = f"Code contains dangerous pattern: {d}"
                    result.success = False
                    return result
            
            # Create restricted namespace
            safe_namespace = {
                '__builtins__': {
                    'True': True, 'False': False, 'None': None,
                    'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'len': len, 'range': range, 'enumerate': enumerate,
                    'zip': zip, 'map': map, 'filter': filter,
                    'sum': sum, 'min': min, 'max': max, 'abs': abs,
                    'round': round, 'pow': pow, 'divmod': divmod,
                    'sorted': sorted, 'reversed': reversed,
                    'print': lambda *args, **kwargs: None,  # Disable print
                }
            }
            
            # Execute with timeout
            import signal as sig
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Code execution timed out")
            
            # Set alarm (Unix only)
            if hasattr(sig, 'SIGALRM'):
                sig.signal(sig.SIGALRM, timeout_handler)
                sig.alarm(self.timeout_seconds)
            
            try:
                exec(code, safe_namespace)
                
                # Get result if 'result' variable was set
                output = safe_namespace.get('result', 'Code executed successfully')
                
                result.output = str(output)[:self.max_output_length]
                result.success = True
                
            except TimeoutError as e:
                result.error = f"Code execution timed out after {self.timeout_seconds} seconds"
                result.success = False
            finally:
                if hasattr(sig, 'SIGALRM'):
                    sig.alarm(0)
            
        except Exception as e:
            result.error = f"Error: {str(e)}"
            result.success = False
        finally:
            result.set_finished()
        
        return result
