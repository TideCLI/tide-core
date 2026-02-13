"""
System Tools
"""

import os
import subprocess
import shutil
from typing import Dict, Any, Optional
from .base import Tool, ToolResult


class BashTool(Tool):
    """Execute bash commands"""
    
    name = "bash"
    description = "Execute shell commands safely"
    category = "system"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command to execute"
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds"
            },
            "working_dir": {
                "type": "string",
                "description": "Working directory"
            }
        },
        "required": ["command"]
    }
    requires_confirmation = True
    
    BANNED_COMMANDS = [
        "rm -rf /",
        "dd if=",
        ":(){:|:&};:",
        "mkfs",
        "fdisk",
        "> /dev/sda",
        "chmod 777 /",
        "chown -R",
        "wget | sh",
        "curl | sh",
        "curl -sL |",
    ]
    
    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        command = kwargs.get("command", "")
        
        # Check for banned commands
        for banned in self.BANNED_COMMANDS:
            if banned in command:
                return False, f"Command contains banned pattern: {banned}"
                
        # Check for dangerous patterns
        dangerous = ["sudo", "su -", "chmod 777", "> /dev/", "kill -9 1"]
        if any(d in command for d in dangerous):
            return True, "Warning: Potentially dangerous command"
            
        return True, None
        
    def execute(self, **kwargs) -> ToolResult:
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", 30)
        working_dir = kwargs.get("working_dir", self.working_dir)
        
        try:
            # Expand environment variables
            command = os.path.expandvars(command)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )
            
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
                
            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    output=output,
                    error=f"Exit code: {result.returncode}"
                )
                
            return ToolResult(
                success=True,
                output=output or "(command completed successfully)",
                metadata={"exit_code": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class PythonTool(Tool):
    """Execute Python code"""
    
    name = "python"
    description = "Execute Python code safely"
    category = "system"
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds"
            }
        },
        "required": ["code"]
    }
    requires_confirmation = True
    
    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        code = kwargs.get("code", "")
        
        # Check for dangerous imports
        dangerous = ["import os", "import sys", "import subprocess", "import socket"]
        if any(d in code for d in dangerous):
            return False, "Cannot use system modules"
            
        return True, None
        
    def execute(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", 10)
        
        # Create restricted namespace
        namespace = {
            "print": print,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
        }
        
        try:
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer):
                exec(code, namespace)
                
            output = output_buffer.getvalue()
            
            return ToolResult(
                success=True,
                output=output or "(code executed successfully)"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class SystemInfoTool(Tool):
    """Get system information"""
    
    name = "system_info"
    description = "Display system information"
    category = "system"
    parameters = {
        "type": "object",
        "properties": {}
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        import platform
        import os
        
        info = {
            "OS": platform.system(),
            "OS Version": platform.release(),
            "Architecture": platform.machine(),
            "Python Version": platform.python_version(),
            "Current User": os.environ.get("USER", "unknown"),
            "Home Directory": os.path.expanduser("~"),
            "Current Directory": os.getcwd(),
        }
        
        output = "\n".join(f"{k}: {v}" for k, v in info.items())
        
        return ToolResult(
            success=True,
            output=output
        )


class EnvTool(Tool):
    """Get environment variables"""
    
    name = "env"
    description = "List environment variables"
    category = "system"
    parameters = {
        "type": "object",
        "properties": {
            "filter": {
                "type": "string",
                "description": "Filter by prefix"
            }
        }
    }
    requires_confirmation = False
    
    def execute(self, **kwargs) -> ToolResult:
        filter_prefix = kwargs.get("filter", "")
        
        env_vars = []
        for key, value in sorted(os.environ.items()):
            if not filter_prefix or key.startswith(filter_prefix):
                env_vars.append(f"{key}={value}")
                
        output = "\n".join(env_vars) if env_vars else "No matching environment variables"
        
        return ToolResult(
            success=True,
            output=output,
            metadata={"count": len(env_vars)}
        )
