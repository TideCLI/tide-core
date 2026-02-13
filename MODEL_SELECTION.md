# 🤖 Tide OS - Model Selection Support

## Overview

Tide OS now supports **multiple AI models** from Ollama! You can choose the best model for your needs.

## Supported Models

| Model | Size | Best For | Status |
|-------|------|----------|--------|
| **llama3.1:8b** | 4.9 GB | Coding, large context | ⭐ Recommended |
| **qwen3:latest** | 4-8 GB | Code generation, reasoning | ⭐ Recommended |
| **codellama:latest** | 4-8 GB | Code completion, debugging | ⭐ Recommended |
| **llama3:latest** | 4-8 GB | General purpose | ✅ Available |
| **mistral:latest** | 4-5 GB | Fast, efficient | ✅ Available |
| **phi3:latest** | 2-4 GB | Compact, laptops | ✅ Available |

## How to Use

### 1. List Available Models

```bash
# Show installed and recommended models
tide-v2 --models

# Or in Docker
docker run tide-os:latest tide-models
```

Output:
```
🤖 Available AI Models

📦 Installed Models:
  1. llama3.1:8b
     Name: Llama 3.1 (8B)
     Description: Best coding performance, large context window
     Size: 4.9 GB

⭐ Recommended Models (Install with 'ollama pull <model>'):
  • qwen3:latest
    Excellent code generation and reasoning
    Size: 4-8 GB
```

### 2. Interactive Model Selection

```bash
# Select model interactively
tide-v2 --select-model

# Shows menu:
# 🤖 Select AI Model for Tide OS
# 
# 📦 Installed Models:
#   1. llama3.1:8b (Llama 3.1 8B)
#   2. qwen3:latest (Qwen 3)
# 
# Select model (1-2) or enter model name [1]:
```

### 3. Specify Model Directly

```bash
# Use specific model
tide-v2 --model llama3.1:8b "analyze code"

# Or with environment variable
TIDE_MODEL=llama3.1:8b tide-v2
```

### 4. Set Default in Config

Edit `tide.json`:
```json
{
  "model": "llama3.1:8b",
  "ollama": {
    "host": "http://localhost:11434"
  }
}
```

## Docker with Model Selection

### Build with Specific Model

```bash
# Build with llama3.1:8b (default)
docker build -t tide-os:latest .

# Build with different model
docker build --build-arg MODEL=qwen3:latest -t tide-os:qwen3 .

# Build with codellama
docker build --build-arg MODEL=codellama:latest -t tide-os:codellama .
```

### Run with Model Selection

```bash
# Run and select model interactively
docker run -it tide-os:latest tide-v2 --select-model

# Run with specific model
docker run -it -e TIDE_MODEL=llama3.1:8b tide-os:latest tide-chat
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `tide-v2 --models` | List all available models |
| `tide-v2 --select-model` | Interactive model selection |
| `tide-v2 --model <name>` | Use specific model |
| `tide-models` | Alias for --models |
| `ollama list` | Show installed Ollama models |
| `ollama pull <model>` | Download new model |

## Configuration Priority

1. **Command line**: `--model llama3.1:8b`
2. **Environment**: `TIDE_MODEL=llama3.1:8b`
3. **Config file**: `tide.json` → `"model": "llama3.1:8b"`
4. **Default**: `qwen3:latest`

## Example Workflows

### Switch Between Models

```bash
# Check available models
tide-v2 --models

# Select interactively
tide-v2 --select-model
# Selected: llama3.1:8b

# Now use it
tide-v2 "analyze this code"
# Using model: llama3.1:8b
```

### Docker with Multiple Models

```bash
# Build different versions
docker build --build-arg MODEL=llama3.1:8b -t tide-os:llama .
docker build --build-arg MODEL=codellama:latest -t tide-os:code .
docker build --build-arg MODEL=qwen3:latest -t tide-os:qwen3 .

# Run specific version
docker run -it tide-os:llama tide-chat
docker run -it tide-os:code tide-chat
```

### For Different Use Cases

```bash
# Coding focus
tide-v2 --model codellama:latest "fix this bug"

# General tasks
tide-v2 --model llama3.1:8b "explain this code"

# Fast responses
tide-v2 --model phi3:latest "quick question"
```

## Model Recommendations

### For Final Year Project
- **llama3.1:8b** (4.9 GB) - Best overall performance ⭐
- Already installed on your system!

### For Different Tasks
- **Code-heavy work**: codellama:latest
- **General questions**: llama3.1:8b or llama3:latest
- **Limited resources**: phi3:latest (2-4 GB)
- **Multilingual**: qwen3:latest

## Integration with Existing Features

Model selection works with all Tide features:
- ✅ All 15 tools
- ✅ Interactive chat mode
- ✅ File analysis
- ✅ Code editing
- ✅ Docker deployment
- ✅ ISO build

## Testing

```bash
# Test model selection
cd /home/snoozescript/tide-os

# List models
python3 tide-v2.py --models

# Select interactively
python3 tide-v2.py --select-model

# Use specific model
python3 tide-v2.py --model llama3.1:8b --tools

# Build Docker with your model
docker build --build-arg MODEL=llama3.1:8b -t tide-os:latest .
```

## Status

✅ **Model selection fully implemented!**

- Interactive selection
- Multiple model support
- Docker ARG support
- Environment variable support
- Config file support
- Command-line support

**Ready for use!** 🌊🤖
