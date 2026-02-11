#!/bin/bash
# Tide OS Lite - Installation Script
# Sets up Ollama + Tide CLI for offline AI coding assistance
# Run this during ISO build or as post-install

set -e

TIDE_VERSION="0.52.9"
DEFAULT_MODEL="glm-4.7-flash:latest"
TIDE_DIR="/opt/tide"
CONFIG_DIR="/etc/tide/agent"
PI_DIR="/home/snoozescript/tide-os/third_party/pi-mono"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

clear
echo "========================================"
echo "   Tide OS Lite - Installer"
echo "   Offline AI Coding Assistant"
echo "========================================"
echo ""

# 1. Install Ollama
log_step "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    log_info "Ollama installed"
else
    log_info "Ollama already installed"
fi

# 2. Enable and start Ollama service
log_step "Setting up Ollama service..."
useradd -r -s /bin/false ollama 2>/dev/null || true
systemctl daemon-reload
systemctl enable ollama 2>/dev/null || true
systemctl start ollama 2>/dev/null || true

# Wait for Ollama to be ready
log_info "Waiting for Ollama to start..."
sleep 3
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_info "Ollama is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        log_warn "Ollama not responding, continuing anyway..."
    fi
    sleep 1
done

# 3. Pull the default model (skip in ISO build, do on first boot)
log_step "Checking default model: $DEFAULT_MODEL"
if ollama list | grep -q "$DEFAULT_MODEL"; then
    log_info "Model already available"
else
    log_info "Model not found. Will be pulled on first boot or you can run:"
    echo "    ollama pull $DEFAULT_MODEL"
fi

# 4. Install Node.js
log_step "Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
log_info "Node.js: $(node --version)"

# 5. Create Tide directories
log_step "Creating Tide directories..."
mkdir -p "$TIDE_DIR/bin"
mkdir -p "$CONFIG_DIR"
mkdir -p "/root/.tide/agent"
mkdir -p "/etc/skel/.tide/agent"

# 6. Install pi binary (the actual CLI)
log_step "Installing Tide CLI binary..."
if [ -d "$PI_DIR/packages/coding-agent/dist" ]; then
    # Copy the entire coding-agent package
    cp -r "$PI_DIR/packages/coding-agent" "$TIDE_DIR/cli-package"
    # Create symlink to main entry point
    ln -sf "$TIDE_DIR/cli-package/dist/cli.js" "$TIDE_DIR/bin/pi"
    log_info "Tide CLI installed from source"
else
    log_error "Tide CLI source not found at $PI_DIR"
    exit 1
fi

# 7. Install tide wrapper script
log_step "Creating tide command wrapper..."
cat > /usr/local/bin/tide << 'TIDE_WRAPPER'
#!/bin/bash
# Tide CLI wrapper - Routes to pi with Ollama config
# This allows 'tide' command to work out of the box

# Set config directories
export PI_CONFIG_DIR="${PI_CONFIG_DIR:-$HOME/.tide/agent}"

# Check for system-wide config if user config doesn't exist
if [ ! -f "$PI_CONFIG_DIR/models.json" ] && [ -f "/etc/tide/agent/models.json" ]; then
    mkdir -p "$PI_CONFIG_DIR"
    cp /etc/tide/agent/models.json "$PI_CONFIG_DIR/"
    cp /etc/tide/agent/settings.json "$PI_CONFIG_DIR/" 2>/dev/null || true
fi

# Path to pi CLI
PI_BINARY="/opt/tide/bin/pi"

# Check if pi exists
if [ ! -f "$PI_BINARY" ]; then
    echo "❌ Tide CLI not found at $PI_BINARY"
    echo "   Please reinstall Tide OS"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Starting Ollama service..."
    systemctl --user start ollama 2>/dev/null || \
    sudo systemctl start ollama 2>/dev/null || \
    (ollama serve > /dev/null 2>&1 &)
    sleep 3
fi

# Run pi with ollama as default provider
# Users can override with --provider or --model flags
exec node "$PI_BINARY" --provider ollama --model glm-4.7-flash:latest "$@"
TIDE_WRAPPER

chmod +x /usr/local/bin/tide
log_info "tide command installed at /usr/local/bin/tide"

