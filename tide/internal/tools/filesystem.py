"""
Filesystem tools - File operations
"""

from pathlib import Path
from typing import List, Dict
from internal.tools.base import Tool, ToolResult


class FileSystemTools:
    """Filesystem tool collection"""
    
    def get_tools(self) -> List[Tool]:
        """Get all filesystem tools"""
        return [
            Tool(
                name="read",
                description="Read file contents with optional offset and limit",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "offset": {"type": "integer"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["path"]
                },
                func=self.read,
                category="filesystem"
            ),
            Tool(
                name="write",
                description="Write content to a file",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["path", "content"]
                },
                func=self.write,
                category="filesystem"
            ),
            Tool(
                name="edit",
                description="Edit file by replacing text",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old_text": {"type": "string"},
                        "new_text": {"type": "string"}
                    },
                    "required": ["path", "old_text", "new_text"]
                },
                func=self.edit,
                category="filesystem"
            ),
            Tool(
                name="ls",
                description="List directory contents",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "recursive": {"type": "boolean"}
                    },
                    "required": ["path"]
                },
                func=self.ls,
                category="filesystem"
            ),
            Tool(
                name="glob",
                description="Find files matching pattern",
                parameters={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"}
                    },
                    "required": ["pattern"]
                },
                func=self.glob,
                category="filesystem"
            ),
            Tool(
                name="view",
                description="View file or directory tree",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "depth": {"type": "integer"}
                    },
                    "required": ["path"]
                },
                func=self.view,
                category="filesystem"
            ),
        ]
    
    def read(self, params: Dict) -> ToolResult:
        """Read file"""
        try:
            path = Path(params["path"]).expanduser()
            if not path.exists():
                return ToolResult(False, "", f"File not found: {params['path']}")
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            offset = params.get("offset", 1)
            limit = params.get("limit", 100)
            start = max(0, offset - 1)
            end = min(len(lines), start + limit)
            
            content = ''.join(lines[start:end])
            if len(lines) > limit:
                content += f"\n... ({len(lines) - limit} more lines)"
            
            return ToolResult(True, content)
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def write(self, params: Dict) -> ToolResult:
        """Write file"""
        try:
            path = Path(params["path"]).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(params["content"])
            
            return ToolResult(True, f"✓ Wrote {len(params['content'])} chars to {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def edit(self, params: Dict) -> ToolResult:
        """Edit file"""
        try:
            path = Path(params["path"]).expanduser()
            if not path.exists():
                return ToolResult(False, "", f"File not found: {params['path']}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            old_text = params.get("old_text", "")
            new_text = params.get("new_text", "")
            
            if old_text not in content:
                return ToolResult(False, "", "Text not found in file")
            
            new_content = content.replace(old_text, new_text, 1)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return ToolResult(True, f"✓ Edited {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def ls(self, params: Dict) -> ToolResult:
        """List directory"""
        try:
            path = Path(params["path"]).expanduser()
            if not path.exists():
                return ToolResult(False, "", f"Directory not found: {params['path']}")
            
            recursive = params.get("recursive", False)
            
            if recursive:
                items = list(path.rglob("*"))
            else:
                items = list(path.iterdir())
            
            results = []
            for item in sorted(items)[:50]:
                icon = "📁" if item.is_dir() else "📄"
                size = item.stat().st_size if item.is_file() else "-"
                results.append(f"{icon} {item.name} {size}")
            
            return ToolResult(True, "\n".join(results))
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def glob(self, params: Dict) -> ToolResult:
        """Glob files"""
        try:
            path = Path(params.get("path", ".")).expanduser()
            pattern = params["pattern"]
            
            matches = list(path.glob(pattern))
            return ToolResult(True, "\n".join([str(m) for m in matches[:50]]))
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def view(self, params: Dict) -> ToolResult:
        """View directory tree"""
        try:
            path = Path(params["path"]).expanduser()
            depth = params.get("depth", 2)
            
            if path.is_file():
                return self.read({"path": str(path)})
            
            lines = [f"📂 {path.name}"]
            
            def add_tree(p: Path, prefix: str = "", current_depth: int = 0):
                if current_depth >= depth:
                    return
                
                try:
                    items = sorted(p.iterdir())[:20]
                    for i, item in enumerate(items):
                        is_last = i == len(items) - 1
                        connector = "└── " if is_last else "├── "
                        lines.append(f"{prefix}{connector}{item.name}")
                        
                        if item.is_dir():
                            ext = "    " if is_last else "│   "
                            add_tree(item, prefix + ext, current_depth + 1)
                except:
                    pass
            
            add_tree(path)
            return ToolResult(True, "\n".join(lines))
        except Exception as e:
            return ToolResult(False, "", str(e))
