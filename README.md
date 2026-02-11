# Tide OS

A lightweight Linux distribution with an offline-first AI coding assistant.

## Overview

Tide OS Lite is a minimal Linux distribution that comes preinstalled with:
- **Tide CLI**: An AI-powered coding assistant that works fully offline
- **Ollama**: Local LLM inference server
- **Nemotron 3 Nano**: Default offline language model

No cloud API keys required. No internet connection needed after initial setup.

## Components

### tide-cli
A rebranded and customized coding agent CLI based on the [pi coding agent](https://github.com/badlogic/pi-mono), preconfigured for offline use with Ollama.

See: [tide-cli/](tide-cli/)

### packaging
Installation scripts and configuration for Tide OS Lite.

See: [packaging/](packaging/)

## Quick Start

### Option 1: Tide OS Lite ISO (Recommended)
1. Download the ISO
2. Boot from ISO (live or install)
3. Run `tide` to start chatting with your AI assistant

### Option 2: Install on existing Linux
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the default model
ollama pull nemotron-3-nano:latest

# Install Tide CLI
npm install -g @tide/tide-cli

# Run
tide
```

## Features

- **Fully Offline**: Works without internet after model download
- **Safe**: Tools require confirmation before making changes
- **Session Management**: Resume conversations, branch history
- **Extensible**: Skills, prompt templates, themes, extensions
- **Lightweight**: Minimal resource usage, runs on 16GB RAM

## Requirements

- RAM: 16GB minimum (with swap)
- Storage: 10GB+ for OS and models
- CPU: x86_64 processor

## Documentation

- [Overall Plan](PLAN_OVERALL_TIDE.md)
- [2-Day Execution Plan](PLAN_12_13_FEB_TIDE.md)
- [Progress Summary](PROGRESS_SUMMARY.md)

## License

MIT

## Attribution

Tide CLI is based on the [pi coding agent](https://github.com/badlogic/pi-mono) by Mario Zechner, licensed under MIT.

---

**Tide OS** - Your offline AI coding companion.
