# 🛠️ Tide OS - Tool Usage Guide

## Quick Reference: Which Tool to Use?

### Creating Files → Use `write`
```
User: "Create an HTML file called index.html"
AI: {"tool": "write", "params": {"path": "index.html", "content": "<!DOCTYPE html>..."}}
```

### Editing Existing Files → Use `search_replace`
```
User: "Change the title in index.html"
AI: {"tool": "search_replace", "params": {"path": "index.html", "search": "<title>Old</title>", "replace": "<title>New</title>"}}
```

### Listing Files → Use `ls`
```
User: "Show me the files"
AI: {"tool": "ls", "params": {"path": "."}}
```

### Running Commands → Use `bash`
```
User: "Create a folder"
AI: {"tool": "bash", "params": {"command": "mkdir myfolder"}}
```

---

## Complete Tool Guide

### 📁 FILESYSTEM TOOLS

#### `write` - CREATE new files
**Use when:** Creating new files that don't exist
```json
{"tool": "write", "params": {"path": "style.css", "content": "body { margin: 0; }"}}
```
**Result:** ✅ Creates new file

#### `search_replace` - EDIT existing files
**Use when:** Modifying existing files with precision
```json
{"tool": "search_replace", "params": {"path": "index.html", "search": "<h1>Hello</h1>", "replace": "<h1>Welcome</h1>"}}
```
**Result:** ✅ Replaces only matching text

#### `edit` - REPLACE whole file
**Use when:** Complete file replacement
```json
{"tool": "edit", "params": {"path": "config.json", "oldText": "{\"debug\": true}", "newText": "{\"debug\": false}"}}
```

#### `view` - READ file contents
**Use when:** Need to see what's in a file
```json
{"tool": "view", "params": {"path": "index.html"}}
```

#### `ls` - LIST directory
**Use when:** See what files exist
```json
{"tool": "ls", "params": {"path": "."}}
```

#### `glob` - FIND files
**Use when:** Find files by pattern
```json
{"tool": "glob", "params": {"pattern": "*.py"}}
```

---

### 🔧 SYSTEM TOOLS

#### `bash` - Run shell commands
**Use when:** Creating folders, moving files, etc.
```json
{"tool": "bash", "params": {"command": "mkdir -p css js images"}}
```

#### `python` - Execute Python code
**Use when:** Calculations, data processing
```json
{"tool": "python", "params": {"code": "print(2 + 2)"}}
```

---

### 💻 CODE TOOLS

#### `lint` - Check code quality
**Use when:** Checking for errors
```json
{"tool": "lint", "params": {"path": "script.py"}}
```

#### `format` - Auto-format code
**Use when:** Cleaning up code style
```json
{"tool": "format", "params": {"path": "script.py"}}
```

---

### 🌐 WEB TOOLS

#### `web_search` - Search the web
**Use when:** Need current information
```json
{"tool": "web_search", "params": {"query": "latest CSS features 2024"}}
```

#### `fetch_url` - Read web pages
**Use when:** Get content from a URL
```json
{"tool": "fetch_url", "params": {"url": "https://example.com/docs"}}
```

---

### 📦 GIT TOOLS

#### `git_status` - Check repo status
```json
{"tool": "git_status", "params": {}}
```

#### `git_commit` - Commit changes
```json
{"tool": "git_commit", "params": {"message": "Added landing page"}}
```

---

## Common Workflows

### 1. Create a Web Project
```
Step 1: Create folder structure
→ {"tool": "bash", "params": {"command": "mkdir -p myproject/css myproject/js"}}

Step 2: Create HTML file
→ {"tool": "write", "params": {"path": "myproject/index.html", "content": "..."}}

Step 3: Create CSS file  
→ {"tool": "write", "params": {"path": "myproject/css/style.css", "content": "..."}}

Step 4: View result
→ {"tool": "ls", "params": {"path": "myproject"}}
```

### 2. Edit Existing Code
```
Step 1: View the file first
→ {"tool": "view", "params": {"path": "app.py", "limit": 50}}

Step 2: Make precise edit
→ {"tool": "search_replace", "params": {"path": "app.py", "search": "def old():", "replace": "def new():"}}

Step 3: Lint to check
→ {"tool": "lint", "params": {"path": "app.py"}}
```

### 3. Git Workflow
```
Step 1: Check status
→ {"tool": "git_status", "params": {}}

Step 2: Stage files
→ {"tool": "git_add", "params": {"files": "."}}

Step 3: Commit
→ {"tool": "git_commit", "params": {"message": "My changes"}}
```

---

## ⚠️ Common Mistakes

### ❌ Wrong: Using search_replace to create file
```
User: "Create a new file"
AI tries: {"tool": "search_replace", ...}  
Result: ❌ "File not found"
```

### ✅ Correct: Use write to create
```
AI should: {"tool": "write", "params": {"path": "file.txt", "content": "..."}}
Result: ✅ File created
```

---

### ❌ Wrong: Using edit for small changes
```
User: "Change one line"
AI tries: {"tool": "edit", "params": {"oldText": "... entire file content ..."}}
Result: ⚠️ Inefficient
```

### ✅ Correct: Use search_replace
```
AI should: {"tool": "search_replace", "params": {"search": "old line", "replace": "new line"}}
Result: ✅ Precise edit
```

---

## Tool Selection Cheat Sheet

| Task | Tool | Example |
|------|------|---------|
| Create new file | `write` | `write` path, content |
| Edit existing file | `search_replace` | `search_replace` path, search, replace |
| Edit multiple places | `multi_edit` | `multi_edit` path, edits array |
| Replace whole file | `edit` | `edit` path, oldText, newText |
| Create folder | `bash` | `bash` mkdir folder |
| Read file | `view` | `view` path |
| List files | `ls` | `ls` path |
| Find files | `glob` | `glob` pattern |
| Check code | `lint` | `lint` path |
| Format code | `format` | `format` path |
| Search web | `web_search` | `web_search` query |
| Git status | `git_status` | `git_status` |
| Git commit | `git_commit` | `git_commit` message |

---

## Testing Tools

Try these commands in `tide chat`:

```
➜ Create a file test.txt with "Hello World"
→ Should use: write tool

➜ Change "Hello" to "Hi" in test.txt  
→ Should use: search_replace tool

➜ List all files
→ Should use: ls tool

➜ Create folder myproject
→ Should use: bash tool
```
