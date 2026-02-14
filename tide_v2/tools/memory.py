"""
Memory Tools - Undo, session memory, and project indexing
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .base import Tool, ToolResult, ToolParameter


class UndoTool(Tool):
    """Track file changes and provide rollback capability"""
    name = "undo"
    description = "Undo file changes by restoring from automatic snapshots"
    category = "memory"
    requires_confirmation = False
    
    parameters = [
        ToolParameter("action", "string", "Action: list, undo, undo_all, diff, snapshot", True),
        ToolParameter("file", "string", "Specific file to undo or snapshot", False, ""),
        ToolParameter("snapshot_id", "integer", "Specific snapshot ID to restore", False, 0)
    ]
    
    def __init__(self, working_dir: str = "."):
        super().__init__(working_dir)
        self._snapshot_dir = Path(working_dir) / ".tide" / "snapshots"
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._snapshots = []  # List of snapshot records
        self._snapshot_index_file = Path(working_dir) / ".tide" / "snapshot_index.json"
        self._load_index()
    
    def _load_index(self):
        if self._snapshot_index_file.exists():
            try:
                with open(self._snapshot_index_file, 'r') as f:
                    self._snapshots = json.load(f)
            except Exception:
                self._snapshots = []
    
    def _save_index(self):
        self._snapshot_index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._snapshot_index_file, 'w') as f:
            json.dump(self._snapshots, f, indent=2)
    
    def create_snapshot(self, file_path: str, tool_name: str) -> bool:
        """Called externally by ToolRegistry before destructive operations"""
        try:
            full_path = Path(self.working_dir) / file_path
            if not full_path.exists():
                return False
            
            # Read current content
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create snapshot file
            snapshot_id = len(self._snapshots) + 1
            timestamp = int(datetime.now().timestamp())
            safe_name = file_path.replace('/', '_').replace('\\', '_')
            snapshot_file = self._snapshot_dir / f"{snapshot_id:03d}_{tool_name}_{safe_name}_{timestamp}.bak"
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Record snapshot
            self._snapshots.append({
                "id": snapshot_id,
                "file": file_path,
                "snapshot_file": str(snapshot_file),
                "tool": tool_name,
                "timestamp": datetime.now().isoformat(),
                "size": len(content)
            })
            self._save_index()
            
            return True
        except Exception:
            return False
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            action = params.get("action", "").lower()
            
            if action == "list":
                result = self._list_snapshots()
            elif action == "undo":
                result = self._undo(params)
            elif action == "undo_all":
                result = self._undo_all()
            elif action == "diff":
                result = self._show_diff(params)
            elif action == "snapshot":
                file_path = params.get("file", "")
                if not file_path:
                    result.error = "file is required for manual snapshot"
                    result.success = False
                else:
                    if self.create_snapshot(file_path, "manual"):
                        result.output = f"Snapshot created for: {file_path}"
                    else:
                        result.error = f"Failed to create snapshot for: {file_path}"
                        result.success = False
            else:
                result.error = f"Unknown action: {action}"
                result.success = False
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _list_snapshots(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        if not self._snapshots:
            result.output = "No snapshots recorded this session."
            return result
        
        lines = [f"Snapshots ({len(self._snapshots)} total):\n"]
        for s in reversed(self._snapshots):  # Most recent first
            lines.append(f"  #{s['id']} | {s['tool']:12} | {s['file']}")
            lines.append(f"       {s['timestamp']} ({s['size']} chars)")
        
        result.output = '\n'.join(lines)
        result.metadata = {"count": len(self._snapshots)}
        return result
    
    def _undo(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        file_path = params.get("file", "")
        snapshot_id = params.get("snapshot_id", 0)
        
        # Find the right snapshot
        target = None
        if snapshot_id:
            target = next((s for s in self._snapshots if s["id"] == snapshot_id), None)
        elif file_path:
            # Find most recent snapshot for this file
            for s in reversed(self._snapshots):
                if s["file"] == file_path:
                    target = s
                    break
        else:
            # Most recent snapshot overall
            if self._snapshots:
                target = self._snapshots[-1]
        
        if not target:
            result.error = "No matching snapshot found"
            result.success = False
            return result
        
        # Restore from snapshot
        snapshot_path = Path(target["snapshot_file"])
        if not snapshot_path.exists():
            result.error = f"Snapshot file missing: {target['snapshot_file']}"
            result.success = False
            return result
        
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        restore_path = Path(self.working_dir) / target["file"]
        restore_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(restore_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        result.output = f"Restored: {target['file']} (from snapshot #{target['id']}, tool: {target['tool']})"
        result.metadata = {"restored_file": target["file"], "snapshot_id": target["id"]}
        return result
    
    def _undo_all(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        if not self._snapshots:
            result.output = "No snapshots to restore."
            return result
        
        # Group by file — keep only the FIRST snapshot per file (the original state)
        originals = {}
        for s in self._snapshots:
            if s["file"] not in originals:
                originals[s["file"]] = s
        
        restored = []
        failed = []
        
        for file_path, snapshot in originals.items():
            try:
                snapshot_path = Path(snapshot["snapshot_file"])
                if snapshot_path.exists():
                    with open(snapshot_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    restore_path = Path(self.working_dir) / file_path
                    with open(restore_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    restored.append(file_path)
                else:
                    failed.append(file_path)
            except Exception:
                failed.append(file_path)
        
        output = f"Restored {len(restored)} file(s) to original state:\n"
        for f in restored:
            output += f"  Restored: {f}\n"
        if failed:
            output += f"\nFailed to restore {len(failed)} file(s):\n"
            for f in failed:
                output += f"  Failed: {f}\n"
        
        result.output = output
        result.metadata = {"restored": len(restored), "failed": len(failed)}
        return result
    
    def _show_diff(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        file_path = params.get("file", "")
        
        if not file_path:
            result.error = "file is required for diff"
            result.success = False
            return result
        
        # Find most recent snapshot for this file
        target = None
        for s in reversed(self._snapshots):
            if s["file"] == file_path:
                target = s
                break
        
        if not target:
            result.error = f"No snapshot found for: {file_path}"
            result.success = False
            return result
        
        # Read snapshot and current file
        snapshot_path = Path(target["snapshot_file"])
        current_path = Path(self.working_dir) / file_path
        
        if not snapshot_path.exists() or not current_path.exists():
            result.error = "Snapshot or current file not found"
            result.success = False
            return result
        
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        with open(current_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        from difflib import unified_diff
        diff = list(unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"snapshot/{file_path}",
            tofile=f"current/{file_path}"
        ))
        
        if diff:
            result.output = f"Changes since snapshot #{target['id']}:\n\n" + ''.join(diff[:200])
        else:
            result.output = f"No changes since snapshot #{target['id']}"
        
        return result


class SessionMemoryTool(Tool):
    """Persistent memory across sessions"""
    name = "session_memory"
    description = "Save and recall notes, decisions, and context across sessions"
    category = "memory"
    requires_confirmation = False
    
    parameters = [
        ToolParameter("action", "string", "Action: save, recall, list, delete, search", True),
        ToolParameter("content", "string", "Content to save", False, ""),
        ToolParameter("tags", "array", "Tags for categorization", False, []),
        ToolParameter("query", "string", "Search query", False, "")
    ]
    
    def __init__(self, working_dir: str = "."):
        super().__init__(working_dir)
        self._memory_file = Path(working_dir) / ".tide" / "memory.json"
        self._memories = self._load()
    
    def _load(self) -> list:
        if self._memory_file.exists():
            try:
                with open(self._memory_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_to_disk(self):
        self._memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._memory_file, 'w') as f:
            json.dump(self._memories, f, indent=2)
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            action = params.get("action", "").lower()
            
            if action == "save":
                result = self._save_memory(params)
            elif action == "recall":
                result = self._recall(params)
            elif action == "list":
                result = self._list_all()
            elif action == "delete":
                result = self._delete(params)
            elif action == "search":
                result = self._search(params)
            else:
                result.error = f"Unknown action: {action}"
                result.success = False
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _save_memory(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        content = params.get("content", "")
        tags = params.get("tags", [])
        
        if not content:
            result.error = "Content is required"
            result.success = False
            return result
        
        memory = {
            "id": len(self._memories) + 1,
            "content": content,
            "tags": tags,
            "timestamp": datetime.now().isoformat(),
            "working_dir": self.working_dir
        }
        self._memories.append(memory)
        self._save_to_disk()
        
        result.output = f"Memory saved (#{memory['id']}): {content[:80]}"
        if tags:
            result.output += f"\nTags: {', '.join(tags)}"
        result.metadata = {"id": memory["id"]}
        return result
    
    def _recall(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        tags = params.get("tags", [])
        
        memories = self._memories
        if tags:
            memories = [m for m in memories if any(t in m.get("tags", []) for t in tags)]
        
        if not memories:
            result.output = "No memories found."
            return result
        
        # Show most recent 10
        recent = memories[-10:]
        lines = [f"Memories ({len(memories)} total, showing {len(recent)}):\n"]
        for m in reversed(recent):
            lines.append(f"  #{m['id']} [{m['timestamp'][:10]}]")
            lines.append(f"    {m['content'][:120]}")
            if m.get('tags'):
                lines.append(f"    Tags: {', '.join(m['tags'])}")
            lines.append("")
        
        result.output = '\n'.join(lines)
        result.metadata = {"total": len(memories), "shown": len(recent)}
        return result
    
    def _list_all(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        if not self._memories:
            result.output = "No memories stored."
            return result
        
        lines = [f"All Memories ({len(self._memories)}):\n"]
        for m in reversed(self._memories):
            tags_str = f" [{', '.join(m.get('tags', []))}]" if m.get('tags') else ""
            lines.append(f"  #{m['id']} {m['timestamp'][:16]}{tags_str}")
            lines.append(f"    {m['content'][:100]}")
            lines.append("")
        
        result.output = '\n'.join(lines)
        return result
    
    def _delete(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        query = params.get("query", "")
        
        if not query:
            result.error = "Provide the memory ID as query"
            result.success = False
            return result
        
        try:
            memory_id = int(query)
        except ValueError:
            result.error = "Query must be a memory ID number"
            result.success = False
            return result
        
        before = len(self._memories)
        self._memories = [m for m in self._memories if m["id"] != memory_id]
        self._save_to_disk()
        
        if len(self._memories) < before:
            result.output = f"Deleted memory #{memory_id}"
        else:
            result.output = f"Memory #{memory_id} not found"
        return result
    
    def _search(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        query = params.get("query", "").lower()
        
        if not query:
            result.error = "Query is required for search"
            result.success = False
            return result
        
        matches = []
        for m in self._memories:
            content_lower = m["content"].lower()
            tags_lower = ' '.join(m.get("tags", [])).lower()
            
            if query in content_lower or query in tags_lower:
                matches.append(m)
        
        if not matches:
            result.output = f"No memories matching: {query}"
            return result
        
        lines = [f"Found {len(matches)} memories matching '{query}':\n"]
        for m in matches:
            lines.append(f"  #{m['id']} [{m['timestamp'][:10]}] {m['content'][:100]}")
        
        result.output = '\n'.join(lines)
        result.metadata = {"matches": len(matches)}
        return result


class ProjectIndexTool(Tool):
    """Project structure analyzer and indexer"""
    name = "project_index"
    description = "Scan and index project structure, dependencies, and key files"
    category = "memory"
    requires_confirmation = False
    
    parameters = [
        ToolParameter("action", "string", "Action: scan, get, files, dependencies, entry_points", True),
        ToolParameter("path", "string", "Project path", False, "."),
        ToolParameter("refresh", "boolean", "Force re-scan even if cache exists", False, False)
    ]
    
    # Common entry point patterns
    ENTRY_POINTS = {
        "python": ["main.py", "__main__.py", "app.py", "manage.py", "wsgi.py", "asgi.py"],
        "javascript": ["index.js", "app.js", "server.js", "main.js"],
        "typescript": ["index.ts", "app.ts", "server.ts", "main.ts"],
        "go": ["main.go", "cmd/*/main.go"],
        "rust": ["src/main.rs", "src/lib.rs"]
    }
    
    LANGUAGE_EXTENSIONS = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "typescript", ".jsx": "javascript", ".go": "go",
        ".rs": "rust", ".java": "java", ".cpp": "c++", ".c": "c",
        ".h": "c", ".rb": "ruby", ".php": "php", ".swift": "swift",
        ".kt": "kotlin", ".md": "markdown", ".json": "json",
        ".yaml": "yaml", ".yml": "yaml", ".toml": "toml"
    }
    
    IGNORE_DIRS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        '.tox', '.mypy_cache', '.pytest_cache', 'dist', 'build',
        '.next', '.nuxt', 'target', '.tide'
    }
    
    def __init__(self, working_dir: str = "."):
        super().__init__(working_dir)
        self._index_file = Path(working_dir) / ".tide" / "project_index.json"
        self._index = None
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            action = params.get("action", "").lower()
            refresh = params.get("refresh", False)
            
            # Load cached index
            if not self._index and not refresh:
                self._load_index()
            
            if action == "scan":
                result = self._scan(params)
            elif action == "get":
                if not self._index:
                    result = self._scan(params)
                else:
                    result = self._get_summary()
            elif action == "files":
                if not self._index:
                    self._scan(params)
                result = self._get_files()
            elif action == "dependencies":
                if not self._index:
                    self._scan(params)
                result = self._get_dependencies()
            elif action == "entry_points":
                if not self._index:
                    self._scan(params)
                result = self._get_entry_points()
            else:
                result.error = f"Unknown action: {action}"
                result.success = False
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _load_index(self):
        if self._index_file.exists():
            try:
                with open(self._index_file, 'r') as f:
                    self._index = json.load(f)
            except Exception:
                self._index = None
    
    def _save_index(self):
        self._index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._index_file, 'w') as f:
            json.dump(self._index, f, indent=2)
    
    def _scan(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        path = params.get("path", ".")
        project_path = Path(self.working_dir) / path
        
        self._index = {
            "project_type": "unknown",
            "languages": {},
            "entry_points": [],
            "dependencies": [],
            "test_dirs": [],
            "total_files": 0,
            "total_lines": 0,
            "key_dirs": [],
            "manifest_files": [],
            "scanned_at": datetime.now().isoformat()
        }
        
        # Detect project type
        self._detect_project_type(project_path)
        
        # Scan files
        self._scan_files(project_path)
        
        # Detect entry points
        self._detect_entry_points(project_path)
        
        # Read dependencies
        self._read_dependencies(project_path)
        
        # Detect test directories
        self._detect_test_dirs(project_path)
        
        # Save cache
        self._save_index()
        
        result = self._get_summary()
        return result
    
    def _detect_project_type(self, path: Path):
        manifests = {
            "pyproject.toml": "python",
            "setup.py": "python",
            "setup.cfg": "python",
            "requirements.txt": "python",
            "package.json": "javascript/typescript",
            "go.mod": "go",
            "Cargo.toml": "rust",
            "pom.xml": "java",
            "build.gradle": "java",
            "Gemfile": "ruby",
            "composer.json": "php",
            "mix.exs": "elixir",
            "Makefile": "make"
        }
        
        found = []
        for manifest, lang in manifests.items():
            if (path / manifest).exists():
                found.append(manifest)
                self._index["project_type"] = lang
                self._index["manifest_files"].append(manifest)
        
        if not found:
            self._index["project_type"] = "unknown"
    
    def _scan_files(self, path: Path):
        file_count = 0
        line_count = 0
        languages = {}
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            # Track key directories
            rel_root = Path(root).relative_to(path)
            if rel_root != Path('.') and len(rel_root.parts) == 1:
                self._index["key_dirs"].append(str(rel_root))
            
            for file in files:
                ext = Path(file).suffix.lower()
                lang = self.LANGUAGE_EXTENSIONS.get(ext, "other")
                
                languages[lang] = languages.get(lang, 0) + 1
                file_count += 1
                
                # Count lines (approximate, skip large files)
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_size < 1_000_000:  # Skip files > 1MB
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            line_count += sum(1 for _ in f)
                except Exception:
                    pass
            
            if file_count > 5000:  # Safety cap
                break
        
        self._index["languages"] = languages
        self._index["total_files"] = file_count
        self._index["total_lines"] = line_count
    
    def _detect_entry_points(self, path: Path):
        for lang, patterns in self.ENTRY_POINTS.items():
            for pattern in patterns:
                if '*' in pattern:
                    matches = list(path.glob(pattern))
                    for m in matches:
                        self._index["entry_points"].append(str(m.relative_to(path)))
                elif (path / pattern).exists():
                    self._index["entry_points"].append(pattern)
    
    def _read_dependencies(self, path: Path):
        deps = []
        
        # Python: requirements.txt
        req_file = path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before ==, >=, etc.)
                            name = re.split(r'[=<>!~\[]', line)[0].strip()
                            if name:
                                deps.append({"name": name, "source": "requirements.txt"})
            except Exception:
                pass
        
        # Python: pyproject.toml (basic parsing)
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                # Simple regex for dependencies
                in_deps = False
                for line in content.split('\n'):
                    if 'dependencies' in line and '=' in line and '[' in line:
                        in_deps = True
                        continue
                    if in_deps:
                        if line.strip() == ']':
                            in_deps = False
                        elif line.strip().startswith('"'):
                            dep = line.strip().strip('",')
                            name = re.split(r'[=<>!~\[]', dep)[0].strip()
                            if name:
                                deps.append({"name": name, "source": "pyproject.toml"})
            except Exception:
                pass
        
        # Node: package.json
        pkg_json = path / "package.json"
        if pkg_json.exists():
            try:
                with open(pkg_json, 'r') as f:
                    pkg = json.load(f)
                for name in pkg.get("dependencies", {}):
                    deps.append({"name": name, "source": "package.json"})
                for name in pkg.get("devDependencies", {}):
                    deps.append({"name": name, "source": "package.json (dev)"})
            except Exception:
                pass
        
        self._index["dependencies"] = deps[:100]  # Cap at 100
    
    def _detect_test_dirs(self, path: Path):
        test_patterns = ["tests", "test", "__tests__", "spec", "specs"]
        for pattern in test_patterns:
            if (path / pattern).is_dir():
                self._index["test_dirs"].append(pattern)
    
    def _get_summary(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        if not self._index:
            result.output = "No project index. Run with action='scan' first."
            return result
        
        idx = self._index
        lines = [
            f"Project Type: {idx['project_type']}",
            f"Total Files: {idx['total_files']}",
            f"Total Lines: {idx['total_lines']:,}",
            f"Manifests: {', '.join(idx['manifest_files']) or 'none'}",
            f""
        ]
        
        if idx['languages']:
            lines.append("Languages:")
            sorted_langs = sorted(idx['languages'].items(), key=lambda x: x[1], reverse=True)
            for lang, count in sorted_langs[:10]:
                lines.append(f"  {lang}: {count} files")
        
        if idx['entry_points']:
            lines.append(f"\nEntry Points:")
            for ep in idx['entry_points']:
                lines.append(f"  {ep}")
        
        if idx['key_dirs']:
            lines.append(f"\nKey Directories:")
            for d in sorted(idx['key_dirs'])[:15]:
                lines.append(f"  {d}/")
        
        if idx['test_dirs']:
            lines.append(f"\nTest Directories:")
            for d in idx['test_dirs']:
                lines.append(f"  {d}/")
        
        if idx['dependencies']:
            dep_count = len(idx['dependencies'])
            lines.append(f"\nDependencies ({dep_count}):")
            for d in idx['dependencies'][:15]:
                lines.append(f"  {d['name']} ({d['source']})")
            if dep_count > 15:
                lines.append(f"  ... and {dep_count - 15} more")
        
        result.output = '\n'.join(lines)
        result.metadata = {
            "project_type": idx['project_type'],
            "total_files": idx['total_files'],
            "languages": idx['languages'],
            "dependency_count": len(idx['dependencies'])
        }
        return result
    
    def _get_files(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        if self._index and self._index.get("languages"):
            lines = ["Files by language:\n"]
            for lang, count in sorted(self._index["languages"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {lang}: {count}")
            result.output = '\n'.join(lines)
        else:
            result.output = "No file data. Run scan first."
        return result
    
    def _get_dependencies(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        if self._index and self._index.get("dependencies"):
            lines = [f"Dependencies ({len(self._index['dependencies'])}):\n"]
            for d in self._index['dependencies']:
                lines.append(f"  {d['name']} ({d['source']})")
            result.output = '\n'.join(lines)
        else:
            result.output = "No dependency data. Run scan first."
        return result
    
    def _get_entry_points(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        if self._index and self._index.get("entry_points"):
            lines = ["Entry points:\n"]
            for ep in self._index['entry_points']:
                lines.append(f"  {ep}")
            result.output = '\n'.join(lines)
        else:
            result.output = "No entry points detected. Run scan first."
        return result
