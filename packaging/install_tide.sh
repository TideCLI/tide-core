#!/bin/bash
# Tide OS Lite - Installation Script
# Sets up Ollama + Tide CLI for offline AI coding assistance

set -e

TIDE_VERSION="0.52.9"
DEFAULT_MODEL="glm-4.7-flash:latest"
TIDE_DIR="/opt/tide"
CONFIG_DIR="/etc/tide"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

log_info "Installing Tide OS Lite components..."

# 1. Install Ollama
log_info "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    log_info "Ollama installed successfully"
else
    log_info "Ollama already installed"
fi

# 2. Enable and start Ollama service
log_info "Enabling Ollama service..."
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
        log_error "Ollama failed to start"
        exit 1
    fi
    sleep 1
done

# 3. Pull the default model
log_info "Pulling default model: $DEFAULT_MODEL"
ollama pull "$DEFAULT_MODEL" || log_warn "Failed to pull model. You may need to pull it manually later."

# 4. Install Node.js (required for Tide CLI)
log_info "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    log_info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

NODE_VERSION=$(node --version 2>/dev/null || echo "none")
log_info "Node.js version: $NODE_VERSION"

# 5. Create Tide directories
log_info "Creating Tide directories..."
mkdir -p "$TIDE_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "/root/.tide/agent"
mkdir -p "/etc/skel/.tide/agent"

# 6. Install Tide CLI
log_info "Installing Tide CLI..."
if [ -d "/vagrant" ]; then
    # Running in Vagrant - copy from synced folder
    cp -r /vagrant/tide-cli "$TIDE_DIR/cli"
else
    # Install from npm (when published)
    npm install -g @tide/tide-cli 2>/dev/null || {
        log_warn "Tide CLI not yet published to npm. Installing locally..."
        # For now, create a placeholder
        echo '#!/bin/bash\necho "Tide CLI placeholder - install from source"' > /usr/local/bin/tide
        chmod +x /usr/local/bin/tide
    }
fi

# 7. Copy default models.json configuration
log_info "Configuring Ollama provider..."
if [ -f "/vagrant/packaging/models.json" ]; then
    cp /vagrant/packaging/models.json "/root/.tide/agent/models.json"
    cp /vagrant/packaging/models.json "/etc/skel/.tide/agent/models.json"
else
    # Create default config inline
    cat > "/root/.tide/agent/models.json" << 'EOF'
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        {
          "id": "nemotron-3-nano:latest",
          "name": "Nemotron 3 Nano (Offline)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 4096,
          "maxTokens": 2048,
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
        }
      ]
    }
  }
}
EOF
    cp "/root/.tide/agent/models.json" "/etc/skel/.tide/agent/models.json"
fi

# 8. Create default settings.json
log_info "Creating default settings..."
cat > "/root/.tide/agent/settings.json" << EOF
{
  "defaultProvider": "ollama",
  "defaultModel": "$DEFAULT_MODEL",
  "defaultThinkingLevel": "off",
  "quietStartup": false,
  "theme": "dark"
}
EOF
cp "/root/.tide/agent/settings.json" "/etc/skel/.tide/agent/settings.json"

# 9. Add tide to PATH for all users
log_info "Adding tide to PATH..."
if ! grep -q "tide" /etc/profile.d/tide.sh 2>/dev/null; then
    echo 'export PATH="$PATH:/opt/tide/bin"' > /etc/profile.d/tide.sh
    chmod +x /etc/profile.d/tide.sh
fi

# 10. Create tide doctor command wrapper
log_info "Creating tide doctor wrapper..."
cat > /usr/local/bin/tide-doctor << 'EOF'
#!/bin/bash
echo "=== Tide OS Health Check ==="
echo ""

# Check Ollama
echo "1. Checking Ollama..."
if systemctl is-active --quiet ollama; then
    echo "   ✓ Ollama service: running"
else
    echo "   ✗ Ollama service: NOT running"
    systemctl status ollama --no-pager || true
fi

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✓ Ollama API: responding"
else
    echo "   ✗ Ollama API: NOT responding"
fi

# Check models
echo ""
echo "2. Checking models..."
ollama list 2>/dev/null || echo "   No models found"

# Check Node.js
echo ""
echo "3. Checking Node.js..."
if command -v node &> /dev/null; then
    echo "   ✓ Node.js: $(node --version)"
else
    echo "   ✗ Node.js: NOT installed"
fi

# Check Tide CLI
echo ""
echo "4. Checking Tide CLI..."
if command -v tide &> /dev/null; then
    echo "   ✓ Tide CLI: $(tide --version 2>/dev/null || echo 'installed')"
else
    echo "   ✗ Tide CLI: NOT in PATH"
fi

# Check config
echo ""
echo "5. Checking configuration..."
if [ -f "$HOME/.tide/agent/models.json" ]; then
    echo "   ✓ models.json: present"
else
    echo "   ✗ models.json: missing"
fi

if [ -f "$HOME/.tide/agent/settings.json" ]; then
    echo "   ✓ settings.json: present"
else
    echo "   ✗ settings.json: missing"
fi

echo ""
echo "=== Health check complete ==="
EOF
chmod +x /usr/local/bin/tide-doctor

# 11. Verify installation
log_info "Verifying installation..."
sleep 2

echo ""
log_info "=== Installation Summary ==="
echo ""
echo "Ollama: $(command -v ollama && ollama --version || echo 'not found')"
echo "Node.js: $(node --version 2>/dev/null || echo 'not found')"
echo "Tide config: $HOME/.tide/agent/"
echo ""
echo "Default model: $DEFAULT_MODEL"
echo "Configured models:"
ollama list 2>/dev/null || echo "  (none pulled yet)"
echo ""
echo "Next steps:"
echo "  1. Log in as a regular user"
echo "  2. Run: tide"
echo "  3. Start chatting with your offline AI assistant!"
echo ""
echo "For troubleshooting, run: tide-doctor"
echo ""

log_info "Tide OS Lite installation complete!"
