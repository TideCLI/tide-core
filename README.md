# Tide OS: AI-Powered Linux Distribution

**Final Year Project - B.Tech Artificial Intelligence and Machine Learning**  
*Sanjay Ghodawat University, Kolhapur*

---

## 📋 Project Information

| | |
|---|---|
| **Students** | Aadil Shabbir Inamdar (Roll No. 65), Om Deepak Ghante (Roll No. 53) |
| **Supervisor** | Prof. Amrish Patil |
| **Department** | AIML, B.Tech B |
| **Year** | 2025-26 |

---

## 🎯 Project Overview

Tide OS is a next-generation Linux distribution that embeds Artificial Intelligence as a native, offline-capable feature. Unlike traditional operating systems that rely on cloud-based AI assistants, Tide OS integrates local Large Language Models (LLMs) directly into the system environment using Ollama.

### Key Features

- ✅ **Fully Offline**: Works without internet after initial setup
- ✅ **Privacy-First**: All AI processing happens locally
- ✅ **Shell Integration**: AI-powered command generation and explanation
- ✅ **Code Assistant**: Write and explain code in any language
- ✅ **System Diagnostics**: Built-in health check tools

---

## 🚀 Quick Start

### Prerequisites
- Linux system (Ubuntu/Debian/Arch)
- 16GB RAM (8GB for OS + 8GB for models)
- 20GB free storage

### Installation

```bash
# Clone the repository
cd /home/snoozescript/tide-os

# Run the installer
sudo bash install-tide-os.sh
```

### Verify Installation

```bash
# Check system health
tide-doctor

# List available models
tide --models

# Start using Tide
tide "Hello, what can you do?"
```

---

## 📖 Usage Examples

### 1. Interactive Chat
```bash
tide
```

### 2. Single Prompt
```bash
tide "Explain quantum computing"
```

### 3. Shell Command Generation
```bash
tide --shell "find files modified in last 24 hours"
```

### 4. Code Explanation
```bash
tide --explain "docker ps -a"
```

### 5. Code Generation
```bash
tide --write "function to sort an array" --language javascript
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  User Layer: tide CLI, tide-doctor, Desktop shortcuts   │
├─────────────────────────────────────────────────────────┤
│  Application Layer: Python CLI with HTTP client         │
├─────────────────────────────────────────────────────────┤
│  AI Services: Ollama API (localhost:11434)              │
├─────────────────────────────────────────────────────────┤
│  Models: Llama 3.1, Qwen, GLM, DeepSeek (Local GGUF)    │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
tide-os/
├── tide-py/               # Tide CLI (Python)
│   └── tide.py           # Main CLI implementation
├── packaging/            # OS integration scripts
│   ├── install_tide.sh   # Component installer
│   └── tide-firstboot.sh # First boot setup
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # Technical architecture
│   └── USER_GUIDE.md     # User manual
├── install-tide-os.sh    # Main OS installer
├── demo.sh               # Demo script
└── README.md             # This file
```

---

## 🎬 Demo

Run the complete demo:

```bash
bash demo.sh
```

Or test individual features:

```bash
cd tide-py

# Health check
python3 tide.py --doctor

# List models
python3 tide.py --models

# Ask a question
python3 tide.py "What is machine learning?"
```

---

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and technical details
- **[User Guide](docs/USER_GUIDE.md)** - Complete usage instructions
- **[Deliverables](FINAL_PROJECT_DELIVERABLES.md)** - Project deliverables checklist

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Base OS | Arch Linux / Ubuntu |
| AI Backend | Ollama (Local LLM inference) |
| CLI | Python 3 + http.client |
| Models | Llama 3.1, Qwen, GLM (GGUF format) |
| Integration | systemd, bash scripts |

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Tide CLI | ✅ Complete |
| Ollama Integration | ✅ Complete |
| Installation Script | ✅ Complete |
| Documentation | ✅ Complete |
| ISO Builder | 🔄 Partial |

---

## 🎓 For Evaluators

This project demonstrates:

1. **AI Integration at OS Level**: Native AI capabilities, not an add-on
2. **Local-First Architecture**: Privacy-preserving offline operation
3. **Developer-Centric Design**: Shell integration, code tools
4. **Explainability**: Transparent AI interactions

### Key Achievements
- ✅ Working AI-powered CLI
- ✅ Offline functionality verified
- ✅ Multiple model support
- ✅ System integration complete
- ✅ Documentation comprehensive

---

## 📄 License

MIT License - See individual component licenses for details.

---

## 🙏 Acknowledgments

- Inspired by [pi coding agent](https://github.com/badlogic/pi-mono) by Mario Zechner
- Powered by [Ollama](https://ollama.com) for local LLM inference
- Built on open-source Linux technologies

---

**Tide OS** - *Your offline AI coding companion*

*This project is submitted in partial fulfillment of the requirements for the degree of Bachelor of Technology in Artificial Intelligence and Machine Learning.*
