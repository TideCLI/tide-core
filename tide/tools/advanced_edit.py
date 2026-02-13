"""
Advanced editing tools - search/replace like Claude Code
"""
from pathlib import Path
from typing import List, Tuple

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


@register_tool
class SearchReplaceTool(Tool):
    """
    Edit file using search/replace blocks.
    More precise than whole file edit - only changes matching text.
    """
    
    name = "search_replace"
    description = "Edit file by searching for text and replacing it (precise editing)"
    category = "filesystem"
    require_confirmation = True
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to file to edit",
            required=True
        ),
        "search": Parameter(
            name="search",
            type=ParameterType.STRING,
            description="Text to search for (exact match)",
            required=True
        ),
        "replace": Parameter(
            name="replace",
            type=ParameterType.STRING,
            description="Replacement text",
            required=True
        ),
        "occurrence": Parameter(
            name="occurrence",
            type=ParameterType.INTEGER,
            description="Which occurrence to replace (1=first, -1=all)",
            required=False,
            default=1
        )
    }
    
    def confirm(self, params: dict) -> bool:
        path = params.get("path", "")
        search = params.get("search", "")[:100]
        replace = params.get("replace", "")[:100]
        
        print(f"\n📝 Search/Replace Edit: {path}")
        print("─" * 50)
        print("SEARCH FOR:")
        print(search)
        print("\nREPLACE WITH:")
        print(replace)
        print("─" * 50)
        
        response = input("\nApply this edit? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, path: str, search: str, replace: str, 
                 occurrence: int = 1) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return ToolResult.error_result(
                    f"File not found: {path}\n\n"
                    f"💡 To CREATE a new file, use the 'write' tool instead:\n"
                    f'   {{"tool": "write", "params": {{"path": "{path}", "content": "your content"}}}}'
                )
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if search text exists
            if search not in content:
                # Try to find similar text
                search_lines = search.strip().split('\n')
                if len(search_lines) > 1:
                    return ToolResult.error_result(
                        f"Search text not found in file.\n"
                        f"Hint: File has {len(content.split(chr(10)))} lines. "
                        f"Use view tool to see exact content."
                    )
                else:
                    return ToolResult.error_result(
                        f"Search text not found: '{search[:50]}...'\n"
                        f"Use view tool to see exact file content."
                    )
            
            # Count occurrences
            count = content.count(search)
            
            # Perform replacement
            if occurrence == -1:
                # Replace all
                new_content = content.replace(search, replace)
                replaced_count = count
            elif occurrence == 1:
                # Replace first
                new_content = content.replace(search, replace, 1)
                replaced_count = 1
            else:
                # Replace specific occurrence
                parts = content.split(search)
                if occurrence > len(parts) - 1:
                    return ToolResult.error_result(
                        f"Occurrence {occurrence} not found. "
                        f"Only {count} occurrence(s) exist."
                    )
                
                # Reconstruct with replacement at specific position
                new_parts = []
                for i, part in enumerate(parts):
                    new_parts.append(part)
                    if i == occurrence - 1 and i < len(parts) - 1:
                        new_parts.append(replace)
                    elif i < len(parts) - 1 and i != occurrence - 1:
                        new_parts.append(search)
                
                new_content = ''.join(new_parts)
                replaced_count = 1
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return ToolResult.success_result(
                output=f"✅ Edited {file_path}\n"
                       f"   Replaced {replaced_count} of {count} occurrence(s)",
                file=str(file_path),
                occurrences_found=count,
                occurrences_replaced=replaced_count
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Edit failed: {str(e)}")


@register_tool
class MultiEditTool(Tool):
    """
    Make multiple edits to a file in one operation.
    """
    
    name = "multi_edit"
    description = "Make multiple search/replace edits to a file at once"
    category = "filesystem"
    require_confirmation = True
    
    parameters = {
        "path": Parameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to file",
            required=True
        ),
        "edits": Parameter(
            name="edits",
            type=ParameterType.STRING,
            description="JSON array of edits: [{\"search\": \"...\", \"replace\": \"...\"}]",
            required=True
        )
    }
    
    def confirm(self, params: dict) -> bool:
        path = params.get("path", "")
        edits_str = params.get("edits", "[]")
        
        try:
            import json
            edits = json.loads(edits_str)
            num_edits = len(edits)
        except:
            num_edits = "?"
        
        print(f"\n📝 Multi-Edit: {path}")
        print(f"   Number of edits: {num_edits}")
        
        response = input("\nApply all edits? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def _execute(self, path: str, edits: str) -> ToolResult:
        try:
            import json
            
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return ToolResult.error_result(f"File not found: {path}")
            
            # Parse edits
            try:
                edit_list = json.loads(edits)
                if not isinstance(edit_list, list):
                    raise ValueError("Edits must be a JSON array")
            except json.JSONDecodeError as e:
                return ToolResult.error_result(f"Invalid JSON in edits: {e}")
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            applied = 0
            failed = []
            
            # Apply each edit
            for i, edit in enumerate(edit_list):
                search = edit.get('search', '')
                replace = edit.get('replace', '')
                
                if not search:
                    failed.append(f"Edit {i+1}: Empty search")
                    continue
                
                if search not in content:
                    failed.append(f"Edit {i+1}: Search text not found")
                    continue
                
                content = content.replace(search, replace, 1)
                applied += 1
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Build result message
            output_lines = [f"✅ Multi-edit completed: {file_path}"]
            output_lines.append(f"   Applied: {applied}/{len(edit_list)} edits")
            
            if failed:
                output_lines.append("\n   Failed:")
                for f in failed:
                    output_lines.append(f"   - {f}")
            
            return ToolResult.success_result(
                output='\n'.join(output_lines),
                file=str(file_path),
                applied=applied,
                total=len(edit_list),
                failed=failed
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Multi-edit failed: {str(e)}")
