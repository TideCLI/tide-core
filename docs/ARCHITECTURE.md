# Tide OS - Technical Architecture

## System Overview

Tide OS is an AI-powered Linux distribution that integrates local Large Language Models (LLMs) directly into the operating system. It provides offline-first AI capabilities through a command-line interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   tide CLI  │  │ tide-doctor │  │ Desktop Shortcuts   │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
└─────────┼───────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Tide CLI (Python)                      │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │  Chat    │ │  Shell   │ │  Code    │            │    │
│  │  │  Mode    │ │Assistant │ │  Tools   │            │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘            │    │
│  └───────┼────────────┼────────────┼────────────────────┘    │
└──────────┼────────────┼────────────┼─────────────────────────┘
           │            │            │
┌──────────▼────────────▼────────────▼─────────────────────────┐
│                    AI Services Layer                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Ollama API                        │    │
│  │              (localhost:11434)                      │    │
│  └─────────────────────────┬───────────────────────────┘    │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     Model Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Llama 3.1│  │   Qwen   │  │ GLM-4.7  │  │ DeepSeek │    │
│  │   8B     │  │   3      │  │  Flash   │  │   Coder  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Layer

**Tide CLI**: The main interface for interacting with AI
- Entry point: `tide` command
- Supports interactive and single-prompt modes
- Commands: chat, explain, shell, write, doctor, models

**Tide Doctor**: System health diagnostic tool
- Checks Ollama service status
- Verifies API connectivity
- Lists installed models
- Validates configuration

### 2. Application Layer

**Tide CLI (Python)**:
```python
# Core modules:
- tide.py          # Main entry point
- chat_mode        # Interactive conversation
- shell_assistant  # Command generation
- code_tools       # Code generation/explanation
- health_check     # System diagnostics
```

**Key Features**:
- HTTP client for Ollama API communication
- JSON parsing for model responses
- Colorized terminal output
- Session history management

### 3. AI Services Layer

**Ollama**:
- Local LLM inference server
- OpenAI-compatible API
- Default endpoint: `http://localhost:11434`
- Supports multiple model formats (GGUF)

**API Endpoints**:
```
GET  /api/tags      # List installed models
POST /api/generate  # Generate text completion
POST /api/chat      # Chat completion (alternative)
```

### 4. Model Layer

**Supported Models**:
| Model | Size | Use Case |
|-------|------|----------|
| llama3.1:8b | 4.7 GB | General purpose |
| qwen3:latest | 4.0 GB | Coding, reasoning |
| glm-4.7-flash | 3.2 GB | Fast responses |
| deepseek-coder | 4.5 GB | Code generation |

## Data Flow

### Single Prompt Flow:
```
User Input → tide CLI → Ollama API → LLM Model → Response → User
```

### Interactive Chat Flow:
```
User Input → tide CLI → History + Context → Ollama API → LLM → Response → Update History → User
```

### Shell Command Generation:
```
Description → tide CLI → Prompt Engineering → Ollama API → Command → User Confirmation → Execution
```

## Configuration

**System Config**: `/etc/tide/config.json`
```json
{
    "version": "1.0.0",
    "default_model": "llama3.1:8b",
    "ollama_host": "localhost",
    "ollama_port": 11434
}
```

**User Config**: `~/.tide/history.json`
- Conversation history
- User preferences

## Security Considerations

1. **Local-Only**: All AI processing happens locally
2. **No Cloud Dependencies**: No API keys or external services
3. **Sandboxed Models**: Ollama runs in isolated environment
4. **User Confirmation**: Shell commands require explicit approval

## Performance

**Requirements**:
- RAM: 16GB minimum (8GB + 8GB for model)
- Storage: 20GB (OS + models)
- CPU: x86_64 with AVX2 support

**Optimization**:
- Quantized models (4-bit) for faster inference
- Streaming responses for real-time feedback
- Session caching for context preservation

## Integration Points

**systemd Services**:
```
ollama.service      # Ollama inference server
tide-firstboot.service  # Initial setup
```

**Desktop Integration**:
- .desktop files for application menu
- Terminal profile with Tide branding
- MOTD (Message of the Day) on login

## Deployment Options

1. **Install Script**: Convert existing Linux to Tide OS
2. **Docker Container**: Containerized environment
3. **ISO Image**: Bootable installation medium
4. **VM Image**: Pre-configured virtual machine

## Future Architecture

```
┌─────────────────────────────────────────┐
│           GUI Layer (Future)            │
│    Electron + React Dashboard           │
└─────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Voice Interface (Future)        │
│      Whisper Speech-to-Text             │
└─────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Implemented
