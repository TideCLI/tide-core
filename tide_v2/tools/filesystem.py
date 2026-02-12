"""
Optimized Filesystem Tools - Based on crush's ls, view, edit implementations
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import fnmatch
import sys

from .base import Tool, ToolResult, ToolParameter


class ViewTool(Tool):
    """
    View file contents with line numbers and smart reading.
    Based on crush's view.go implementation.
    """
    name = "view"
    description = "Read the contents of a file with line numbers"
    category = "filesystem"
    
    # Constants from crush
    MAX_READ_SIZE = 5 * 1024 * 1024  # 5MB
    DEFAULT_READ_LIMIT = 2000
    MAX_LINE_LENGTH = 2000
    
    parameters = [
        ToolParameter("file_path", "string", "The path to the file to read", True),
        ToolParameter("offset", "integer", "Line number to start from (0-based)", False, 0),
        ToolParameter("limit", "integer", "Number of lines to read (default 2000)", False, 2000)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            offset = params.get("offset", 0)
            limit = params.get("limit", self.DEFAULT_READ_LIMIT)
            
            if not file_path:
                result.error = "file_path is required"
                result.success = False
                return result
            
            # Resolve path
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                # Try to suggest similar files (crush feature)
                suggestions = self._suggest_files(path)
                if suggestions:
                    result.error = f"File not found: {file_path}\n\nDid you mean:\n" + "\n".join(suggestions)
                else:
                    result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            if path.is_dir():
                result.error = f"Path is a directory, not a file: {file_path}"
                result.success = False
                return result
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.MAX_READ_SIZE:
                result.error = f"File too large ({file_size} bytes). Maximum: {self.MAX_READ_SIZE} bytes"
                result.success = False
                return result
            
            # Read file with offset and limit
            content, total_lines = self._read_file(path, offset, limit)
            
            # Add line numbers
            numbered_content = self._add_line_numbers(content, offset + 1)
            
            # Build output
            output = f"<file path='{file_path}'>\n"
            output += numbered_content
            
            # Add truncation note if needed
            if offset + len(content.split('\n')) < total_lines:
                last_line = offset + len(content.split('\n'))
                output += f"\n\n(File has more lines. Use offset={last_line} to continue)"
            
            output += "\n</file>"
            
            result.output = output
            result.metadata = {
                "file_path": str(path),
                "total_lines": total_lines,
                "lines_read": len(content.split('\n')),
                "file_size": file_size
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _suggest_files(self, path: Path) -> List[str]:
        """Suggest similar files when file not found"""
        suggestions = []
        try:
            dir_path = path.parent if path.parent.exists() else Path(self.working_dir)
            target_name = path.name.lower()
            
            for entry in dir_path.iterdir():
                entry_name = entry.name.lower()
                # Check if names are similar
                if (target_name in entry_name or entry_name in target_name or
                    self._levenshtein(target_name, entry_name) <= 3):
                    suggestions.append(str(entry.relative_to(self.working_dir)))
                    if len(suggestions) >= 3:
                        break
        except:
            pass
        return suggestions
    
    def _levenshtein(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _read_file(self, path: Path, offset: int, limit: int) -> tuple:
        """Read file with offset and limit, returns (content, total_lines)"""
        lines = []
        total_lines = 0
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            # Skip to offset
            for _ in range(offset):
                line = f.readline()
                if not line:
                    break
                total_lines += 1
            
            # Read limit lines
            for _ in range(limit):
                line = f.readline()
                if not line:
                    break
                # Truncate long lines
                if len(line) > self.MAX_LINE_LENGTH:
                    line = line[:self.MAX_LINE_LENGTH] + "...\n"
                lines.append(line.rstrip('\n'))
                total_lines += 1
            
            # Count remaining lines
            while f.readline():
                total_lines += 1
        
        return '\n'.join(lines), total_lines
    
    def _add_line_numbers(self, content: str, start_line: int) -> str:
        """Add line numbers to content"""
        if not content:
            return ""
        
        lines = content.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            line_num = start_line + i
            num_str = str(line_num)
            # Pad to 6 characters like crush
            padded_num = num_str.rjust(6)
            result.append(f"{padded_num}|{line}")
        
        return '\n'.join(result)


class LSTool(Tool):
    """
    List directory contents as a tree.
    Based on crush's ls.go implementation.
    """
    name = "ls"
    description = "List directory contents as a tree structure"
    category = "filesystem"
    
    MAX_FILES = 1000
    DEFAULT_DEPTH = 5
    
    parameters = [
        ToolParameter("path", "string", "Directory path (default: current)", False, "."),
        ToolParameter("depth", "integer", "Maximum depth to traverse", False, 5),
        ToolParameter("ignore", "array", "Glob patterns to ignore", False, [".git", "node_modules", "__pycache__", ".venv"])
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            path = params.get("path", ".")
            depth = params.get("depth", self.DEFAULT_DEPTH)
            ignore_patterns = params.get("ignore", [".git", "node_modules"])
            
            # Resolve path
            search_path = Path(self.working_dir) / path
            search_path = search_path.resolve()
            
            if not search_path.exists():
                result.error = f"Path does not exist: {path}"
                result.success = False
                return result
            
            if not search_path.is_dir():
                result.error = f"Path is not a directory: {path}"
                result.success = False
                return result
            
            # List directory
            files, truncated = self._list_directory(search_path, ignore_patterns, depth)
            
            # Build tree
            tree = self._build_tree(files, search_path)
            output = self._print_tree(tree, search_path)
            
            # Add warning if truncated
            if truncated:
                output = f"[Directory has more than {self.MAX_FILES} files. Showing first {self.MAX_FILES}.]\n\n" + output
            
            result.output = output
            result.metadata = {
                "number_of_files": len(files),
                "truncated": truncated,
                "depth": depth
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _list_directory(self, path: Path, ignore_patterns: List[str], max_depth: int) -> tuple:
        """List directory recursively"""
        files = []
        truncated = False
        
        def should_ignore(name: str) -> bool:
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(name, pattern):
                    return True
            return False
        
        def traverse(current: Path, depth: int):
            nonlocal truncated
            
            if truncated:
                return
            
            if depth > max_depth:
                return
            
            try:
                for entry in sorted(current.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
                    if should_ignore(entry.name):
                        continue
                    
                    if len(files) >= self.MAX_FILES:
                        truncated = True
                        return
                    
                    rel_path = entry.relative_to(path)
                    files.append(str(rel_path))
                    
                    if entry.is_dir():
                        traverse(entry, depth + 1)
            except PermissionError:
                pass
        
        traverse(path, 0)
        return files, truncated
    
    def _build_tree(self, files: List[str], root: Path) -> List[Dict]:
        """Build tree structure from file list"""
        tree = []
        path_map = {}
        
        for file_path in sorted(files):
            parts = Path(file_path).parts
            current_path = ""
            parent_path = ""
            
            for i, part in enumerate(parts):
                if current_path:
                    current_path = str(Path(current_path) / part)
                else:
                    current_path = part
                
                if current_path in path_map:
                    parent_path = current_path
                    continue
                
                is_dir = (i < len(parts) - 1) or not Path(root / file_path).is_file()
                
                node = {
                    "name": part,
                    "path": current_path,
                    "type": "directory" if is_dir else "file",
                    "children": []
                }
                
                path_map[current_path] = node
                
                if parent_path:
                    if parent_path in path_map:
                        path_map[parent_path]["children"].append(node)
                else:
                    tree.append(node)
                
                parent_path = current_path
        
        return tree
    
    def _print_tree(self, tree: List[Dict], root_path: Path) -> str:
        """Print tree as string"""
        lines = []
        root_str = str(root_path)
        if not root_str.endswith('/'):
            root_str += '/'
        lines.append(f"- {root_str}")
        
        for node in tree:
            self._print_node(lines, node, 1)
        
        return '\n'.join(lines)
    
    def _print_node(self, lines: List[str], node: Dict, level: int):
        """Print tree node"""
        indent = "  " * level
        name = node["name"]
        if node["type"] == "directory":
            name += "/"
        lines.append(f"{indent}- {name}")
        
        for child in node.get("children", []):
            self._print_node(lines, child, level + 1)


class EditTool(Tool):
    """
    Edit file contents with diff view.
    Based on crush's edit.go implementation.
    """
    name = "edit"
    description = "Apply edits to a file with automatic diff generation"
    category = "filesystem"
    requires_confirmation = True
    
    parameters = [
        ToolParameter("file_path", "string", "Path to the file to edit", True),
        ToolParameter("old_string", "string", "Text to replace (must match exactly)", True),
        ToolParameter("new_string", "string", "Replacement text", True)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            old_string = params.get("old_string", "")
            new_string = params.get("new_string", "")
            
            if not all([file_path, old_string]):
                result.error = "file_path and old_string are required"
                result.success = False
                return result
            
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_string exists
            if old_string not in content:
                result.error = f"old_string not found in file. File may have changed."
                result.success = False
                return result
            
            # Apply edit
            new_content = content.replace(old_string, new_string, 1)
            
            # Generate diff
            diff = self._generate_diff(file_path, content, new_content)
            
            # Write new content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result.output = f"Successfully edited {file_path}\n\nDiff:\n{diff}"
            result.metadata = {
                "file_path": str(path),
                "replacements": 1,
                "old_length": len(old_string),
                "new_length": len(new_string)
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _generate_diff(self, file_path: str, old_content: str, new_content: str) -> str:
        """Generate unified diff"""
        import difflib
        
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        
        return ''.join(diff)


class WriteTool(Tool):
    """Write content to a new file"""
    name = "write"
    description = "Create a new file with the specified content"
    category = "filesystem"
    requires_confirmation = True
    
    parameters = [
        ToolParameter("file_path", "string", "Path for the new file", True),
        ToolParameter("content", "string", "File content", True)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            content = params.get("content", "")
            
            if not file_path:
                result.error = "file_path is required"
                result.success = False
                return result
            
            path = Path(self.working_dir) / file_path
            
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            if path.exists():
                result.error = f"File already exists: {file_path}. Use edit to modify."
                result.success = False
                return result
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result.output = f"Successfully created {file_path} ({len(content)} characters)"
            result.metadata = {
                "file_path": str(path),
                "size": len(content),
                "lines": content.count('\n') + 1
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result


class GlobTool(Tool):
    """Find files matching a glob pattern"""
    name = "glob"
    description = "Find files matching a glob pattern"
    category = "filesystem"
    
    parameters = [
        ToolParameter("pattern", "string", "Glob pattern (e.g., '*.py', '**/*.js')", True),
        ToolParameter("path", "string", "Directory to search in", False, ".")
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            pattern = params.get("pattern", "")
            path = params.get("path", ".")
            
            if not pattern:
                result.error = "pattern is required"
                result.success = False
                return result
            
            search_path = Path(self.working_dir) / path
            
            # Handle ** patterns
            if "**" in pattern:
                matches = list(search_path.rglob(pattern.replace("**", "").lstrip("/")))
            else:
                matches = list(search_path.glob(pattern))
            
            # Filter to files only and sort
            files = sorted([str(m.relative_to(self.working_dir)) for m in matches if m.is_file()])
            
            if not files:
                result.output = f"No files matching '{pattern}' found in {path}"
            else:
                output = f"Found {len(files)} files matching '{pattern}':\n\n"
                output += '\n'.join(files[:100])  # Limit output
                if len(files) > 100:
                    output += f"\n\n... and {len(files) - 100} more files"
                result.output = output
            
            result.metadata = {"matches": len(files), "pattern": pattern}
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
