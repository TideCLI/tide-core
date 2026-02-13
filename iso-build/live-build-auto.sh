#!/bin/bash
#
# Tide OS ISO Builder - Automated using live-build
# This is the proper way to build Debian/Ubuntu based distributions
#

set -e

TIDE_VERSION="2.0.0"
BUILD_DIR="$(pwd)/tide-os-live-build"
CONFIG_DIR="$BUILD_DIR/config"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🌊 Tide OS Live Build System                                 ║"
echo "║   Automated ISO Creation                                       ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Step 1: Install live-build
echo -e "${CYAN}Step 1: Installing live-build...${NC}"
apt-get update -qq
apt-get install -y -qq live-build live-config live-boot || {
    echo -e "${RED}Failed to install live-build${NC}"
    exit 1
}

# Step 2: Create build directory
echo -e "${CYAN}Step 2: Setting up build environment...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Step 3: Initialize live-build
echo -e "${CYAN}Step 3: Initializing live-build configuration...${NC}"
lb config \
    --distribution jammy \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --debian-installer live \
    --debian-installer-gui true \
    --archive-areas "main restricted universe multiverse" \
    --apt-source-archives false \
    --parent-mirror-bootstrap http://archive.ubuntu.com/ubuntu/ \
    --parent-mirror-binary http://archive.ubuntu.com/ubuntu/ \
    --mirror-bootstrap http://archive.ubuntu.com/ubuntu/ \
    --mirror-binary http://archive.ubuntu.com/ubuntu/ \
    --bootappend-live "boot=casper quiet splash" \
    --iso-volume "Tide OS $TIDE_VERSION" \
    --iso-publisher "Tide OS Team" \
    --iso-application "Tide OS" \
    --linux-packages "linux-image linux-headers" \
    --memtest memtest86+ \
    --win32-loader false \
    --loadlin false \
    --firmware-binary true \
    --firmware-chroot true

# Step 4: Create package list
echo -e "${CYAN}Step 4: Configuring packages...${NC}"
mkdir -p "$CONFIG_DIR/package-lists"

cat > "$CONFIG_DIR/package-lists/tide-os.list.chroot" << 'EOF'
# Desktop Environment
ubuntu-desktop-minimal
gnome-session
gnome-shell
gnome-terminal
nautilus

# System Tools
linux-image-generic
linux-headers-generic
grub-pc
grub-efi-amd64
efibootmgr
shim-signed

# Tide OS Dependencies
python3
python3-pip
python3-venv
python3-full
git
curl
wget
vim
nano
htop
tree
ripgrep
fd-find
neofetch
figlet
toilet
lolcat
cowsay
fortune-mod
bash-completion
plymouth
plymouth-themes

# Development
build-essential
cmake
pkg-config

# Media
ubuntu-restricted-addons
fonts-dejavu
ttf-ubuntu-font-family

# Utilities
usb-creator-gtk
unetbootin
gparted
disks
EOF

# Step 5: Create hooks for Tide installation
echo -e "${CYAN}Step 5: Creating installation hooks...${NC}"
mkdir -p "$CONFIG_DIR/hooks/live"

cat > "$CONFIG_DIR/hooks/live/tide-install.chroot" << 'HOOK'
#!/bin/bash
set -e

echo "🌊 Installing Tide OS..."

# Create tide user
useradd -m -s /bin/bash -G sudo tide || true
echo "tide:tide" | chpasswd
echo "tide ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set hostname
echo "tide-os" > /etc/hostname
cat > /etc/hosts << EOF
127.0.0.1   localhost
127.0.1.1   tide-os
EOF

# Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh || true

# Install Tide OS
echo "Installing Tide OS application..."
mkdir -p /opt/tide-os
mkdir -p /etc/tide-os
mkdir -p /var/lib/tide-os

# Create virtual environment
python3 -m venv /opt/tide-os/venv

# Copy Tide files (will be done in bootstrap hook)
echo "Tide OS 2.0.0" > /etc/tide-os/version
echo "Install Date: $(date)" >> /etc/tide-os/version

# Install Python packages
/opt/tide-os/venv/bin/pip install --upgrade pip
/opt/tide-os/venv/bin/pip install rich requests prompt-toolkit

# Create tide commands
cat > /usr/local/bin/tide-chat << 'CMD'
#!/bin/bash
source /opt/tide-os/venv/bin/activate
cd /opt/tide-os && python3 tide-v2.py "$@"
CMD
chmod +x /usr/local/bin/tide-chat

cat > /usr/local/bin/tide-tools << 'CMD'
#!/bin/bash
source /opt/tide-os/venv/bin/activate
cd /opt/tide-os && python3 tide-v2.py --tools
CMD
chmod +x /usr/local/bin/tide-tools

# Configure MOTD
cat > /etc/update-motd.d/99-tide-os << 'MOTD'
#!/bin/bash
echo ""
/usr/bin/figlet -f slant "TIDE OS" | /usr/games/lolcat 2>/dev/null || echo "TIDE OS"
echo "  🌊 Professional AI Coding Environment v2.0.0"
echo "  Powered by Ollama • Based on charmbracelet/crush"
echo ""
echo "  Quick Start:"
echo "    tide-chat    - Start AI assistant"
echo "    tide-tools   - List available tools"
echo "    ollama list  - Show AI models"
echo ""
MOTD
chmod +x /etc/update-motd.d/99-tide-os

