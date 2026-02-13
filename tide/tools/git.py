"""
Git tools for version control operations
"""
import subprocess
from pathlib import Path
from typing import Optional, List

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


def run_git_command(args: List[str], cwd: Optional[str] = None) -> tuple:
    """Run a git command and return (success, stdout, stderr)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except Exception as e:
        return (False, "", str(e))


@register_tool
class GitStatusTool(Tool):
    """Check git repository status"""
    
    name = "git_status"
    description = "Show git repository status (modified, staged, untracked files)"
    category = "git"
    
    parameters = {
        "short": Parameter(
            name="short",
            type=ParameterType.BOOLEAN,
            description="Show short format",
            required=False,
            default=False
        )
    }
    
    def _execute(self, short: bool = False) -> ToolResult:
        args = ["status"]
        if short:
            args.append("-s")
        else:
            args.append("-sb")  # Short branch info + full status
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        return ToolResult.success_result(
            output=f"📊 Git Status:\n{stdout}" if stdout else "📊 Working tree clean",
            status=stdout
        )


@register_tool
class GitDiffTool(Tool):
    """Show git diff for changes"""
    
    name = "git_diff"
    description = "Show changes between commits, working tree, etc."
    category = "git"
    
    parameters = {
        "file": Parameter(
            name="file",
            type=ParameterType.STRING,
            description="Specific file to diff (optional)",
            required=False,
            default=None
        ),
        "staged": Parameter(
            name="staged",
            type=ParameterType.BOOLEAN,
            description="Show staged changes",
            required=False,
            default=False
        ),
        "cached": Parameter(
            name="cached",
            type=ParameterType.BOOLEAN,
            description="Alias for staged",
            required=False,
            default=False
        )
    }
    
    def _execute(self, file: Optional[str] = None, 
                 staged: bool = False, cached: bool = False) -> ToolResult:
        args = ["diff"]
        
        if staged or cached:
            args.append("--cached")
        
        if file:
            args.append(file)
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        if not stdout:
            return ToolResult.success_result(
                output="📋 No changes to show",
                has_changes=False
            )
        
        # Limit output length
        output = stdout
        if len(output) > 3000:
            output = output[:3000] + "\n\n... (diff truncated)"
        
        return ToolResult.success_result(
            output=f"📋 Git Diff:\n```diff\n{output}\n```",
            diff=output,
            has_changes=True
        )


@register_tool
class GitLogTool(Tool):
    """Show git commit history"""
    
    name = "git_log"
    description = "Show recent commit history"
    category = "git"
    
    parameters = {
        "n": Parameter(
            name="n",
            type=ParameterType.INTEGER,
            description="Number of commits to show",
            required=False,
            default=10
        ),
        "oneline": Parameter(
            name="oneline",
            type=ParameterType.BOOLEAN,
            description="Show one line per commit",
            required=False,
            default=True
        ),
        "file": Parameter(
            name="file",
            type=ParameterType.STRING,
            description="Show history for specific file",
            required=False,
            default=None
        )
    }
    
    def _execute(self, n: int = 10, oneline: bool = True, 
                 file: Optional[str] = None) -> ToolResult:
        args = ["log"]
        
        if oneline:
            args.append("--oneline")
        
        args.extend(["-n", str(n)])
        
        if file:
            args.append(file)
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        return ToolResult.success_result(
            output=f"📜 Git Log (last {n} commits):\n{stdout}",
            log=stdout
        )


@register_tool
class GitAddTool(Tool):
    """Stage files for commit"""
    
    name = "git_add"
    description = "Stage files for commit"
    category = "git"
    require_confirmation = True
    
    parameters = {
        "files": Parameter(
            name="files",
            type=ParameterType.STRING,
            description="Files to stage (use '.' for all, or specific file path)",
            required=True
        )
    }
    
    def confirm(self, params: dict) -> bool:
        files = params.get("files", "")
        if files == ".":
            print("\n⚠️  Stage ALL modified files?")
        else:
            print(f"\n⚠️  Stage file(s): {files}?")
        response = input("Confirm? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, files: str) -> ToolResult:
        args = ["add", files]
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        # Show what was staged
        success2, status_out, _ = run_git_command(["status", "-s"])
        
        return ToolResult.success_result(
            output=f"✅ Staged: {files}\n\nCurrent status:\n{status_out}" if success2 
                   else f"✅ Staged: {files}",
            files=files
        )


@register_tool
class GitCommitTool(Tool):
    """Commit staged changes"""
    
    name = "git_commit"
    description = "Commit staged changes with a message"
    category = "git"
    require_confirmation = True
    
    parameters = {
        "message": Parameter(
            name="message",
            type=ParameterType.STRING,
            description="Commit message",
            required=True
        ),
        "add_all": Parameter(
            name="add_all",
            type=ParameterType.BOOLEAN,
            description="Stage all modified files before commit",
            required=False,
            default=False
        )
    }
    
    def confirm(self, params: dict) -> bool:
        message = params.get("message", "")
        add_all = params.get("add_all", False)
        
        print(f"\n📝 Commit Message: {message}")
        if add_all:
            print("   (Will stage all modified files first)")
        
        response = input("\nCommit? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, message: str, add_all: bool = False) -> ToolResult:
        args = ["commit", "-m", message]
        
        if add_all:
            # Stage all first
            run_git_command(["add", "."])
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        return ToolResult.success_result(
            output=f"✅ Committed: {message}\n\n{stdout}",
            message=message
        )


@register_tool
class GitBranchTool(Tool):
    """List or manage branches"""
    
    name = "git_branch"
    description = "List git branches"
    category = "git"
    
    parameters = {
        "all": Parameter(
            name="all",
            type=ParameterType.BOOLEAN,
            description="Show all branches (local and remote)",
            required=False,
            default=False
        )
    }
    
    def _execute(self, all: bool = False) -> ToolResult:
        args = ["branch"]
        
        if all:
            args.append("-a")
        
        success, stdout, stderr = run_git_command(args)
        
        if not success:
            return ToolResult.error_result(f"Git error: {stderr}")
        
        return ToolResult.success_result(
            output=f"🌿 Branches:\n{stdout}",
            branches=stdout
        )
