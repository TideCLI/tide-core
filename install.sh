#!/bin/bash
# Tide OS Installation Script
# Install Tide OS on your Linux system

set -e

# Configuration
VERSION="2.0.0"
INSTALL_DIR="/opt/tide-os"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/tide"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ] && [ "$1" != "--user" ]; then
        log_warn "Not running as root. Use --user for user-mode installation."
    fi
}

# Install dependencies
install_deps() {
    log_info "Installing dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip curl
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip curl
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python python-pip curl
    fi
    
    # Install Python dependencies
    pip3 install rich requests --quiet 2>/dev/null || true
    
    log_success "Dependencies installed"
}

# Install Ollama
install_ollama() {
    log_info "Checking Ollama..."
    
    if command -v ollama &> /dev/null; then
        log_success "Ollama already installed"
        return 0
    fi
    
    log_info "Installing Ollama..."
    
    # Download and install Ollama
    curl -fsSL https://ollama.com/install.sh | sh
    
    log_success "Ollama installed"
}

# Install Tide OS
install_tide() {
    log_info "Installing Tide OS v${VERSION}..."
    
    # Create install directory
    sudo mkdir -p "$INSTALL_DIR"
    
    # Copy source
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    sudo cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
    
    # Copy tools
    sudo cp -r "$SCRIPT_DIR/tools" "$INSTALL_DIR/"
    
    # Create config directory
    mkdir -p "$CONFIG_DIR"
    
    # Create default config
    cat > "$CONFIG_DIR/settings.json" << EOF
{
  "model": "qwen3:latest",
  "ollama_host": "http://localhost:11434",
  "timeout": 120,
  "auto_setup": true
}
EOF
    
    # Create launcher scripts
    create_launchers
    
    log_success "Tide OS installed to $INSTALL_DIR"
}

# Create launcher scripts
create_launchers() {
    log_info "Creating launcher scripts..."
    
    # Main tide command
    sudo tee "$BIN_DIR/tide" > /dev/null << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/../opt/tide-os/src"
exec python3 -m tide.cli.main "$@"
EOF
    sudo chmod +x "$BIN_DIR/tide"
    
    # TUI launcher
    sudo tee "$BIN_DIR/tide-tui" > /dev/null << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/../opt/tide-os/src"
exec python3 -m tide.tui.interface "$@"
EOF
    sudo chmod +x "$BIN_DIR/tide-tui"
    
    # Model manager
    sudo cp "$SCRIPT_DIR/tools/tide-model" "$BIN_DIR/tide-model"
    sudo chmod +x "$BIN_DIR/tide-model"
    
    log_success "Launchers created"
}

# Setup Tide OS branding
setup_branding() {
    log_info "Setting up Tide OS branding..."
    
    # Create version file
    sudo mkdir -p /etc/tide-os
    echo "Tide OS v${VERSION}" | sudo tee /etc/tide-os/version > /dev/null
    
    # Create MOTD
    sudo tee /etc/motd.d/tide-os > /dev/null << EOF
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║    🌊  Welcome to Tide OS v${VERSION}                              ║
║                                                                   ║
║    Your AI-Powered Terminal                                      ║
║                                                                   ║
║    Get started:                                                   ║
║      tide          - Start AI chat                                ║
║      tide-tui     - Launch TUI interface                         ║
║      tide-model   - Manage AI models                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    
    log_success "Branding configured"
}

# Auto-setup models
setup_models() {
    log_info "Checking AI models..."
    
    # Start Ollama in background
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama
    sleep 3
    
    # Check models
    if ! ollama list | grep -q "qwen3"; then
        log_info "Installing recommended AI model (qwen3:latest)..."
        ollama pull qwen3:latest
    fi
    
    # Kill background Ollama
    kill $OLLAMA_PID 2>/dev/null || true
    
    log_success "AI models ready"
}

# Show summary
show_summary() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                    🌊 Tide OS Installed! 🌊                        ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Commands:"
    echo "  tide          - Start AI chat"
    echo "  tide-tui      - Launch beautiful TUI"
    echo "  tide-model   - Manage AI models"
    echo ""
    echo "First steps:"
    echo "  1. Start Ollama: ollama serve"
    echo "  2. Run Tide: tide"
    echo ""
}

# Main
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║               🌊 Tide OS Installer v${VERSION} 🌊                    ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    check_root "$@"
    
    if [ "$1" = "--user" ]; then
        # User mode installation
        log_info "User-mode installation selected"
        # Would set up in ~/.local instead
        log_warn "User-mode installation not fully implemented"
        exit 1
    fi
    
    # Install
    install_deps
    install_ollama
    install_tide
    setup_branding
    
    # Ask about models
    if [ -t 1 ]; then
        read -p "Install recommended AI model now? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            setup_models
        fi
    fi
    
    show_summary
}

main "$@"
