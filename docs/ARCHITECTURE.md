# Tide OS Architecture

## Overview

Tide OS is built with a clean, modular architecture inspired by [charmbracelet/crush](https://github.com/charmbracelet/crush). The design prioritizes:

- **Modularity**: Clear separation of concerns
- **Extensibility**: Easy to add new tools and models
- **Safety**: Confirmation prompts for dangerous operations
- **Configurability**: File-based configuration with sensible defaults

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                    (click + rich)                            │
├─────────────────────────────────────────────────────────────┤
│                        Agent Layer                           │
│              (session management, tool calling)              │
├─────────────────────────────────────────────────────────────┤
│                      Tools Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Filesystem│ │  System  │ │   Code   │ │ Registry │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│                      Models Layer                            │
│                    (Ollama client)                           │
├─────────────────────────────────────────────────────────────┤
│                     Config Layer                             │
│              (JSON-based configuration)                      │
└─────────────────────────────────────────────────────────────┘
```

## Module Details

### 1. CLI (`tide/cli.py`)

- Entry point for all user interactions
- Built with `click` for argument parsing
- `rich` for beautiful terminal output
- Commands: `chat`, `tools`, `config`, `models`, `ask`

### 2. Agent (`tide/agent.py`)

- Manages conversation sessions
- Handles tool calling logic
- Parses LLM responses for tool invocations
- Maintains conversation history

### 3. Tools (`tide/tools/`)

#### Base (`base.py`)
- Abstract `Tool` class with validation
- `Parameter` dataclass for type checking
- `ToolResult` for standardized output
- `ToolContext` for passing configuration

#### Registry (`registry.py`)
- Central tool management
- Tool discovery and execution
- Global registry instance

#### Filesystem (`filesystem.py`)
- `ViewTool`: Read files with line numbers
- `LsTool`: Tree directory listing
- `EditTool`: File editing with diff preview
- `WriteTool`: Create new files
- `GlobTool`: Pattern-based file finding

#### System (`system.py`)
- `BashTool`: Shell execution with safety controls
- `PythonTool`: Restricted Python execution
- `ReadTool`: Quick file reading

#### Code (`code.py`)
- `GrepTool`: Pattern searching
- `AnalyzeTool`: AST-based code analysis
- `TodosTool`: Find TODO/FIXME markers

### 4. Models (`tide/models/`)

#### Ollama (`ollama.py`)
- HTTP client for Ollama API
- Chat completions
- Model listing
- Streaming support (planned)

### 5. Config (`tide/config.py`)

- Priority-based config loading
- Dot-notation access (`config.get('tools.bash.timeout')`)
- Deep merging of configs
- Default values

## Data Flow

```
User Input
    │
    ▼
┌─────────┐
│   CLI   │
└────┬────┘
     │
     ▼
┌─────────┐
│  Agent  │
└────┬────┘
     │
     ├────────────┐
     ▼            ▼
┌─────────┐  ┌─────────┐
│  Tools  │  │  LLM    │
└────┬────┘  └────┬────┘
     │            │
     └──────┬─────┘
            ▼
      Tool Results
            │
            ▼
      ┌─────────┐
      │  LLM    │ (Final response)
      └────┬────┘
           ▼
      User Output
```

## Tool Execution Flow

1. **Parse**: Agent detects tool call in LLM response
2. **Validate**: Tool validates parameters
3. **Confirm**: If `require_confirmation`, prompt user
4. **Execute**: Run tool logic
5. **Return**: Send result back to LLM
6. **Respond**: LLM generates final response

## Configuration Priority

1. `.tide.json` (project-specific, hidden)
2. `tide.json` (project-specific)
3. `~/.config/tide/config.json` (user global)
4. Built-in defaults

## Security Model

- **Banned Commands**: Bash tool blocks dangerous patterns
- **Timeouts**: All operations have timeouts
- **Confirmation**: Destructive operations require user confirmation
- **Path Validation**: Working directory restrictions

## Extension Points

### Adding a New Tool

```python
from tide.tools import Tool, ToolResult, register_tool, Parameter, ParameterType

@register_tool
class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    category = "custom"
    
    parameters = {
        "arg": Parameter(
            name="arg",
            type=ParameterType.STRING,
            description="An argument",
            required=True
        )
    }
    
    def _execute(self, arg: str) -> ToolResult:
        return ToolResult.success_result(f"Result: {arg}")
```

### Adding a New Model Provider

1. Create client in `tide/models/`
2. Implement same interface as `OllamaClient`
3. Update `Agent` to support multiple providers

## Design Decisions

### Why Click + Rich?

- **Click**: Standard CLI framework, good help generation
- **Rich**: Best-in-class terminal output, tables, panels, syntax highlighting

### Why Ollama First?

- Local execution = privacy
- No API costs
- Works offline
- Easy setup

### Why Tool Classes?

- Self-documenting through `get_schema()`
- Validation built-in
- Easy to register/discover
- Type-safe

## Future Improvements

- [ ] LSP integration (like crush)
- [ ] MCP support
- [ ] Streaming responses
- [ ] Multi-provider support
- [ ] Plugin system
- [ ] Session persistence
