# Tide - AI-Powered Coding Agent

Professional AI coding assistant with IDE-like interface and advanced code understanding.

## Structure

```
tide/
├── cmd/
│   └── main.py              # Entry point
├── internal/
│   ├── agent/               # Core agent
│   │   ├── agent.py         # Main agent logic
│   │   ├── session.py       # Chat sessions
│   │   └── executor.py      # Tool execution
│   ├── tools/               # Tools
│   │   ├── base.py          # Tool base classes
│   │   ├── registry.py      # Tool registry
│   │   ├── filesystem.py    # File operations
│   │   ├── system.py        # System commands
│   │   └── code.py          # Code analysis
│   ├── ui/                  # UI
│   │   └── app.py           # Main application
│   └── config/
│       └── settings.py      # Configuration
└── README.md
```

## Quick Start

```bash
cd tide/cmd
python3 main.py
```

## Features

- **16 Professional Tools** - Filesystem, system, code analysis
- **AST-Based Code Understanding** - Parse Python structure
- **IDE-Like Interface** - File explorer + code viewer + chat
- **Session Management** - Persistent conversations
- **Multi-File Context** - Chat with multiple files

## Tools

| Tool | Description |
|------|-------------|
| read/write/edit | File operations |
| ls/glob/view | Directory operations |
| bash/python | System execution |
| analyze_code | AST parsing |
| grep | Pattern search |
| view_diff | File comparison |
| find_todos | Find TODO/FIXME |
| count_lines | LOC statistics |
| git_status | Git integration |

## Usage

1. **IDE Interface**: File explorer + code viewer + chat
2. **Simple Chat**: Basic chat mode
3. **Tools View**: See all 16 available tools
