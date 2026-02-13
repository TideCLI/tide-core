# 🌊 Tide OS

**Professional AI Coding Agent** - inspired by [charmbracelet/crush](https://github.com/charmbracelet/crush)

Tide OS is a clean, professional AI coding assistant that works **offline** with local Ollama models. Built with a crush-inspired architecture for reliability and extensibility.

## ✨ Features

- 🤖 **AI Chat** - Natural conversation with tool calling
- 🛠️ **10 Professional Tools** - View, edit, bash, grep, analyze, and more
- 🔒 **Works Offline** - Uses local Ollama models (no API costs)
- ⚡ **Fast** - Direct Ollama integration
- 🎨 **Beautiful UI** - Rich terminal interface
- 🔧 **Configurable** - JSON-based configuration

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd tide-os

# Install dependencies
pip install -e .

# Or install in development mode
pip install -e ".[dev]"

# Install Ollama models
curl -fsSL https://ollama.com/install.sh | sh
ollama pull hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M  # Default
ollama pull llama3.1:8b
ollama pull qwen3:latest
```

## 🚀 Quick Start

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Models

```bash
# Default (fast, efficient - 2.4GB)
ollama pull hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M

# Alternative models
ollama pull llama3.1:8b    # Higher quality (4.9GB)
ollama pull qwen3:latest    # Latest generation
```

### 3. Start Tide

```bash
# Launch modern TUI (default)
tide

# Or use CLI mode
tide chat

# With specific model
tide -m nanbeige
tide -m llama3.1
tide -m qwen3
```

## 🛠️ Available Tools

| Tool | Category | Description | Confirmation |
|------|----------|-------------|--------------|
| **view** | filesystem | Read files with line numbers | - |
| **ls** | filesystem | Tree directory listing | - |
| **edit** | filesystem | Edit files with diff preview | ⚠️ |
| **write** | filesystem | Create new files | ⚠️ |
| **glob** | filesystem | Find files by pattern | - |
| **read** | system | Quick file read | - |
| **bash** | system | Execute shell commands | ⚠️ |
| **python** | system | Run Python code | - |
| **grep** | code | Search file contents | - |
| **analyze_code** | code | AST-based code analysis | - |
| **find_todos** | code | Find TODO/FIXME markers | - |

## 📖 Usage

### Modern TUI (Default)

```bash
$ tide
🌊 Launching Tide OS TUI...

[Sidebar with model selector and tools list]
[Chat area with message history]
[Input box at bottom]
```

**TUI Features:**
- 🎨 Modern interface with sidebar
- 🤖 Model selector dropdown
- 🛠️ Tools information panel
- 💬 Chat history with markdown
- ⌨️ Keyboard shortcuts (Ctrl+L to clear, Ctrl+C to quit)

### Model Management

```bash
# List all configured models
tide models

# Output:
# 🤖 Configured Models
# ┌──────────┬─────────────────────────────────────┐
# │ Alias    │ Model                               │
# ├──────────┼─────────────────────────────────────┤
# │▶ nanbeige│ Edge-Quant Nanbeige 4.1 3B (2.4GB)  │  ← Default
# │  llama3.1│ Llama 3.1 8B (4.9GB)                │
# │  qwen3   │ Qwen 3 Latest                       │
# └──────────┴─────────────────────────────────────┘

# Set default model
tide models --set nanbeige    # Fast, efficient (2.4GB)
tide models --set llama3.1    # Higher quality (4.9GB)
tide models --set qwen3       # Latest generation

# Use specific model for one command
tide -m nanbeige chat
tide -m llama3.1 ask "analyze this code"
```

### CLI Chat Mode

```bash
$ tide chat
🌊 Tide OS v3.0.0
Connected to: hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M
➜ List all Python files
🔧 Using tool: glob
... (output) ...

➜ model llama3.1    # Switch model
✓ Switched to llama3.1
```

### One-shot Commands

```bash
tide ask "view tide/cli.py"
tide -m nanbeige ask "grep 'def main' --path src"
```

### List Tools

```bash
tide tools
```

### Show Config

```bash
tide show-config
```

## ⚙️ Configuration

Tide looks for configuration in this priority order:

1. `.tide.json` (hidden, current directory)
2. `tide.json` (current directory)
3. `~/.config/tide/config.json` (global)
4. Built-in defaults

### Default Models

| Alias | Model | Size | Speed | Description |
|-------|-------|------|-------|-------------|
| **nanbeige** | `hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M` | 2.4GB | ⚡ Fast | Default - Efficient & fast |
| llama3.1 | `llama3.1:8b` | 4.9GB | 🚀 Medium | Higher quality |
| qwen3 | `qwen3:latest` | Variable | 🚀 Medium | Latest generation |

### Example `tide.json`

```json
{
  "model": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
  "ollama": {
    "host": "http://localhost:11434",
    "timeout": 120,
    "stream": true
  },
  "models": {
    "nanbeige": {
      "name": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
      "description": "Edge-Quant Nanbeige 4.1 3B - Fast & Efficient",
      "size": "2.4 GB",
      "speed": "fast"
    },
    "llama3.1": {
      "name": "llama3.1:8b",
      "description": "Llama 3.1 8B - High Quality",
      "size": "4.9 GB",
      "speed": "medium"
    }
  },
  "tools": {
    "bash": {
      "require_confirmation": true,
      "timeout": 30
    }
  }
}
```

## 🏗️ Architecture

```
tide/
├── __init__.py          # Package initialization
├── cli.py               # Rich-based CLI
├── agent.py             # AI Agent with tool calling
├── config.py            # Configuration management
├── models/
│   └── ollama.py        # Ollama client
├── tools/
│   ├── base.py          # Tool base classes
│   ├── registry.py      # Tool registry
│   ├── filesystem.py    # File operations
│   ├── system.py        # System operations
│   └── code.py          # Code analysis
└── ui/                  # UI components
```

## 🔄 Comparison with Crush

| Feature | Crush (Go) | Tide OS (Python) |
|---------|------------|------------------|
| Multi-provider | ✅ Many APIs | ✅ Ollama (local) |
| Tools | ✅ 10+ | ✅ 11 |
| Sessions | ✅ | ✅ |
| **Modern TUI** | ✅ Bubble Tea | ✅ **Textual** |
| **Model Management** | ✅ | ✅ **Built-in** |
| Streaming | ✅ | ✅ |
| LSP | ✅ | 🚧 Planned |
| MCP | ✅ | 🚧 Planned |
| Cost | Paid APIs | **Free (local)** |
| Privacy | Cloud | **Local** |

## 🤝 Contributing

```bash
# Setup development environment
git clone <repository-url>
cd tide-os
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black tide/
ruff check tide/
```

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

Inspired by [charmbracelet/crush](https://github.com/charmbracelet/crush).

---

**🌊 Tide OS - Code smarter, locally.**
