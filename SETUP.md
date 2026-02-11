# Tide OS - Complete Setup Guide

## Prerequisites

### Hardware Requirements
- **RAM**: 16GB minimum (8GB for OS + 8GB for AI models)
- **Storage**: 20GB free space
- **CPU**: x86_64 with AVX2 support
- **Internet**: Required for initial setup only

### Software Requirements
- Ubuntu 22.04/24.04 LTS or Arch Linux
- Python 3.10+
- curl, git
- sudo privileges

---

## Quick Start (5 minutes)

### Step 1: Navigate to Project
```bash
cd /home/snoozescript/tide-os
```

### Step 2: Run Setup Script
```bash
# Make script executable
chmod +x install-tide-os.sh

# Run installer
sudo ./install-tide-os.sh
```

### Step 3: Verify Installation
```bash
tide-doctor
```

Expected output: All systems showing ✅

### Step 4: Start Using Tide
```bash
# Interactive mode
tide

# Or single prompt
tide "Hello, what can you do?"
```

---

## Manual Setup (If Script Fails)

### Step 1: Install Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Step 2: Pull AI Models
```bash
# Pull default model (4.7GB)
ollama pull llama3.1:8b

# Pull additional models (optional)
ollama pull qwen3:latest
ollama pull glm-4.7-flash:latest
```

### Step 3: Install Tide CLI
```bash
# Create directories
sudo mkdir -p /opt/tide/cli
sudo mkdir -p /etc/tide

# Copy Tide CLI
sudo cp -r /home/snoozescript/tide-os/tide-py/* /opt/tide/cli/

# Create tide command
sudo tee /usr/local/bin/tide << 'EOF'
#!/bin/bash
python3 /opt/tide/cli/tide.py "$@"
EOF

sudo chmod +x /usr/local/bin/tide

# Create tide-doctor command
sudo tee /usr/local/bin/tide-doctor << 'EOF'
#!/bin/bash
python3 /opt/tide/cli/tide.py --doctor
EOF

sudo chmod +x /usr/local/bin/tide-doctor
```

### Step 4: Configure System
```bash
# Create config
cat > /tmp/config.json << 'EOF'
{
    "version": "1.0.0",
    "default_model": "llama3.1:8b",
    "ollama_host": "localhost",
    "ollama_port": 11434
}
EOF

sudo mv /tmp/config.json /etc/tide/config.json

# Setup MOTD
sudo tee /etc/update-motd.d/99-tide << 'EOF'
#!/bin/bash
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Welcome to Tide OS - AI-Powered Linux Distribution       ║"
echo "║                                                           ║"
echo "║  Commands:                                                ║"
echo "║    tide          - Start AI assistant                     ║"
echo "║    tide-doctor   - Check system health                    ║"
echo "║    ollama        - Manage AI models                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
EOF

sudo chmod +x /etc/update-motd.d/99-tide
```

---

## Verify Everything Works

### Test 1: Check Commands Exist
```bash
which tide
which tide-doctor
which ollama
```
All should return paths.

### Test 2: Run Health Check
```bash
tide-doctor
```
Should show all green checks.

### Test 3: List Models
```bash
tide --models
```
Should show installed models.

### Test 4: Test AI Response
```bash
tide "What is 2+2?"
```
Should return an answer.

### Test 5: Test Offline (Optional)
```bash
# Disconnect internet
# Run tide
tide "Explain Linux"
# Should still work!
```

---

## Troubleshooting

### Issue: "ollama: command not found"
```bash
# Fix: Add to PATH
export PATH=$PATH:/usr/local/bin

# Or reinstall
curl -fsSL https://ollama.com/install.sh | sh
```

### Issue: "tide: command not found"
```bash
# Fix: Check if in PATH
ls -la /usr/local/bin/tide

# If exists, reload shell
source ~/.bashrc

# Or run with full path
python3 /home/snoozescript/tide-os/tide-py/tide.py
```

### Issue: "Connection refused" to Ollama
```bash
# Check if Ollama is running
sudo systemctl status ollama

# Start if not running
sudo systemctl start ollama

# Or run manually
ollama serve &
```

### Issue: "No models found"
```bash
# Pull a model
ollama pull llama3.1:8b

# Verify
ollama list
```

### Issue: Slow responses
```bash
# Check available RAM
free -h

# Use smaller model
tide --model glm-4.7-flash "prompt"

# Or close other applications
```

---

## Post-Setup Configuration

### Change Default Model
```bash
# Edit config
sudo nano /etc/tide/config.json

# Change "default_model" to your preferred model
```

### Add Custom Models
```bash
# Pull new model
ollama pull mistral:latest

# Use with tide
tide --model mistral:latest "prompt"
```

### Create Desktop Shortcuts (GUI)
```bash
# Create desktop entry
cat > ~/.local/share/applications/tide.desktop << 'EOF'
[Desktop Entry]
Name=Tide AI Terminal
Exec=gnome-terminal -- tide
Type=Application
Terminal=false
Icon=utilities-terminal
Categories=System;TerminalEmulator;
EOF
```

---

## Next Steps

1. **Run Demo Script**
   ```bash
   cd /home/snoozescript/tide-os
   bash demo.sh
   ```

2. **Read User Guide**
   ```bash
   cat docs/USER_GUIDE.md
   ```

3. **Explore Features**
   - Interactive chat: `tide`
   - Shell commands: `tide --shell "description"`
   - Code help: `tide --write "function" -l python`

4. **Record Demo Video**
   - Use screen recorder
   - Run through demo.sh
   - Capture all features

---

## Uninstallation

```bash
# Remove tide commands
sudo rm /usr/local/bin/tide
sudo rm /usr/local/bin/tide-doctor

# Remove installation
sudo rm -rf /opt/tide
sudo rm -rf /etc/tide

# Remove MOTD
sudo rm /etc/update-motd.d/99-tide

# Note: Ollama and models remain installed
# To remove Ollama: sudo rm /usr/local/bin/ollama
# To remove models: rm -rf ~/.ollama
```

---

## Support

If setup fails:

1. Check logs: `journalctl -u ollama`
2. Verify Python: `python3 --version`
3. Check Ollama API: `curl http://localhost:11434/api/tags`
4. Review this guide and try manual setup

---

**Setup Time**: 5-10 minutes
**Last Updated**: February 2026
