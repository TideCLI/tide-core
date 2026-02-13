#!/bin/bash
#
# Tide OS Installer Script
# Brands your Ubuntu/Debian system as Tide OS
# Usage: sudo ./install-tide-os.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Tide OS Configuration
TIDE_VERSION="2.0.0"
TIDE_NAME="Tide OS"
INSTALL_DIR="/opt/tide-os"
BIN_DIR="/usr/local/bin"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🌊 Tide OS Installer v${TIDE_VERSION}                           ║"
echo "║   Professional AI Coding Environment                          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo -e "${RED}❌ Cannot detect OS${NC}"
    exit 1
fi

echo -e "${CYAN}📦 Detected OS: ${OS} ${VER}${NC}\n"

# Check if Ubuntu/Debian
if [[ ! "$OS" =~ (Ubuntu|Debian) ]]; then
    echo -e "${YELLOW}⚠️  Warning: Tide OS is optimized for Ubuntu/Debian${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${CYAN}🚀 Installing Tide OS...${NC}\n"

# Update system
echo -e "${CYAN}⬆️  Updating system packages...${NC}"
apt-get update -qq

# Install dependencies
echo -e "${CYAN}📦 Installing dependencies...${NC}"
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    ripgrep \
    neofetch \
    figlet \
    lolcat \
    toilet \
    cowsay \
    fortune \
    bash-completion \
    sudo \
    2>/dev/null || true

# Install Ollama
echo -e "${CYAN}🤖 Installing Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✅ Ollama installed${NC}"
else
    echo -e "${GREEN}✅ Ollama already installed${NC}"
fi

# Create Tide OS directories
echo -e "${CYAN}📁 Creating Tide OS directories...${NC}"
mkdir -p ${INSTALL_DIR}
mkdir -p ${INSTALL_DIR}/tools
mkdir -p ${INSTALL_DIR}/config
mkdir -p /etc/tide-os

# Copy Tide application
echo -e "${CYAN}📝 Installing Tide application...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r ${SCRIPT_DIR}/tide_v2 ${INSTALL_DIR}/
cp ${SCRIPT_DIR}/tide-v2.py ${INSTALL_DIR}/
cp ${SCRIPT_DIR}/tide.json ${INSTALL_DIR}/config/

# Create virtual environment
echo -e "${CYAN}🐍 Setting up Python environment...${NC}"
python3 -m venv ${INSTALL_DIR}/venv
source ${INSTALL_DIR}/venv/bin/activate
pip install -q --upgrade pip
pip install -q rich requests prompt-toolkit

# Create tide command
echo -e "${CYAN}🔧 Creating tide commands...${NC}"
cat > ${BIN_DIR}/tide-chat << 'EOF'
#!/bin/bash
source /opt/tide-os/venv/bin/activate
cd /opt/tide-os && python3 tide-v2.py "$@"
EOF
chmod +x ${BIN_DIR}/tide-chat

cat > ${BIN_DIR}/tide-tools << 'EOF'
#!/bin/bash
source /opt/tide-os/venv/bin/activate
cd /opt/tide-os && python3 tide-v2.py --tools
EOF
chmod +x ${BIN_DIR}/tide-tools

cat > ${BIN_DIR}/tide << 'EOF'
#!/bin/bash
tide-chat "$@"
EOF
chmod +x ${BIN_DIR}/tide

# Create Tide OS branding
echo -e "${CYAN}🎨 Applying Tide OS branding...${NC}"

# Update MOTD
cat > /etc/update-motd.d/99-tide-os << 'EOF'
#!/bin/bash
echo ""
/usr/games/figlet -f slant "TIDE OS" | /usr/games/lolcat
echo "  🌊 Professional AI Coding Environment v2.0.0" | /usr/games/lolcat
echo "  Powered by Ollama • Based on charmbracelet/crush" | /usr/games/lolcat
echo ""
echo "  Available Commands:"
echo "    tide-chat   - Start AI assistant"
echo "    tide-tools  - List available tools"
echo "    ollama list - Show AI models"
echo ""
EOF
chmod +x /etc/update-motd.d/99-tide-os

# Remove other MOTD parts
rm -f /etc/update-motd.d/10-help-text 2>/dev/null || true

# Update bashrc for all users
cat > /etc/profile.d/tide-os.sh << 'EOF'
# Tide OS Configuration
export TIDE_OS_VERSION="2.0.0"
export TIDE_OS_NAME="Tide OS"
export PS1="🌊 \u@tide-os:\w\$ "

# Tide aliases
alias tide='tide-chat'
alias ttools='tide-tools'
alias tlist='tide-tools'

# Fun aliases
alias weather='curl wttr.in'
alias moon='curl wttr.in/Moon'
EOF
chmod +x /etc/profile.d/tide-os.sh

# Create Tide OS desktop entry (if GUI)
if [ -d /usr/share/applications ]; then
    cat > /usr/share/applications/tide-os.desktop << 'EOF'
[Desktop Entry]
Name=Tide OS
Comment=Professional AI Coding Environment
Exec=/usr/local/bin/tide-chat
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Development;Utility;
EOF
fi

# Set hostname
echo -e "${CYAN}🖥️  Setting hostname...${NC}"
hostnamectl set-hostname tide-os 2>/dev/null || true

# Create version file
cat > /etc/tide-os/version << EOF
TIDE_OS_VERSION=${TIDE_VERSION}
TIDE_OS_NAME="${TIDE_NAME}"
INSTALL_DATE=$(date)
EOF

# Create uninstall script
cat > ${BIN_DIR}/tide-uninstall << 'EOF'
#!/bin/bash
# Tide OS Uninstaller
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

echo "Uninstalling Tide OS..."
rm -rf /opt/tide-os
rm -f /usr/local/bin/tide*
rm -f /etc/update-motd.d/99-tide-os
rm -f /etc/profile.d/tide-os.sh
rm -rf /etc/tide-os
echo "Tide OS uninstalled."
EOF
chmod +x ${BIN_DIR}/tide-uninstall

# Success message
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║   ✅ Tide OS v${TIDE_VERSION} installed successfully!                  ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🌊 Your system is now branded as Tide OS!${NC}"
echo ""
echo "Quick Start:"
echo "  tide-chat           - Start AI assistant"
echo "  tide-tools          - List all tools"
echo "  ollama pull qwen3   - Download AI model"
echo ""
echo "Log out and log back in to see the full branding."
echo ""
