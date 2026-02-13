"""
Linting and code quality tools
"""
import subprocess
import json
from pathlib import Path
from typing import Optional, List

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


@register_tool
class LintTool(Tool):
    """Run linters on code files"""
    
    name = "lint"
    description = "Run linter (ruff, pylint, eslint) on code files"
    category = "code"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="File or directory to lint",
            required=True
        ),
        "linter": Parameter(
            name="linter",
            type=ParameterType.STRING,
            description="Linter to use (auto, ruff, pylint, flake8, eslint)",
            required=False,
            default="auto"
        ),
        "fix": Parameter(
            name="fix",
            type=ParameterType.BOOLEAN,
            description="Auto-fix issues (if supported)",
            required=False,
            default=False
        )
    }
    
    def _detect_linter(self, path: str) -> str:
        """Auto-detect appropriate linter"""
        p = Path(path)
        suffix = p.suffix if p.is_file() else ""
        
        # Check for JS/TS
        if suffix in ['.js', '.jsx', '.ts', '.tsx']:
            return "eslint"
        
        # Python - prefer ruff if available
        if suffix in ['.py', '']:
            import shutil
            if shutil.which("ruff"):
                return "ruff"
            if shutil.which("pylint"):
                return "pylint"
            if shutil.which("flake8"):
                return "flake8"
        
        return "ruff"  # Default
    
    def _execute(self, path: str, linter: str = "auto", fix: bool = False) -> ToolResult:
        try:
            target = Path(path).expanduser().resolve()
            
            if not target.exists():
                return ToolResult.error_result(f"Path not found: {path}")
            
            # Auto-detect if needed
            if linter == "auto":
                linter = self._detect_linter(path)
            
            # Build command
            cmd = [linter]
            
            if linter == "ruff":
                cmd.extend(["check"])
                if fix:
                    cmd.append("--fix")
                cmd.append(str(target))
            elif linter == "pylint":
                cmd.extend(["--output-format", "text", str(target)])
            elif linter == "flake8":
                cmd.append(str(target))
            elif linter == "eslint":
                if fix:
                    cmd.append("--fix")
                cmd.append(str(target))
            else:
                return ToolResult.error_result(f"Unknown linter: {linter}")
            
            # Run linter
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Ruff returns 1 if issues found (not error)
            has_issues = result.returncode != 0
            
            output = result.stdout or result.stderr
            
            if not output.strip():
                return ToolResult.success_result(
                    output=f"✅ {linter}: No issues found in {path}",
                    linter=linter,
                    issues=0
                )
            
            # Count issues (rough estimate)
            issue_count = len([l for l in output.split('\n') if l.strip()])
            
            # Truncate if too long
            display_output = output
            if len(display_output) > 2000:
                display_output = display_output[:2000] + "\n\n... (output truncated)"
            
            status = "⚠️" if has_issues else "✅"
            
            return ToolResult.success_result(
                output=f"{status} {linter} results for {path}:\n{display_output}",
                linter=linter,
                has_issues=has_issues,
                issues=issue_count,
                full_output=output
            )
            
        except FileNotFoundError:
            return ToolResult.error_result(
                f"Linter '{linter}' not found. Install it:\n"
                f"  pip install ruff  # Recommended\n"
                f"  pip install pylint\n"
                f"  npm install -g eslint"
            )
        except subprocess.TimeoutExpired:
            return ToolResult.error_result("Linting timed out")
        except Exception as e:
            return ToolResult.error_result(f"Linting failed: {str(e)}")


@register_tool
class FormatTool(Tool):
    """Auto-format code"""
    
    name = "format"
    description = "Auto-format code using formatters (black, ruff, prettier)"
    category = "code"
    require_confirmation = True
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="File or directory to format",
            required=True
        ),
        "formatter": Parameter(
            name="formatter",
            type=ParameterType.STRING,
            description="Formatter to use (auto, black, ruff, prettier)",
            required=False,
            default="auto"
        )
    }
    
    def confirm(self, params: dict) -> bool:
        path = params.get("path", "")
        print(f"\n⚠️  Format code in: {path}?")
        response = input("Confirm? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, path: str, formatter: str = "auto") -> ToolResult:
        try:
            target = Path(path).expanduser().resolve()
            
            if not target.exists():
                return ToolResult.error_result(f"Path not found: {path}")
            
            # Auto-detect
            if formatter == "auto":
                suffix = target.suffix if target.is_file() else ""
                
                if suffix in ['.js', '.jsx', '.ts', '.tsx', '.json', '.md']:
                    formatter = "prettier"
                else:
                    import shutil
                    if shutil.which("ruff"):
                        formatter = "ruff"
                    elif shutil.which("black"):
                        formatter = "black"
            
            # Build command
            if formatter == "ruff":
                cmd = ["ruff", "format", str(target)]
            elif formatter == "black":
                cmd = ["black", str(target)]
            elif formatter == "prettier":
                cmd = ["prettier", "--write", str(target)]
            else:
                return ToolResult.error_result(f"Unknown formatter: {formatter}")
            
            # Run formatter
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return ToolResult.error_result(
                    f"Formatter error:\n{result.stderr}"
                )
            
            output = result.stdout or f"✅ Formatted with {formatter}"
            
            return ToolResult.success_result(
                output=output,
                formatter=formatter
            )
            
        except FileNotFoundError:
            return ToolResult.error_result(
                f"Formatter '{formatter}' not found. Install it:\n"
                f"  pip install ruff  # Recommended\n"
                f"  pip install black\n"
                f"  npm install -g prettier"
            )
        except Exception as e:
            return ToolResult.error_result(f"Formatting failed: {str(e)}")
