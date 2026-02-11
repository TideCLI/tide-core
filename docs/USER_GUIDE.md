# Tide OS - User Guide

## Introduction

Welcome to Tide OS! This guide will help you get started with the AI-powered Linux distribution.

## Installation

### Method 1: Install on Existing Linux (Recommended for Demo)

```bash
# Download and run the installer
curl -fsSL https://your-repo/install-tide-os.sh | sudo bash

# Or run locally
cd /home/snoozescript/tide-os
sudo bash install-tide-os.sh
```

### Method 2: Manual Setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama
ollama serve

# 3. Pull a model
ollama pull llama3.1:8b

# 4. Run Tide CLI
python3 /home/snoozescript/tide-os/tide-py/tide.py
```

## Quick Start

### Check System Health
```bash
tide-doctor
```

Expected output:
```
╔═══════════════════════════════════════╗
║      Tide OS - Health Check           ║
╚═══════════════════════════════════════╝

1. Ollama Service
   ✅ Ollama is running

2. Ollama API
   ✅ API responding on port 11434

3. Models
   ✅ Installed models:
      - llama3.1:8b

4. Tide Configuration
   ✅ Config directory exists

═══════════════════════════════════════
✅ All systems operational!
Run 'tide' to start the AI assistant!
═══════════════════════════════════════
```

## Using Tide CLI

### Interactive Mode
```bash
tide
```

Start a conversation with the AI. Type your questions and get responses.

**Commands in interactive mode**:
- `/help` - Show available commands
- `/models` - List installed models
- `/clear` - Clear the screen
- `exit` or `quit` - Exit the program

### Single Prompt Mode
```bash
tide "Your question here"
```

Example:
```bash
tide "Explain the difference between Python and JavaScript"
```

## Features

### 1. Shell Command Assistant

Generate shell commands from natural language:

```bash
tide --shell "find all files modified in the last 24 hours"
```

Output:
```
Suggested command:
  find . -mtime -1 -type f

Execute? (y/n): y
[Command executes...]
```

### 2. Code Explanation

Explain code or commands:

```bash
tide --explain "ls -la | grep .txt"
```

Output:
```
Explanation:

This command lists all files in the current directory in long format
and filters for lines containing ".txt":

- ls -la: List all files (-a) in long format (-l)
- |: Pipe output to next command
- grep .txt: Filter for lines containing ".txt"
```

### 3. Code Generation

Generate code in any language:

```bash
tide --write "function to calculate fibonacci" --language python
```

Output:
```python
def fibonacci(n):
    """Calculate fibonacci sequence up to n numbers"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
```

### 4. Model Management

List installed models:
```bash
tide --models
```

Pull a new model:
```bash
tide --pull mistral:latest
```

Use a specific model:
```bash
tide --model qwen3:latest "Your question"
```

## Available Models

| Model | Best For | Size |
|-------|----------|------|
| llama3.1:8b | General purpose | 4.7 GB |
| qwen3:latest | Coding, reasoning | 4.0 GB |
| glm-4.7-flash | Fast responses | 3.2 GB |
| deepseek-coder | Code generation | 4.5 GB |
| mistral:latest | Balanced performance | 4.1 GB |

## Tips and Tricks

### 1. Getting Better Responses

Be specific in your prompts:
- ❌ "Help with Python"
- ✅ "Write a Python function to parse JSON with error handling"

### 2. Context in Interactive Mode

The AI remembers conversation context in interactive mode. You can refer to previous messages:
```
You: Write a Python function to add two numbers
Tide: [Provides code]
You: Now modify it to handle strings too
Tide: [Updates code with string handling]
```

### 3. Shell Command Safety

Generated commands require confirmation before execution. Review them carefully!

### 4. Offline Usage

Tide OS works completely offline after initial model download. No internet required!

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama manually
ollama serve

# Or as a service
sudo systemctl start ollama
```

### No Models Found

```bash
# Pull default model
ollama pull llama3.1:8b

# Verify installation
ollama list
```

### Slow Responses

1. Use a smaller model: `glm-4.7-flash`
2. Close other applications
3. Check available RAM: `free -h`

### API Connection Error

```bash
# Check if Ollama is listening
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

## Configuration

### Change Default Model

Edit `~/.tide/config.json`:
```json
{
    "default_model": "your-preferred-model"
}
```

### Environment Variables

```bash
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export TIDE_DEFAULT_MODEL=llama3.1:8b
```

## Advanced Usage

### Scripting with Tide

```bash
#!/bin/bash
# Example: Generate commit messages

changes=$(git diff --stat)
message=$(tide "Write a git commit message for these changes: $changes")
git commit -m "$message"
```

### Batch Processing

```bash
# Process multiple files
for file in *.py; do
    tide --explain "$file" > "${file}.explain.txt"
done
```

## Security Notes

1. **Local Processing**: All AI runs locally - your data never leaves your machine
2. **Command Confirmation**: Potentially dangerous commands require your approval
3. **Model Files**: Downloaded models are stored in `~/.ollama/models/`

## Getting Help

1. Run `tide --help` for command options
2. Run `tide-doctor` to check system status
3. Check logs: `journalctl -u ollama`

## Updates

To update Tide OS:
```bash
cd /home/snoozescript/tide-os
git pull
sudo bash install-tide-os.sh
```

---

**Version**: 1.0  
**Last Updated**: February 2026
