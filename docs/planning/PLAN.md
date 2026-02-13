# 🌊 Tide OS - Simplified Improvement Plan

## Focus Areas
1. **Better Tool Calling** - Make tools actually execute
2. **Better TUI Interactions** - Modern, responsive interface

## OUT OF SCOPE (Skip These)
- ❌ Git integration
- ❌ RepoMap / Repository context
- ❌ Streaming responses
- ❌ Web interface
- ❌ VS Code extension

---

## Phase 1: Fix Tool Calling (CRITICAL)

### Problem
AI responds with text like "I'll create a folder for you" but doesn't actually call tools.

### Solution

#### 1.1 Force Tool Usage
Update system prompt to be extremely explicit:
```
CRITICAL: When user asks you to CREATE, WRITE, EDIT, or DELETE:
1. You MUST respond with ONLY JSON tool call
2. NO explanations, NO markdown, JUST JSON
3. Example: {"tool": "bash", "params": {"command": "mkdir test"}}
```

#### 1.2 Tool Execution Chain
Current flow: User → AI → (maybe tool) → Response
New flow: User → AI → MUST use tool → Execute → Show result → Confirm success

#### 1.3 Add Tool Confirmation UI
In TUI: Show tool call in a modal/dialog, ask user to confirm, then execute.

---

## Phase 2: Better TUI Interactions

### 2.1 Main Layout
```
┌─────────────────────────────────────────────────────┐
│ Header: Tide OS v3.0.0              Model: nanbeige │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │  Chat Area                               │
│          │  ┌────────────────────────────────────┐  │
│ - Tools  │  │ User: Create a folder              │  │
│ - Models │  │                                    │  │
│          │  │ AI: 🔧 Using tool: bash            │  │
│          │  │     ✅ Folder created              │  │
│          │  └────────────────────────────────────┘  │
│          │                                          │
│          │  Input: [Type here...        ] [Send]   │
└──────────┴──────────────────────────────────────────┘
```

### 2.2 Interactive Elements
- **Tool Cards**: Show tool execution as expandable cards
- **Confirmation Modals**: For destructive operations
- **Progress Indicators**: Show when tool is running
- **Syntax Highlighting**: For code blocks in responses

### 2.3 Keyboard Shortcuts
- `Ctrl+Enter` - Send message
- `Ctrl+L` - Clear chat
- `Ctrl+M` - Open model selector
- `Ctrl+T` - Open tools panel
- `Esc` - Cancel current operation

---

## Phase 3: Tool Execution Flow

### Current (Broken)
```
User: Create a folder
AI: I'll create a folder for you! 
    First, let me make the directory...
    (just text, no actual tool call)
```

### Fixed (New)
```
User: Create a folder called test
AI: {"tool": "bash", "params": {"command": "mkdir test"}}
System: 🔧 Executing: bash "mkdir test"
System: ✅ Success: Folder created
AI: I've created the folder "test" for you!
```

---

## Implementation Status

### ✅ Phase 1: Tool Calling Fix (COMPLETE)
- [x] Improve system prompt (force JSON responses)
- [x] Fix JSON parser for tool detection
- [x] Add "Tool Mode" - AI must use tools for actions
- [x] Create tool execution confirmation UI
- [x] Test with real file operations

### 🔄 Phase 2: Enhanced TUI (IN PROGRESS)
- [x] Improve layout with proper sidebar (in TUI app)
- [x] Add tool execution confirmation (in CLI)
- [ ] Add tool result cards
- [ ] Keyboard shortcuts
- [ ] Progress indicators

### 📋 Phase 3: Polish (PENDING)
- [ ] Syntax highlighting in chat
- [ ] Better error handling
- [ ] Tool result formatting
- [ ] Session persistence

---

## Key Design Decisions

### 1. Tool-First Mode
When user asks for actions (create, edit, delete), AI MUST use tools.
Enforce this by:
- System prompt rules
- Parsing logic that rejects non-JSON action responses
- Re-prompting if AI forgets to use tools

### 2. Explicit Confirmation
All file operations show:
- What tool will be called
- What parameters will be used
- Confirm/Cancel buttons

### 3. Visual Feedback
- Loading spinner while AI thinks
- Tool execution card (expandable)
- Success/error icons
- Progress for multi-step operations

---

## Success Metrics

- [ ] Creating files/folders works 100% of time
- [ ] Editing files works 100% of time
- [ ] User confirms every destructive action
- [ ] TUI feels responsive (< 100ms for UI actions)
- [ ] Clear visual feedback for all operations
