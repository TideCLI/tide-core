# Tide OS - Tool Expansion Plan

## Goal: Match Claude Code & Aider Tool Coverage

---

## Phase 1: Essential Tools (Add 8 more = 19 total)

### 1. Web Search Tool
```python
# tools/web.py
class WebSearchTool(Tool):
    """Search the web for up-to-date information"""
    name = "web_search"
    
    def _execute(self, query: str, num_results: int = 5) -> ToolResult:
        # Use duckduckgo or similar
        # Return search results
```

**Usage:**
```
User: "What is the latest version of Python?"
AI: {"tool": "web_search", "params": {"query": "latest python version 2024"}}
```

### 2. Git Status Tool
```python
class GitStatusTool(Tool):
    """Check git repository status"""
    name = "git_status"
    
    def _execute(self) -> ToolResult:
        # Run git status
        # Show modified, staged, untracked files
```

### 3. Git Diff Tool
```python
class GitDiffTool(Tool):
    """Show git diff for changes"""
    name = "git_diff"
    
    def _execute(self, file: Optional[str] = None, staged: bool = False) -> ToolResult:
        # Show what changed
```

### 4. Git Commit Tool
```python
class GitCommitTool(Tool):
    """Commit changes with a message"""
    name = "git_commit"
    require_confirmation = True
    
    def _execute(self, message: str, add_all: bool = False) -> ToolResult:
        # Stage files and commit
```

### 5. Search Replace Tool (Better Edit)
```python
class SearchReplaceTool(Tool):
    """Edit file using search/replace blocks like Claude"""
    name = "search_replace"
    require_confirmation = True
    
    def _execute(self, path: str, search: str, replace: str) -> ToolResult:
        # Find exact text and replace
        # More precise than whole file edit
```

### 6. Linter Tool
```python
class LinterTool(Tool):
    """Run linter on code files"""
    name = "lint"
    
    def _execute(self, path: str, linter: str = "auto") -> ToolResult:
        # Run pylint, ruff, or eslint
        # Show errors and warnings
```

### 7. Test Runner Tool
```python
class TestTool(Tool):
    """Run tests and show results"""
    name = "test"
    
    def _execute(self, path: str = ".", test_file: Optional[str] = None) -> ToolResult:
        # Run pytest, unittest, etc.
        # Show pass/fail status
```

### 8. Undo Tool
```python
class UndoTool(Tool):
    """Undo last file change"""
    name = "undo"
    
    def _execute(self, steps: int = 1) -> ToolResult:
        # Revert last edit operation
```

---

## Phase 2: Advanced Tools (Add 6 more = 25 total)

### 9. HTTP Request Tool
```python
class HttpTool(Tool):
    """Make HTTP requests"""
    name = "http"
    
    def _execute(self, url: str, method: str = "GET", 
                 headers: Optional[Dict] = None, 
                 body: Optional[str] = None) -> ToolResult:
        # For API testing, webhooks
```

### 10. JSON Processor Tool
```python
class JsonTool(Tool):
    """Process and query JSON data"""
    name = "json_query"
    
    def _execute(self, path: str, query: Optional[str] = None) -> ToolResult:
        # Parse, validate, query JSON
```

### 11. Environment Variables Tool
```python
class EnvTool(Tool):
    """Manage environment variables"""
    name = "env"
    
    def _execute(self, action: str, key: Optional[str] = None, 
                 value: Optional[str] = None) -> ToolResult:
        # Get/set env vars
```

### 12. Port Scanner Tool
```python
class PortTool(Tool):
    """Check ports and network"""
    name = "port"
    
    def _execute(self, host: str = "localhost", port: Optional[int] = None) -> ToolResult:
        # Check if ports are open
```

### 13. Archive Tool
```python
class ArchiveTool(Tool):
    """Compress/decompress files"""
    name = "archive"
    
    def _execute(self, action: str, source: str, dest: Optional[str] = None) -> ToolResult:
        # zip, tar, unzip
```

### 14. Database Query Tool
```python
class DbTool(Tool):
    """Query databases"""
    name = "db_query"
    
    def _execute(self, connection: str, query: str) -> ToolResult:
        # SQLite support initially
```

---

## Phase 3: Smart Tools (Add 5 more = 30 total)

### 15. Smart Search Tool
```python
class SmartGrepTool(Tool):
    """Intelligent code search with context"""
    name = "smart_grep"
    
    def _execute(self, pattern: str, context: int = 5) -> ToolResult:
        # Search with better context than basic grep
```

### 16. Code Explain Tool
```python
class ExplainTool(Tool):
    """Explain what code does"""
    name = "explain"
    
    def _execute(self, path: str) -> ToolResult:
        # Read file and provide explanation
```

### 17. Refactor Tool
```python
class RefactorTool(Tool):
    """Suggest and apply refactoring"""
    name = "refactor"
    require_confirmation = True
    
    def _execute(self, path: str, goal: str) -> ToolResult:
        # Analyze and suggest improvements
```

### 18. Dependency Tool
```python
class DepsTool(Tool):
    """Check and manage dependencies"""
    name = "deps"
    
    def _execute(self, action: str = "list") -> ToolResult:
        # pip list, check outdated, etc.
```

### 19. Documentation Tool
```python
class DocsTool(Tool):
    """Generate documentation from code"""
    name = "docs"
    
    def _execute(self, path: str, output: Optional[str] = None) -> ToolResult:
        # Extract docstrings, generate markdown
```

---

## Comparison After Implementation

| Category | Tide OS | Claude Code | Aider |
|----------|---------|-------------|-------|
| File Operations | ✅ 5+ | ✅ 5 | ✅ 5 |
| Git Tools | ✅ 3 | ❌ 0 | ✅ 4 |
| Code Analysis | ✅ 4 | ✅ 3 | ✅ 4 |
| Web Integration | ✅ 1 | ✅ 1 | ✅ 1 |
| System/Network | ✅ 5 | ✅ 2 | ✅ 2 |
| Testing | ✅ 2 | ❌ 0 | ✅ 2 |
| **Total** | **30** | **11** | **18** |

---

## Implementation Order

### Week 1: Core Expansion (Tools 1-8)
1. Web search - DuckDuckGo integration
2. Git tools - status, diff, commit
3. Search/replace - Better edit tool
4. Linter - pylint/ruff wrapper
5. Test runner - pytest integration
6. Undo - Track and revert changes

### Week 2: Advanced (Tools 9-14)
7. HTTP requests
8. JSON processing
9. Environment variables
10. Port scanning
11. Archive operations

### Week 3: Smart Tools (Tools 15-19)
12. Smart grep
13. Code explanation
14. Refactoring
15. Dependencies
16. Documentation generation

---

## Quick Implementation Example

Adding a new tool takes ~5 minutes:

```python
# tide/tools/new_tool.py
from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool

@register_tool
class MyTool(Tool):
    name = "my_tool"
    description = "What this tool does"
    category = "category"
    require_confirmation = False  # or True
    
    parameters = {
        "param1": Parameter(
            name="param1",
            type=ParameterType.STRING,
            description="What this param does",
            required=True
        )
    }
    
    def _execute(self, param1: str) -> ToolResult:
        # Do the work
        result = do_something(param1)
        return ToolResult.success_result(
            output=f"Done: {result}",
            data={"key": "value"}
        )
```

Then import it in `agent.py` to register.

---

## Recommended Next Steps

1. **Start with Web Search** - Easy to implement, high value
2. **Add Git Tools** - Many users need this
3. **Improve Edit Tool** - Search/replace is essential
4. **Add Linter** - Quality assurance

These 4 tools would bring Tide OS to feature parity with Claude Code!
