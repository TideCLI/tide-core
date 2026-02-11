# Tide OS - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Commands](#basic-commands)
3. [Interactive Mode](#interactive-mode)
4. [Shell Assistant](#shell-assistant)
5. [Code Tools](#code-tools)
6. [Advanced Features](#advanced-features)
7. [Tips & Tricks](#tips--tricks)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Time Setup
```bash
# Check if everything is working
tide-doctor

# You should see:
# ✅ Ollama is running
# ✅ API responding
# ✅ Models installed
# ✅ Config valid
```

### Your First Query
```bash
# Single prompt mode
tide "What is artificial intelligence?"

# The AI will respond with an explanation
```

---

## Basic Commands

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `tide` | Start interactive chat | `tide` |
| `tide "prompt"` | Single prompt | `tide "Explain Linux"` |
| `tide --doctor` | Health check | `tide-doctor` |
| `tide --models` | List models | `tide --models` |
| `tide --shell "desc"` | Generate command | `tide --shell "find files"` |
| `tide --explain "cmd"` | Explain command | `tide --explain "ls -la"` |
| `tide --write "desc"` | Generate code | `tide --write "sort array" -l python` |
| `tide --pull model` | Download model | `tide --pull mistral` |
| `tide --model name` | Use specific model | `tide --model qwen3 "prompt"` |

### Getting Help
```bash
# Show all options
tide --help

# Show version
tide --version
```

---

## Interactive Mode

### Starting Interactive Mode
```bash
tide
```

You'll see:
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗       ║
║        ... Tide OS Logo ...                               ║
╚═══════════════════════════════════════════════════════════╝

Model: llama3.1:8b
Type 'exit', 'quit', or press Ctrl+C to exit

Commands:
  /help    - Show help
  /models  - List models
  /clear   - Clear screen

You: 
```

### Interactive Commands

#### /help
Shows all available commands in interactive mode.

#### /models
Lists all installed Ollama models with sizes.

#### /clear
Clears the terminal screen.

#### /code <language>
Switches to coding mode for specific language.
```
You: /code python
Tide: Switched to python coding mode. Describe what you want to build:
```

#### /shell
Gets help with shell commands.
```
You: /shell
Tide: Describe what you want to do, and I'll give you the shell command:
```

### Example Interactive Session
```
You: Hello!
Tide: Hello! How can I help you today?

You: Write a Python function to calculate factorial
Tide: Here's a Python function to calculate factorial:

def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

You: Now add error handling
Tide: [Updates code with error handling]

You: exit
Tide: Goodbye! 👋
```

---

## Shell Assistant

### Generate Shell Commands

#### Basic Usage
```bash
tide --shell "description of what you want to do"
```

#### Examples

**Find files:**
```bash
$ tide --shell "find all Python files modified today"

Suggested command:
  find . -name "*.py" -mtime -1

Execute? (y/n): y
[command runs]
```

**System info:**
```bash
$ tide --shell "show disk usage for all directories"

Suggested command:
  du -h --max-depth=1 | sort -h

Execute? (y/n): y
```

**Docker:**
```bash
$ tide --shell "remove all stopped docker containers"

Suggested command:
  docker container prune -f

Execute? (y/n): n  # Be careful with destructive commands!
```

### Safety Features
- Commands require confirmation before execution
- Review carefully before typing 'y'
- Dangerous commands can be cancelled with 'n'

---

## Code Tools

### Code Explanation

#### Explain Commands
```bash
tide --explain "ls -la | grep .txt | wc -l"
```

Output:
```
This command:
1. Lists all files in long format (-la)
2. Filters for lines containing .txt
3. Counts the number of lines (wc -l)

Result: Count of .txt files in current directory
```

#### Explain Code
```bash
tide --explain "for i in {1..10}; do echo $i; done"
```

### Code Generation

#### Basic Syntax
```bash
tide --write "description" --language <language>
```

#### Python Examples

**Function:**
```bash
tide --write "function to read CSV file" --language python
```

**Class:**
```bash
tide --write "class for managing student records with add, delete, list methods" --language python
```

**Algorithm:**
```bash
tide --write "binary search implementation" --language python
```

#### JavaScript Examples
```bash
tide --write "fetch API wrapper with error handling" --language javascript
tide --write "React component for login form" --language javascript
tide --write "function to debounce input" --language javascript
```

#### Other Languages
```bash
tide --write "bash script to backup files" --language bash
tide --write "SQL query to find duplicates" --language sql
tide --write "C function to reverse string" --language c
tide --write "Java class for calculator" --language java
```

---

## Advanced Features

### Using Different Models

#### List Available Models
```bash
tide --models
```

#### Switch Models
```bash
# Use specific model for one query
tide --model qwen3:latest "complex coding question"

# Use smaller model for faster responses
tide --model glm-4.7-flash:latest "quick question"
```

#### Download New Models
```bash
tide --pull mistral:latest
tide --pull codellama:latest
tide --pull llama3.2:latest
```

### Environment Variables

```bash
# Change Ollama host
export OLLAMA_HOST=192.168.1.100

# Change port
export OLLAMA_PORT=11435

# Set default model
export TIDE_DEFAULT_MODEL=qwen3:latest
```

### Configuration File

Location: `/etc/tide/config.json`

```json
{
    "version": "1.0.0",
    "default_model": "llama3.1:8b",
    "ollama_host": "localhost",
    "ollama_port": 11434
}
```

---

## Tips & Tricks

### Getting Better Responses

#### Be Specific
❌ Bad: "Help with Python"
✅ Good: "Write a Python function to parse JSON with error handling"

#### Provide Context
❌ Bad: "Fix this"
✅ Good: "This Python function crashes on empty input. How to fix it? [paste code]"

#### Ask for Examples
```
You: Show me 3 ways to reverse a list in Python
```

### Productivity Shortcuts

#### Bash Alias
Add to `~/.bashrc`:
```bash
alias ai='tide'
alias ask='tide'
alias how='tide --shell'
alias explain='tide --explain'
```

Then use:
```bash
ai "what is Docker?"
how "compress a folder"
explain "grep -r pattern ."
```

#### Function for Common Tasks
Add to `~/.bashrc`:
```bash
# Git commit message generator
gcommit() {
    msg=$(tide "Write a git commit message for: $(git diff --stat)" 2>/dev/null)
    git commit -m "$msg"
}

# Code reviewer
creview() {
    tide --explain "$(cat $1)"
}
```

### Working Offline

**Verify offline operation:**
```bash
# Disconnect Wi-Fi/Ethernet
# Then run:
tide "Explain how neural networks work"
# Should work perfectly!
```

**Pre-download models for offline use:**
```bash
# While connected, pull multiple models
ollama pull llama3.1:8b
ollama pull qwen3:latest
ollama pull glm-4.7-flash:latest

# Now you can work offline with any of these
```

---

## Troubleshooting

### Common Issues

#### "Ollama not running"
```bash
# Start Ollama
sudo systemctl start ollama

# Enable auto-start
sudo systemctl enable ollama

# Check status
sudo systemctl status ollama
```

#### "No models found"
```bash
# Pull a model
ollama pull llama3.1:8b

# Verify
ollama list
```

#### "Connection refused"
```bash
# Check if Ollama is listening
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

#### Slow responses
```bash
# Check RAM usage
free -h

# Use smaller/faster model
tide --model glm-4.7-flash "prompt"

# Close other applications
```

#### Command not found
```bash
# Check installation
ls -la /usr/local/bin/tide

# Reinstall if needed
cd /home/snoozescript/tide-os
sudo bash install-tide-os.sh
```

### Debug Mode

```bash
# Run with verbose output
python3 /opt/tide/cli/tide.py --doctor
```

### Reset Configuration

```bash
# Remove user config
rm -rf ~/.tide

# Remove system config
sudo rm /etc/tide/config.json

# Reinstall
sudo bash /home/snoozescript/tide-os/install-tide-os.sh
```

---

## Command Cheat Sheet

```bash
# ===== BASIC =====
tide                          # Interactive mode
tide "question"               # Single prompt
tide --help                   # Show help

# ===== SYSTEM =====
tide-doctor                   # Health check
tide --models                 # List models
tide --pull modelname         # Download model

# ===== SHELL =====
tide --shell "description"    # Generate command
tide --explain "command"      # Explain command

# ===== CODE =====
tide --write "description" -l python    # Generate Python
tide --write "description" -l javascript # Generate JS
tide --explain "code"         # Explain code

# ===== MODELS =====
tide --model modelname "prompt"  # Use specific model
tide --models                 # List available
ollama list                   # Ollama's list
ollama pull name              # Pull model
ollama rm name                # Remove model
```

---

## Next Steps

1. **Practice** with different prompts
2. **Customize** your bash aliases
3. **Explore** different models
4. **Build** scripts using tide
5. **Share** with your team

---

**Happy Coding with Tide OS!** 🌊
