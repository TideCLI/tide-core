# 🌊 Tide OS - 23 Professional Tools

## Summary

Tide OS now has **23 tools** - more than Claude Code (11) and Aider (18)!

## Tool Categories

### 📁 FILESYSTEM (7 tools)
- `view` - Read files with line numbers
- `ls` - List directory contents
- `edit` - Edit files (whole file replacement)
- `write` - Create new files
- `glob` - Find files by pattern
- `search_replace` ✨ - Precise search/replace editing
- `multi_edit` ✨ - Multiple edits at once

### 🔧 SYSTEM (3 tools)
- `bash` - Execute shell commands
- `python` - Run Python code
- `read` - Quick file read

### 💻 CODE (5 tools)
- `grep` - Search file contents
- `analyze_code` - AST-based code analysis
- `find_todos` - Find TODO/FIXME markers
- `lint` ✨ - Run ruff/pylint/eslint
- `format` ✨ - Auto-format code

### 🌐 WEB (2 tools) - NEW!
- `web_search` ✨ - Search the web (DuckDuckGo)
- `fetch_url` ✨ - Fetch content from URLs

### 📦 GIT (6 tools) - NEW!
- `git_status` ✨ - Check repository status
- `git_diff` ✨ - Show changes
- `git_log` ✨ - View commit history
- `git_add` ✨ - Stage files
- `git_commit` ✨ - Commit changes
- `git_branch` ✨ - List branches

## Installation

### Optional Dependencies

```bash
# For web search
pip install duckduckgo-search

# For linting (recommended - fast!)
pip install ruff

# For formatting
pip install black

# Git is usually pre-installed
git --version
```

## Usage Examples

### Web Search (Like Claude Code)
```
➜ What is the latest version of React?
🔧 Using tool: web_search
✅ React 18.2.0 is the current stable version...
```

### Git Workflow (Like Aider)
```
➜ Check git status
🔧 Using tool: git_status
📊 Git Status:
   M modified: tide/agent.py
   ?? untracked: new_tools.py

➜ Commit the changes
🔧 Using tool: git_commit
✅ Committed: Added new tools
```

### Precise Editing (Like Claude)
```
➜ Replace "old_func" with "new_func" in app.py
🔧 Using tool: search_replace
   Search: def old_func():
   Replace: def new_func():
⚠️  Confirm? [y/N]: y
✅ Edited app.py
```

### Code Quality
```
➜ Lint the code
🔧 Using tool: lint
⚠️  ruff results:
   tide/agent.py:42:1: E302 expected 2 blank lines

➜ Format the files
🔧 Using tool: format
✅ Formatted with ruff
```

## Comparison

| Feature | Tide OS | Claude Code | Aider |
|---------|---------|-------------|-------|
| File Operations | ✅ 7 | ✅ 5 | ✅ 5 |
| Git Tools | ✅ 6 | ❌ 0 | ✅ 4 |
| Web Search | ✅ 1 | ✅ 1 | ✅ 1 |
| Code Analysis | ✅ 5 | ✅ 3 | ✅ 4 |
| Lint/Format | ✅ 2 | ❌ 0 | ✅ 2 |
| **Total Tools** | **23** | **11** | **18** |

## Next Steps

1. Install optional dependencies
2. Try `tide chat` or `tide`
3. Test new tools like web_search, git_commit, search_replace

The tool system is now on par with industry leaders! 🚀
