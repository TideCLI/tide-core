"""
Filesystem tools - view, edit, write, ls, glob
Inspired by crush's file operations
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from .base import Tool, ToolContext, ToolResult, Parameter, ParameterType
from .registry import register_tool


@register_tool
class ViewTool(Tool):
    """Read file contents with line numbers and syntax awareness"""
    
    name = "view"
    description = "Read a file's contents with line numbers"
    category = "filesystem"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to the file to view",
            required=True
        ),
        "offset": Parameter(
            name="offset",
            type=ParameterType.INTEGER,
            description="Line number to start viewing from (1-indexed)",
            required=False,
            default=1
        ),
        "limit": Parameter(
            name="limit",
            type=ParameterType.INTEGER,
            description="Maximum number of lines to read",
            required=False,
            default=100
        )
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
    MAX_LINES = 500
    
    def _execute(self, path: str, offset: int = 1, limit: int = 100) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return ToolResult.error_result(f"File not found: {path}")
            
            if not file_path.is_file():
                return ToolResult.error_result(f"Not a file: {path}")
            
            # Check file size
            size = file_path.stat().st_size
            if size > self.MAX_FILE_SIZE:
                return ToolResult.error_result(
                    f"File too large ({size / 1024 / 1024:.1f}MB > 5MB limit)"
                )
            
            # Cap limit
            limit = min(limit, self.MAX_LINES)
            
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Apply offset and limit
            start_idx = max(0, offset - 1)
            end_idx = min(start_idx + limit, total_lines)
            
            # Format with line numbers
            numbered_lines = []
            for i in range(start_idx, end_idx):
                line_num = i + 1
                line_content = lines[i].rstrip('\n\r')
                numbered_lines.append(f"{line_num:4d} | {line_content}")
            
            output = '\n'.join(numbered_lines)
            
            # Add header
            header = f"📄 {file_path}\n"
            header += f"   Lines {start_idx + 1}-{end_idx} of {total_lines}"
            if size > 1024:
                header += f" ({size / 1024:.1f}KB)"
            header += "\n"
            header += "─" * 60 + "\n"
            
            return ToolResult.success_result(
                output=header + output,
                file=str(file_path),
                total_lines=total_lines,
                shown_lines=end_idx - start_idx
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error reading file: {str(e)}")


@register_tool
class LsTool(Tool):
    """List directory contents with tree view"""
    
    name = "ls"
    description = "List directory contents (tree view)"
    category = "filesystem"
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Directory path to list",
            required=False,
            default="."
        ),
        "depth": Parameter(
            name="depth",
            type=ParameterType.INTEGER,
            description="Maximum recursion depth",
            required=False,
            default=2
        )
    }
    
    def _execute(self, path: str = ".", depth: int = 2) -> ToolResult:
        try:
            dir_path = Path(path).expanduser().resolve()
            
            if not dir_path.exists():
                return ToolResult.error_result(f"Directory not found: {path}")
            
            if not dir_path.is_dir():
                return ToolResult.error_result(f"Not a directory: {path}")
            
            # Get config limits
            max_depth = self.context.get_config("ls.max_depth", 5)
            max_files = self.context.get_config("ls.max_files", 1000)
            ignore_patterns = self.context.get_config(
                "ls.ignore", 
                [".git", "node_modules", "__pycache__"]
            )
            
            # Cap depth
            depth = min(depth, max_depth)
            
            lines = [f"📁 {dir_path}", ""]
            file_count = [0]  # Use list for mutable reference
            
            def should_ignore(name: str) -> bool:
                return any(pattern in name for pattern in ignore_patterns)
            
            def build_tree(current: Path, prefix: str = "", current_depth: int = 0) -> List[str]:
                if current_depth > depth or file_count[0] >= max_files:
                    return []
                
                result = []
                try:
                    items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                except PermissionError:
                    return [prefix + "⚠️  Permission denied"]
                
                # Filter ignored items
                items = [item for item in items if not should_ignore(item.name)]
                
                for i, item in enumerate(items):
                    file_count[0] += 1
                    if file_count[0] > max_files:
                        result.append(prefix + "... (max files reached)")
                        break
                    
                    is_last = (i == len(items) - 1)
                    branch = "└── " if is_last else "├── "
                    
                    if item.is_dir():
                        result.append(f"{prefix}{branch}📁 {item.name}/")
                        if current_depth < depth:
                            extension = "    " if is_last else "│   "
                            result.extend(build_tree(item, prefix + extension, current_depth + 1))
                    else:
                        icon = "📄"
                        if item.suffix in ['.py', '.js', '.go', '.rs']:
                            icon = "🐍" if item.suffix == '.py' else "📜"
                        result.append(f"{prefix}{branch}{icon} {item.name}")
                
                return result
            
            lines.extend(build_tree(dir_path))
            lines.append("")
            lines.append(f"Total items shown: {file_count[0]}")
            
            return ToolResult.success_result(
                output='\n'.join(lines),
                directory=str(dir_path),
                file_count=file_count[0]
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error listing directory: {str(e)}")


@register_tool
class EditTool(Tool):
    """Edit a file with diff preview"""
    
    name = "edit"
    description = "Edit a file by replacing text"
    category = "filesystem"
    require_confirmation = True
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to the file to edit",
            required=True
        ),
        "oldText": Parameter(
            name="oldText",
            type=ParameterType.STRING,
            description="Text to find and replace",
            required=True
        ),
        "newText": Parameter(
            name="newText",
            type=ParameterType.STRING,
            description="Replacement text",
            required=True
        )
    }
    
    def confirm(self, params: dict) -> bool:
        """Show diff before confirming"""
        path = params.get("path", "")
        old_text = params.get("oldText", "")
        new_text = params.get("newText", "")
        
        print(f"\n📝 Edit: {path}")
        print("─" * 50)
        print("─ REMOVED ─")
        print(old_text[:500] + "..." if len(old_text) > 500 else old_text)
        print("\n─ ADDED ─")
        print(new_text[:500] + "..." if len(new_text) > 500 else new_text)
        print("─" * 50)
        
        response = input("\nApply this edit? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, path: str, oldText: str, newText: str) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return ToolResult.error_result(f"File not found: {path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if oldText not in content:
                return ToolResult.error_result("Old text not found in file")
            
            # Create backup if configured
            if self.context.get_config("edit.create_backup", True):
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)
            
            # Perform edit
            new_content = content.replace(oldText, newText, 1)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return ToolResult.success_result(
                output=f"✅ Edited {file_path}",
                file=str(file_path),
                replaced=True
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error editing file: {str(e)}")


@register_tool
class WriteTool(Tool):
    """Write content to a new file"""
    
    name = "write"
    description = "Create a new file with the given content"
    category = "filesystem"
    require_confirmation = True
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path for the new file",
            required=True
        ),
        "content": Parameter(
            name="content",
            type=ParameterType.STRING,
            description="Content to write to the file",
            required=True
        )
    }
    
    def confirm(self, params: dict) -> bool:
        path = params.get("path", "")
        content = params.get("content", "")[:200]
        
        print(f"\n📝 Write to: {path}")
        print(f"Content preview:\n{content}...")
        
        response = input("\nCreate this file? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, path: str, content: str) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            
            if file_path.exists():
                return ToolResult.error_result(f"File already exists: {path}")
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult.success_result(
                output=f"✅ Created {file_path}",
                file=str(file_path),
                bytes_written=len(content.encode('utf-8'))
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error writing file: {str(e)}")


@register_tool
class GlobTool(Tool):
    """Find files matching a glob pattern"""
    
    name = "glob"
    description = "Find files by pattern (e.g., '*.py', 'src/**/*.js')"
    category = "filesystem"
    
    parameters = {
        "pattern": Parameter(
            name="pattern",
            type=ParameterType.STRING,
            description="Glob pattern to match",
            required=True
        ),
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Directory to search in",
            required=False,
            default="."
        )
    }
    
    def _execute(self, pattern: str, path: str = ".") -> ToolResult:
        try:
            import fnmatch
            
            search_path = Path(path).expanduser().resolve()
            matches = []
            
            # Handle ** patterns
            if "**" in pattern:
                parts = pattern.split("**")
                if len(parts) == 2 and parts[0] in ('', '/'):
                    # Pattern like '**/*.py'
                    suffix = parts[1].lstrip('/')
                    for item in search_path.rglob(suffix or "*"):
                        if item.is_file():
                            matches.append(str(item.relative_to(search_path)))
            else:
                # Simple glob
                for item in search_path.iterdir():
                    if fnmatch.fnmatch(item.name, pattern):
                        matches.append(str(item.relative_to(search_path)))
            
            # Limit results
            matches = sorted(matches)[:100]
            
            output = f"🔍 Pattern: {pattern}\n"
            output += f"📁 Directory: {search_path}\n"
            output += f"📄 Matches: {len(matches)}\n"
            output += "─" * 40 + "\n"
            output += '\n'.join(matches) if matches else "(no matches)"
            
            return ToolResult.success_result(
                output=output,
                pattern=pattern,
                matches=matches,
                count=len(matches)
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Error searching: {str(e)}")
