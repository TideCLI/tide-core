# ✅ Working Example: Creating a Landing Page

## The Problem

`search_replace` tool is for **editing** existing files, not **creating** new files!

## The Solution

Use the RIGHT tool for each step:

### Step 1: Create Folder (bash tool)
```json
{"tool": "bash", "params": {"command": "mkdir -p my-landing-page"}}
```

### Step 2: Create HTML File (write tool)
```json
{"tool": "write", "params": {"path": "my-landing-page/index.html", "content": "<!DOCTYPE html>\n<html>\n<head>\n  <title>My Landing Page</title>\n  <style>\n    body { font-family: Arial; margin: 0; padding: 20px; }\n    h1 { color: #333; }\n  </style>\n</head>\n<body>\n  <h1>Welcome to My Site</h1>\n  <p>This is my landing page.</p>\n</body>\n</html>"}}
```

### Step 3: Create CSS File (write tool)
```json
{"tool": "write", "params": {"path": "my-landing-page/style.css", "content": "body {\n  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n  color: white;\n  min-height: 100vh;\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  font-family: 'Segoe UI', sans-serif;\n}\n\nh1 {\n  font-size: 3rem;\n  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);\n}"}}
```

### Step 4: Verify (ls tool)
```json
{"tool": "ls", "params": {"path": "my-landing-page"}}
```

---

## Complete Workflow in Tide Chat

```
➜ Create a landing page folder
🔧 Using tool: bash
✅ Success: Folder created

➜ Create HTML file with content
🔧 Using tool: write  
⚠️  Confirm? [y/N]: y
✅ Success: File created

➜ Create CSS file
🔧 Using tool: write
⚠️  Confirm? [y/N]: y
✅ Success: File created

➜ List the files
🔧 Using tool: ls
📁 my-landing-page/
  ├── 📄 index.html
  └── 📄 style.css
```

---

## Tool Selection Quick Reference

| Task | Tool | Why |
|------|------|-----|
| Create folder | `bash` | mkdir command |
| Create file | `write` | Creates new file |
| Edit file | `search_replace` | Modifies existing |
| Delete file | `bash` | rm command |
| List files | `ls` | Directory listing |
| View file | `view` | Read contents |

---

## Common Mistake

### ❌ Wrong Approach
Using `search_replace` to create a file:
```
User: "Create index.html"
AI: {"tool": "search_replace", ...}  
❌ Error: "File not found - use write tool instead"
```

### ✅ Correct Approach
Using `write` to create, `search_replace` to edit:
```
User: "Create index.html"
AI: {"tool": "write", ...}
✅ Success: File created

User: "Change the title"
AI: {"tool": "search_replace", ...}
✅ Success: File edited
```

---

## Try It Now

Run these commands in `tide chat`:

```
➜ Create folder test-project
➜ Create test-project/README.md with "# My Project"
➜ List files in test-project
```

Each should use the correct tool automatically!
