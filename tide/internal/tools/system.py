"""
System tools - Shell execution and system operations
"""

import subprocess
from typing import List, Dict
from internal.tools.base import Tool, ToolResult


class SystemTools:
    """System tool collection"""
    
    def get_tools(self) -> List[Tool]:
        """Get all system tools"""
        return [
            Tool(
                name="bash",
                description="Execute bash command with timeout",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "timeout": {"type": "integer"},
                        "working_dir": {"type": "string"}
                    },
                    "required": ["command"]
                },
                func=self.bash,
                requires_confirmation=True,
                category="system"
            ),
            Tool(
                name="python",
                description="Execute Python code",
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    },
                    "required": ["code"]
                },
                func=self.python,
                category="system"
            ),
        ]
    
    def bash(self, params: Dict) -> ToolResult:
        """Execute bash command"""
        try:
            cmd = params["command"]
            timeout = params.get("timeout", 60)
            cwd = params.get("working_dir")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            
            if result.returncode != 0:
                return ToolResult(False, output, f"Exit code: {result.returncode}")
            
            return ToolResult(True, output or "✓ Command executed")
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", f"Timeout after {timeout}s")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def python(self, params: Dict) -> ToolResult:
        """Execute Python code"""
        try:
            code = params["code"]
            
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                exec(code, {"__name__": "__main__"})
                output = buffer.getvalue()
                return ToolResult(True, output or "✓ Executed")
            finally:
                sys.stdout = old_stdout
        except Exception as e:
            return ToolResult(False, "", f"Python error: {e}")
