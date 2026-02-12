# Tide v2 - Professional AI Coding Agent

## Overview

Tide v2 is a complete rewrite based on **charmbracelet/crush** architecture, optimized for **Ollama** local LLMs.

## Key Improvements from v1

### 1. Tool System (Based on crush)

| Feature | Tide v1 | Tide v2 (crush-based) |
|---------|---------|----------------------|
| Tool base class | Simple | Full metadata + validation |
| Parameter validation | None | Type checking + required fields |
| Result metadata | Basic | Rich metadata + timing |
| Ollama format | Manual | Auto-converted |
| Execution tracking | None | Full history |

**Example Tool (v2):**
```python
class ViewTool(Tool):
    name = "view"
    description = "Read file contents"
    parameters = [
        ToolParameter("file_path", "string", "Path to file", True),
        ToolParameter("offset", "integer", "Start line", False, 0),
    ]
    max_output_length = 30000
    
    def execute(self, params):
        # Implementation with full error handling
```

### 2. Filesystem Tools (from crush)

**View Tool:**
- ✅ Line numbers (aligned like crush)
- ✅ Offset/limit support
- ✅ 5MB size limit
- ✅ Smart file suggestions on 404
- ✅ Line truncation for long lines

**LS Tool:**
- ✅ Tree structure (like crush)
- ✅ Depth limiting
- ✅ Ignore patterns
- ✅ File count limits
- ✅ Truncation warnings

**Edit Tool:**
- ✅ Diff generation
- ✅ Confirmation required
- ✅ Exact match validation

### 3. System Tools (from crush)

**Bash Tool:**
- ✅ Banned commands list (security)
- ✅ Timeout support
- ✅ Working directory support
- ✅ Return code tracking
- ✅ stdout/stderr separation

**Python Tool:**
- ✅ Restricted namespace
- ✅ Dangerous code detection
- ✅ Timeout handling

### 4. Code Tools

**Analyze Tool:**
- ✅ AST parsing
- ✅ Imports, functions, classes
- ✅ Docstring extraction
- ✅ Formatted output with emojis

**Grep Tool:**
- ✅ Ripgrep integration
- ✅ Fallback to grep
- ✅ Context lines
- ✅ File glob patterns
- ✅ Colored output

### 5. Architecture Improvements

**Tool Registry:**
- Category-based organization
- Execution history
- Statistics tracking
- Validation before execution

**Agent:**
- Proper message management
- Tool call parsing
- Multi-step execution
- Context preservation

**Ollama Client:**
- Connection checking
- Tool call parsing (multiple formats)
- Error handling
- Model listing

## Directory Structure

```
tide_v2/
├── __init__.py
├── __main__.py
├── agent.py              # Main agent with tool support
├── cli.py                # Professional CLI
├── ollama_client.py      # Ollama API client
├── tool_registry.py      # Tool management
└── tools/
    ├── __init__.py
    ├── base.py           # Tool base classes
    ├── filesystem.py     # View, LS, Edit, Write, Glob
    ├── system.py         # Bash, Python
    └── code.py           # Analyze, Grep, Todos
```

## Usage

### Interactive Mode
```bash
cd /home/snoozescript/tide-os
python3 -m tide_v2
```

### Quick Chat
```bash
python3 -m tide_v2 "analyze agent.py"
```

### List Tools
```bash
python3 -m tide_v2 --tools
```

### Direct Tool Execution
```
➜ tool view {"file_path": "README.md"}
➜ tool bash {"command": "ls -la"}
➜ tool analyze_code {"file_path": "agent.py"}
```

## Commands in Interactive Mode

| Command | Description |
|---------|-------------|
| `tools` | List all available tools |
| `tool <name> {params}` | Execute tool directly |
| `clear` | Clear chat history |
| `stats` | Show agent statistics |
| `help` | Show help |
| `exit` | Quit |

## Comparison: Tide v2 vs crush

| Feature | crush | Tide v2 |
|---------|-------|---------|
| Language | Go | Python |
| LLM | Cloud APIs | Ollama (local) |
| Cost | Paid subscription | Free |
| Offline | No | ✅ Yes |
| Privacy | Cloud processing | ✅ Local |
| Tools | 20+ | 10 (growing) |
| Permission system | ✅ Full | Basic |
| Job management | ✅ Yes | Basic |
| TUI | ✅ Bubble Tea | Rich (simpler) |
| Configuration | crush.json | tide.json |

## Advantages of Tide v2

### Over crush:
1. ✅ **Free** - No API costs
2. ✅ **Offline** - Works without internet
3. ✅ **Private** - Local LLM processing
4. ✅ **Python** - Easier to modify/extend
5. ✅ **Ollama** - Works with any local model

### Over Tide v1:
1. ✅ **Professional architecture** - Based on crush
2. ✅ **Better tools** - Line numbers, diffs, tree view
3. ✅ **Validation** - Parameter type checking
4. ✅ **Security** - Banned commands, timeouts
5. ✅ **Metadata** - Rich execution info
6. ✅ **History** - Execution tracking

## Testing

```bash
# Test imports
cd /home/snoozescript/tide-os
python3 -c "from tide_v2 import TideAgent; print('✅ OK')"

# Test agent
python3 -c "
from tide_v2 import TideAgent
agent = TideAgent()
print(f'Tools: {len(agent.get_available_tools())}')
print(f'Available: {agent.get_available_tools()}')
"

# Run CLI
python3 -m tide_v2 --tools
```

## Future Enhancements

From crush that can be added:
- [ ] Multi-edit (batch operations)
- [ ] Job management (async execution)
- [ ] Web fetch/search
- [ ] Sourcegraph integration
- [ ] LSP integration
- [ ] Diff viewer
- [ ] Image attachments
- [ ] Session management
- [ ] Better TUI with Bubble Tea

## Files Created

```
tide_v2/
├── __init__.py
├── __main__.py
├── agent.py              (180 lines)
├── cli.py                (240 lines)
├── ollama_client.py      (170 lines)
├── tool_registry.py      (160 lines)
└── tools/
    ├── __init__.py
    ├── base.py           (180 lines)
    ├── filesystem.py     (550 lines)
    ├── system.py         (250 lines)
    └── code.py           (350 lines)

tide.json                 # Configuration file
TIDE_V2_SUMMARY.md        # This file
```

**Total: 2100+ lines of optimized code**

## Status

✅ **Complete and working!**

- Professional tool architecture
- 10 production-grade tools
- Ollama integration
- Interactive CLI
- Direct tool execution
- Error handling
- Security features

**Ready for use and further development!** 🌊🎓
