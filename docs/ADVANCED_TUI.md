# 🌊 Tide OS - Advanced TUI

## Claude Code / OpenCode Style Interface

### 🎯 Launch

```bash
# Standard TUI
tide tui

# Advanced TUI (Claude Code style)
tide advanced
```

### ✨ Features

#### 4-Panel Layout

```
┌─────────────┬──────────────┬──────────────┐
│ 📁 Explorer │ 💻 Editor    │ 💬 Chat      │
│             │              │              │
│  File Tree  │  Syntax      │  AI          │
│  Navigation │  Highlighted │  Assistant   │
│             │  Code        │              │
├─────────────┴──────────────┴──────────────┤
│ 💻 Terminal                                 │
│  Run bash, git, python commands           │
└───────────────────────────────────────────┘
```

#### 📁 File Browser (Left Panel)
- **Directory Tree** - Navigate your project
- **Click to Open** - Files open in the editor
- **Visual Indicators** - See file types at a glance

#### 💻 Code Editor (Center Panel)
- **Syntax Highlighting** - For Python, JS, HTML, CSS, etc.
- **Line Numbers** - Easy reference
- **Multiple Tabs** - Open multiple files
- **Click Tabs** - Switch between open files

#### 💬 Chat Panel (Right Panel)
- **Rich Messages** - Markdown support
- **Code Blocks** - Syntax highlighted
- **Tool Results** - See what AI is doing
- **Quick Input** - Enter at bottom

#### 💻 Terminal (Bottom Panel)
- **Integrated Terminal** - Run commands directly
- **Command History** - Scroll through output
- **Real-time Output** - See results immediately
- **All Commands** - bash, git, python, etc.

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+M` | Change Model |
| `Ctrl+O` | Focus File Browser |
| `Ctrl+T` | Focus Terminal |
| `Ctrl+Q` | Quit |

### 🛠️ Usage Examples

#### 1. Open and Edit a File
```
1. Click on "tide/agent.py" in left panel
2. File opens in center editor with syntax highlighting
3. Ask AI in chat: "Add a comment at line 10"
4. AI uses search_replace to modify the file
```

#### 2. Run Terminal Commands
```
1. Click in terminal at bottom
2. Type: git status
3. See output in terminal panel
4. Type: mkdir new_folder
```

#### 3. Chat with AI
```
1. Type in chat panel: "List all Python files"
2. AI responds with file list
3. Click on any file to open it
```

#### 4. Model Switching
```
1. Press Ctrl+M
2. Select different model (llama3.1, qwen3, etc.)
3. Sidebar updates immediately
4. Continue chatting with new model
```

### 🔄 Workflow Example

```
User Action                    Interface Response
─────────────────────────────────────────────────
Click on cli.py               File opens in editor
                              with syntax highlighting
                              
Type in terminal:             Output appears below
$ python --version            Python 3.11.2

Ask in chat:                  AI responds with code
"Add error handling"          block and offers to edit

Click "Apply"                 File is modified,
                              changes shown in editor
```

### 📊 Comparison

| Feature | Claude Code | OpenCode | Tide OS Advanced |
|---------|-------------|----------|------------------|
| File Browser | ✅ | ✅ | ✅ |
| Code Editor | ✅ | ✅ | ✅ |
| Split View | ✅ | ✅ | ✅ |
| Terminal | ✅ | ✅ | ✅ |
| AI Chat | ✅ | ✅ | ✅ |
| Syntax Highlight | ✅ | ✅ | ✅ |
| Multi-model | ❌ | ❌ | ✅ |
| Offline | ❌ | ❌ | ✅ |
| Cost | $20/mo | Free | Free |

### 🎨 Customization

The interface uses Textual CSS for styling. Key areas:

- `file-browser-panel` - Left sidebar
- `code-editor-panel` - Center editor
- `chat-panel` - Right chat
- `terminal-panel` - Bottom terminal

### 🚀 Tips

1. **Quick File Open** - Click any file in left panel
2. **Multi-file Work** - Open multiple files, switch via tabs
3. **Terminal Power** - Run any command without leaving app
4. **Contextual AI** - AI knows what files you have open
5. **Live Editing** - See changes as AI makes them

### 📝 Files

```
tide/ui/
├── app.py           # Basic TUI
└── advanced_app.py  # Advanced (Claude Code style)
```

### 🐛 Troubleshooting

**Issue**: Advanced TUI won't start
```bash
# Install missing dependencies
pip install textual-textarea
```

**Issue**: File browser empty
```bash
# Make sure you run from a directory with files
cd /path/to/project
tide advanced
```

**Issue**: Terminal not responding
- Click in terminal panel first
- Try pressing Enter

### 🎉 Enjoy!

The advanced TUI brings professional IDE features to your AI coding assistant!