# 8. Install system-wide config
log_step "Installing system configuration..."
cat > "$CONFIG_DIR/models.json" << 'EOF'
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        {
          "id": "glm-4.7-flash:latest",
          "name": "GLM 4.7 Flash (Offline)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 131072,
          "maxTokens": 8192,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        },
        {
          "id": "llama3.1:8b",
          "name": "Llama 3.1 8B (Offline)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 4096,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        },
        {
          "id": "llama3.2:latest",
          "name": "Llama 3.2 (Offline)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 4096,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
EOF

cat > "$CONFIG_DIR/settings.json" << EOF
{
  "defaultProvider": "ollama",
  "defaultModel": "$DEFAULT_MODEL",
  "defaultThinkingLevel": "off",
  "quietStartup": false,
  "theme": "dark"
}
EOF

# Also copy to /etc/skel for new users
cp "$CONFIG_DIR/models.json" "/etc/skel/.tide/agent/"
cp "$CONFIG_DIR/settings.json" "/etc/skel/.tide/agent/"

log_info "System config installed to $CONFIG_DIR"

# 9. Create tide-doctor utility
log_step "Creating tide-doctor utility..."
cat > /usr/local/bin/tide-doctor << 'EOF'
#!/bin/bash
echo "╔═══════════════════════════════════════╗"
echo "║      Tide OS - Health Check           ║"
echo "╚═══════════════════════════════════════╝"
echo ""

PASS="✅"
FAIL="❌"

# Check Ollama service
echo "1. Ollama Service"
if systemctl is-active --quiet ollama 2>/dev/null || pgrep -x ollama > /dev/null; then
    echo "   $PASS Ollama is running"
else
    echo "   $FAIL Ollama is NOT running"
    echo "      Fix: sudo systemctl start ollama"
fi

# Check Ollama API
echo ""
echo "2. Ollama API"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   $PASS API responding on port 11434"
else
    echo "   $FAIL API not responding"
fi

# Check models
echo ""
echo "3. Models"
MODELS=$(ollama list 2>/dev/null | tail -n +2)
if [ -n "$MODELS" ]; then
    echo "   $PASS Installed models:"
    echo "$MODELS" | while read line; do
        echo "      - $line"
    done
else
    echo "   $FAIL No models installed"
    echo "      Fix: ollama pull glm-4.7-flash:latest"
fi

# Check Node.js
echo ""
echo "4. Node.js"
if command -v node &> /dev/null; then
    echo "   $PASS Node.js $(node --version)"
else
    echo "   $FAIL Node.js not installed"
fi

# Check Tide CLI
echo ""
echo "5. Tide CLI"
if [ -f "/opt/tide/bin/pi" ]; then
    echo "   $PASS pi binary: /opt/tide/bin/pi"
else
    echo "   $FAIL pi binary not found"
fi

if [ -f "/usr/local/bin/tide" ]; then
    echo "   $PASS tide wrapper: /usr/local/bin/tide"
else
    echo "   $FAIL tide wrapper not found"
fi

# Check config
echo ""
echo "6. Configuration"
if [ -f "/etc/tide/agent/models.json" ]; then
    echo "   $PASS System config: /etc/tide/agent/"
else
    echo "   $FAIL System config missing"
fi

if [ -f "$HOME/.tide/agent/models.json" ]; then
    echo "   $PASS User config: $HOME/.tide/agent/"
else
    echo "   $PASS Will copy from system config on first run"
fi

echo ""
echo "═══════════════════════════════════════"
echo "Run 'tide' to start the AI assistant!"
echo "═══════════════════════════════════════"
EOF
chmod +x /usr/local/bin/tide-doctor
log_info "tide-doctor installed"

# 10. Install first-boot service (pulls model if not present)
log_step "Setting up first-boot service..."
cat > /etc/systemd/system/tide-firstboot.service << 'EOF'
[Unit]
Description=Tide OS First Boot Setup
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=oneshot
ExecStart=/opt/tide/scripts/firstboot.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /opt/tide/scripts
cat > /opt/tide/scripts/firstboot.sh << 'EOF'
#!/bin/bash
# First boot setup - ensure model is available

DEFAULT_MODEL="glm-4.7-flash:latest"

# Wait for Ollama
for i in {1..60}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Check if model exists
if ! ollama list | grep -q "$DEFAULT_MODEL"; then
    echo "Pulling $DEFAULT_MODEL (this may take a while)..."
    ollama pull "$DEFAULT_MODEL"
fi

# Mark as done
touch /opt/tide/.firstboot-done
EOF
chmod +x /opt/tide/scripts/firstboot.sh

systemctl daemon-reload
systemctl enable tide-firstboot.service 2>/dev/null || true
log_info "First-boot service configured"

# Done!
echo ""
echo "========================================"
echo "   ✅ Tide OS Lite Installed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Pull the model: ollama pull $DEFAULT_MODEL"
echo "  2. Run: tide"
echo "  3. Start coding with offline AI!"
echo ""
echo "Troubleshooting: tide-doctor"
echo ""
