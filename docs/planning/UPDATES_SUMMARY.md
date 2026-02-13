# 🌊 Tide OS Updates - Models & Modern TUI

## Summary of Changes

### 1. Added 3 Pre-configured Models

| Alias | Model | Size | Speed | Default |
|-------|-------|------|-------|---------|
| **nanbeige** | `hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M` | 2.4 GB | ⚡ Fast | ✅ Yes |
| llama3.1 | `llama3.1:8b` | 4.9 GB | 🚀 Medium | No |
| qwen3 | `qwen3:latest` | Variable | 🚀 Medium | No |

**Default Model:** Edge-Quant Nanbeige 4.1 3B - Fast & Efficient

### 2. Model Management System

```bash
# List all models with details
tide models

# Set default model
tide models --set nanbeige
tide models --set llama3.1
tide models --set qwen3

# Use specific model for one command
tide -m nanbeige chat
tide --model llama3.1 ask "analyze code"

# Switch models in chat
➜ model nanbeige
✓ Switched to nanbeige
```

### 3. Modern TUI (Textual)

New `tide/ui/app.py` with:
- 🎨 Modern sidebar interface
- 🤖 Model selector dropdown
- 🛠️ Tools information panel
- 💬 Chat history with markdown rendering
- ⏳ Loading indicators
- ⌨️ Keyboard shortcuts
- 📊 Responsive layout

**Launch TUI:**
```bash
tide              # Default - launches TUI
tide tui          # Explicit TUI launch
tide chat         # CLI mode
```

### 4. Updated Commands

| Command | Description |
|---------|-------------|
| `tide` | Launch TUI (default) |
| `tide -m nanbeige` | Use specific model |
| `tide tui` | Launch modern TUI |
| `tide chat` | CLI chat mode |
| `tide models` | List & manage models |
| `tide models --set X` | Set default model |
| `tide tools` | List tools |
| `tide show-config` | Show configuration |
| `tide ask "..."` | One-shot query |

### 5. Configuration Updates

`config/tide.json` now includes:
```json
{
  "model": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
  "models": {
    "nanbeige": {
      "name": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
      "description": "Edge-Quant Nanbeige 4.1 3B - Fast & Efficient (2.4GB)",
      "size": "2.4 GB",
      "speed": "fast"
    },
    "llama3.1": { ... },
    "qwen3": { ... }
  }
}
```

### 6. Dependencies Added

```toml
dependencies = [
    "click>=8.0.0",
    "rich>=13.0.0",
    "requests>=2.28.0",
    "textual>=0.45.0",  # NEW for TUI
]
```

## File Changes

### New Files
- `tide/ui/app.py` - Modern TUI application (~275 lines)

### Modified Files
- `tide/cli.py` - Added TUI command, model management
- `tide/config.py` - Added model management methods
- `config/tide.json` - Added 3 model configurations
- `pyproject.toml` - Added textual dependency
- `README.md` - Updated documentation

## Usage Examples

### Quick Start
```bash
# Pull the models
ollama pull hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M
ollama pull llama3.1:8b
ollama pull qwen3:latest

# Launch TUI (uses nanbeige by default)
tide

# Use different model
tide -m llama3.1

# List and manage models
tide models
tide models --set llama3.1
```

### Model Speed Comparison

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| nanbeige | 2.4GB | ⚡ Fast | Quick tasks, efficiency |
| llama3.1 | 4.9GB | 🚀 Medium | Higher quality responses |
| qwen3 | Variable | 🚀 Medium | Latest features |

## Performance

- **Nanbeige 3B**: ~2x faster than Llama 3.1 8B
- **Memory usage**: ~3GB for nanbeige vs ~6GB for llama3.1
- **Quality**: Llama 3.1 8B produces more detailed responses

## Next Steps

The TUI can be further enhanced with:
- [ ] Session persistence
- [ ] Message search
- [ ] Theme customization
- [ ] Split-pane file viewer
- [ ] Syntax highlighting in chat
- [ ] Streaming responses
