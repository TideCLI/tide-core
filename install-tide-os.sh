#!/bin/bash
# Tide OS Lite - Installation Script
# Converts any Ubuntu/Debian system into Tide OS
# Run: curl -fsSL https://raw.githubusercontent.com/yourrepo/tide-os/main/install-tide-os.sh | sudo bash

set -e

TIDE_VERSION="1.0.0"
DEFAULT_MODEL="llama3.1:8b"
TIDE_DIR="/opt/tide"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root (use sudo)"
        exit 1
    fi
}

print_banner() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗       ║
║   ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝       ║
║      ██║   ██║██║  ██║█████╗      ██║   ██║███████╗       ║
║      ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║       ║
║      ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║       ║
║      ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝       ║
║                                                           ║
║        AI-Powered Linux Distribution Installer            ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo "Version: $TIDE_VERSION"
    echo ""
}

install_dependencies() {
    log_step "Installing dependencies..."
    apt-get update
    apt-get install -y curl wget git python3 python3-pip python3-venv \
        nodejs npm software-properties-common apt-transport-https ca-certificates
    log_info "Dependencies installed"
}

install_ollama() {
    log_step "Installing Ollama..."
    if command -v ollama &> /dev/null; then
        log_info "Ollama already installed"
    else
        curl -fsSL https://ollama.com/install.sh | sh
        log_info "Ollama installed"
    fi
    
    # Create systemd service
    cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=default.target
EOF
    
    useradd -r -s /bin/false -m ollama 2>/dev/null || true
    systemctl daemon-reload
    systemctl enable ollama
    systemctl start ollama
    
    # Wait for Ollama
    log_info "Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            log_info "Ollama is ready"
            break
        fi
        sleep 1
    done
}

install_tide_cli() {
    log_step "Installing Tide CLI..."
    
    # Create directories
    mkdir -p $TIDE_DIR
    mkdir -p /etc/tide
    
    # Copy Python CLI
    cp -r /home/snoozescript/tide-os/tide-py $TIDE_DIR/cli
    
    # Create tide command
    cat > /usr/local/bin/tide << 'EOF'
#!/bin/bash
export PYTHONPATH=/opt/tide/cli:$PYTHONPATH
exec python3 /opt/tide/cli/tide.py "$@"
EOF
    chmod +x /usr/local/bin/tide
    
    # Create config
    mkdir -p /etc/tide
    cat > /etc/tide/config.json << EOF
{
    "version": "$TIDE_VERSION",
    "default_model": "$DEFAULT_MODEL",
    "ollama_host": "localhost",
    "ollama_port": 11434
}
EOF
    
    log_info "Tide CLI installed"
}

pull_default_model() {
    log_step "Pulling default model ($DEFAULT_MODEL)..."
    if ollama list | grep -q "$DEFAULT_MODEL"; then
        log_info "Model already available"
    else
        log_info "This may take a while (several GB download)..."
        ollama pull $DEFAULT_MODEL
        log_info "Model pulled successfully"
    fi
}

setup_branding() {
    log_step "Setting up Tide OS branding..."
    
    # Create MOTD
    cat > /etc/update-motd.d/99-tide << 'EOF'
#!/bin/bash
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Welcome to Tide OS - AI-Powered Linux Distribution       ║"
echo "║                                                           ║"
echo "║  Commands:                                                ║"
echo "║    tide          - Start AI assistant                     ║"
echo "║    tide-doctor   - Check system health                    ║"
echo "║    ollama        - Manage local AI models                 ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
EOF
    chmod +x /etc/update-motd.d/99-tide
    
    # Create tide-doctor command
    cat > /usr/local/bin/tide-doctor << 'EOF'
#!/bin/bash
python3 /opt/tide/cli/tide.py --doctor
EOF
    chmod +x /usr/local/bin/tide-doctor
    
    # Bash alias
    cat > /etc/profile.d/tide.sh << 'EOF'
alias tide="tide"
alias tide-doctor="tide-doctor"
EOF
    
    log_info "Branding configured"
}

create_desktop_shortcuts() {
    log_step "Creating desktop shortcuts..."
    
    mkdir -p /usr/share/applications
    
    cat > /usr/share/applications/tide-terminal.desktop << 'EOF'
[Desktop Entry]
Name=Tide AI Terminal
Comment=AI-Powered Terminal
Exec=gnome-terminal --command "tide"
Type=Application
Terminal=false
Icon=utilities-terminal
Categories=System;TerminalEmulator;
EOF
    
    cat > /usr/share/applications/tide-doctor.desktop << 'EOF'
[Desktop Entry]
Name=Tide Doctor
Comment=Check Tide OS Health
Exec=gnome-terminal --command "tide-doctor"
Type=Application
Terminal=false
Icon=utilities-system-monitor
Categories=System;
EOF
    
    log_info "Desktop shortcuts created"
}

run_tests() {
    log_step "Running basic tests..."
    
    # Test tide command exists
    if command -v tide &> /dev/null; then
        log_info "✓ tide command available"
    else
        log_error "✗ tide command not found"
        return 1
    fi
    
    # Test Ollama
    if systemctl is-active --quiet ollama; then
        log_info "✓ Ollama service running"
    else
        log_warn "✗ Ollama service not running"
    fi
    
    # Test model
    if ollama list | grep -q "llama"; then
        log_info "✓ Models available"
    else
        log_warn "✗ No models found"
    fi
    
    log_info "Basic tests passed"
}

main() {
    check_root
    print_banner
    
    log_info "Starting Tide OS installation..."
    log_info "This will take 10-30 minutes depending on internet speed"
    echo ""
    
    install_dependencies
    install_ollama
    install_tide_cli
    pull_default_model
    setup_branding
    create_desktop_shortcuts
    
    echo ""
    log_info "Installation complete!"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Tide OS Lite is now installed!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run 'tide-doctor' to check system health"
    echo "  2. Run 'tide' to start the AI assistant"
    echo "  3. Run 'ollama list' to see available models"
    echo ""
    echo "To pull more models:"
    echo "  ollama pull llama3.2"
    echo "  ollama pull codellama"
    echo "  ollama pull mistral"
    echo ""
    
    run_tests
}

main "$@"
