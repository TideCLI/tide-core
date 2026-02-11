# Tide CLI

Offline-first AI coding assistant with read, bash, edit, write tools. Built for Tide OS Lite.

## Overview

Tide CLI is a rebranded and customized version of the [pi coding agent](https://github.com/badlogic/pi-mono), preconfigured for **fully offline** use with Ollama and local models.

## Features

- **Fully offline**: Works without internet after initial model download
- **Default model**: Nemotron 3 Nano (optimized for offline use)
- **Safe tools**: read, bash, edit, write with confirmation
- **Session management**: Resume conversations, branch history
- **Extensible**: Skills, prompt templates, themes, extensions

## Quick Start

### Prerequisites

1. Install Ollama: https://ollama.ai
2. Pull the default model:
   ```bash
   ollama pull nemotron-3-nano:latest
   ```

### Installation

```bash
# From npm (when published)
npm install -g @tide/tide-cli

# Or build from source
git clone <your-repo>
cd tide-cli
npm install
npm run build
npm link
```

### Usage

```bash
# Start interactive session
tide

# Ask a question
tide "List all .ts files in src/"

# Include files
tide @README.md "Summarize this file"

# Non-interactive mode
tide -p "What is the purpose of this codebase?"

# Continue previous session
tide --continue

# Use different model
tide --provider ollama --model llama3.1:8b
```

## Configuration

Tide CLI stores configuration in `~/.tide/agent/`:

- `models.json` - Custom model definitions (Ollama preconfigured)
- `settings.json` - User preferences
- `sessions/` - Conversation history

### Default Models

The default `models.json` includes these Ollama models:

| Model ID | Name | Context | Max Output |
|----------|------|---------|------------|
| `nemotron-3-nano:latest` | Nemotron 3 Nano (Offline) | 4K | 2K |
| `llama3.1:8b` | Llama 3.1 8B (Offline) | 128K | 4K |
| `llama3.2:latest` | Llama 3.2 (Offline) | 128K | 4K |
| `qwen2.5-coder:7b` | Qwen 2.5 Coder 7B (Offline) | 32K | 4K |

To add more models, edit `~/.tide/agent/models.json`:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "your-model:latest" }
      ]
    }
  }
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/model` | Switch models |
| `/settings` | Configure preferences |
| `/resume` | Resume previous session |
| `/new` | Start new session |
| `/help` | Show all commands |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TIDE_CODING_AGENT_DIR` | Config directory (default: `~/.tide/agent`) |
| `OLLAMA_HOST` | Ollama server host (default: `http://localhost:11434`) |

## Tools

| Tool | Description |
|------|-------------|
| `read` | Read file contents |
| `bash` | Execute shell commands |
| `edit` | Make precise file edits |
| `write` | Create/overwrite files |
| `grep` | Search file contents |
| `find` | Find files by pattern |
| `ls` | List directory contents |

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Build standalone binary
npm run build:binary

# Run tests
npm test
```

## License

MIT

## Attribution

Tide CLI is based on the [pi coding agent](https://github.com/badlogic/pi-mono) by Mario Zechner.

This project rebrands and customizes pi for offline-first use with Ollama, as part of the Tide OS Lite project.

---

**Tide OS Lite** - A lightweight Linux distribution with Tide CLI + Ollama preinstalled for fully offline AI-assisted coding.