# Configure bash
cat > /etc/profile.d/tide-os.sh << 'PROFILE'
# Tide OS Configuration
export TIDE_OS_VERSION="2.0.0"
export TIDE_OS_NAME="Tide OS"
export PS1="🌊 \u@tide-os:\w\$ "

# Aliases
alias tide='tide-chat'
alias ttools='tide-tools'
alias tlist='tide-tools'
PROFILE
chmod +x /etc/profile.d/tide-os.sh

# Set default desktop background
cat > /usr/share/tide-os/set-defaults.sh << 'DEFAULTS'
#!/bin/bash
# Set Tide OS defaults for GNOME

# Set background to blue
gsettings set org.gnome.desktop.background primary-color '#0066cc' || true
gsettings set org.gnome.desktop.background color-shading-type 'solid' || true

# Set theme
gsettings set org.gnome.desktop.interface gtk-theme 'Yaru' || true
gsettings set org.gnome.desktop.interface icon-theme 'Yaru' || true

# Show home icon on desktop
gsettings set org.gnome.shell.extensions.ding show-home true || true
DEFAULTS
chmod +x /usr/share/tide-os/set-defaults.sh

echo "✅ Tide OS installation complete!"
HOOK

chmod +x "$CONFIG_DIR/hooks/live/tide-install.chroot"

# Step 6: Copy Tide application files
echo -e "${CYAN}Step 6: Copying Tide application...${NC}"
mkdir -p "$CONFIG_DIR/includes.chroot/opt/tide-os"
mkdir -p "$CONFIG_DIR/includes.chroot/etc/tide-os/config"

# Copy Tide v2 files
cp -r ../../tide_v2 "$CONFIG_DIR/includes.chroot/opt/tide-os/"
cp ../../tide-v2.py "$CONFIG_DIR/includes.chroot/opt/tide-os/"
cp ../../tide.json "$CONFIG_DIR/includes.chroot/etc/tide-os/config/"

# Step 7: Configure bootloader
echo -e "${CYAN}Step 7: Configuring bootloader...${NC}"
mkdir -p "$CONFIG_DIR/bootloaders"

# Custom GRUB config
cat > "$CONFIG_DIR/bootloaders/grub.cfg" << 'GRUB'
set timeout=10
set default=0

# Set colors
set menu_color_normal=white/black
set menu_color_highlight=black/light-blue

# Tide OS Theme
set gfxmode=1024x768
set gfxpayload=keep

loadfont unicode

set theme=/boot/grub/themes/tide/theme.txt

menuentry "🌊 Start Tide OS (Live)" --class ubuntu --class gnu-linux --class gnu --class os {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}

menuentry "🌊 Start Tide OS (Safe Graphics)" --class ubuntu --class gnu-linux --class gnu --class os {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper nomodeset quiet splash ---
    initrd /casper/initrd
}

menuentry "🔧 Install Tide OS" --class ubuntu --class gnu-linux --class gnu --class os {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper only-ubiquity quiet splash ---
    initrd /casper/initrd
}

menuentry "🧪 Memory Test" {
    linux16 /boot/memtest86+.bin
}
GRUB

# Step 8: Configure Plymouth
echo -e "${CYAN}Step 8: Configuring Plymouth theme...${NC}"
mkdir -p "$CONFIG_DIR/includes.chroot/usr/share/plymouth/themes/tide"

cat > "$CONFIG_DIR/includes.chroot/usr/share/plymouth/themes/tide/tide.plymouth" << 'PLYMOUTH'
[Plymouth Theme]
Name=Tide OS
Description=Tide OS Boot Theme
ModuleName=two-step

[two-step]
ImageDir=/usr/share/plymouth/themes/tide
HorizontalAlignment=.5
VerticalAlignment=.5
PLYMOUTH

# Step 9: Build the ISO
echo -e "${CYAN}Step 9: Building Tide OS ISO...${NC}"
echo -e "${CYAN}This may take 30-60 minutes depending on your system...${NC}"
echo ""

lb build 2>&1 | tee build.log || {
    echo -e "${RED}❌ Build failed! Check build.log for details.${NC}"
    exit 1
}

# Step 10: Move output
echo -e "${CYAN}Step 10: Finalizing...${NC}"
ISO_NAME="tide-os-${TIDE_VERSION}-amd64.iso"
if [ -f "live-image-amd64.hybrid.iso" ]; then
    mv live-image-amd64.hybrid.iso "../${ISO_NAME}"
    cd ..
    
    # Generate checksums
    sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"
    md5sum "$ISO_NAME" > "${ISO_NAME}.md5"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║   ✅ Tide OS ISO Build Complete!                               ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Output:${NC} $(pwd)/${ISO_NAME}"
    echo -e "${CYAN}Size:${NC}   $(du -h "${ISO_NAME}" | cut -f1)"
    echo ""
    echo "To test:"
    echo "  qemu-system-x86_64 -m 4G -cdrom ${ISO_NAME}"
    echo ""
    echo "To write to USB:"
    echo "  sudo dd if=${ISO_NAME} of=/dev/sdX bs=4M status=progress"
    echo ""
else
    echo -e "${RED}❌ ISO not found. Build may have failed.${NC}"
    exit 1
fi
