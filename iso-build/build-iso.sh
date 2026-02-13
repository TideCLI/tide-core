#!/bin/bash
#
# Tide OS ISO Builder
# Creates a fully customized Linux distribution
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
TIDE_VERSION="2.0.0"
TIDE_CODENAME="Wave"
BASE_IMAGE="ubuntu-22.04.3-desktop-amd64.iso"
BUILD_DIR="$(pwd)/build"
OUTPUT_DIR="$(pwd)/output"
MOUNT_DIR="$BUILD_DIR/mount"
EXTRACT_DIR="$BUILD_DIR/extract"
CUSTOM_DIR="$BUILD_DIR/custom"
CHROOT_DIR="$BUILD_DIR/chroot"

# Show banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🌊 Tide OS ISO Builder v${TIDE_VERSION}                             ║"
echo "║   Fully Customized Linux Distribution                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Function to show progress
progress() {
    echo -e "${CYAN}➜ $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Step 1: Install dependencies
progress "Step 1/10: Installing dependencies..."
apt-get update -qq
apt-get install -y -qq \
    squashfs-tools \
    genisoimage \
    syslinux-utils \
    isolinux \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    xorriso \
    p7zip-full \
    wget \
    curl \
    rsync \
    squashfuse \
    || error "Failed to install dependencies"

success "Dependencies installed"

# Step 2: Clean and create directories
progress "Step 2/10: Preparing build directories..."
rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$MOUNT_DIR" "$EXTRACT_DIR" "$CUSTOM_DIR" "$CHROOT_DIR" "$OUTPUT_DIR"
success "Directories created"

# Step 3: Download base ISO if not present
progress "Step 3/10: Checking for base ISO..."
ISO_PATH="$OUTPUT_DIR/$BASE_IMAGE"

if [ ! -f "$ISO_PATH" ]; then
    progress "Downloading Ubuntu 22.04 ISO..."
    wget -q --show-progress \
        "https://releases.ubuntu.com/22.04/$BASE_IMAGE" \
        -O "$ISO_PATH" \
        || error "Failed to download ISO"
fi

success "Base ISO ready: $ISO_PATH"

# Step 4: Mount and extract ISO
progress "Step 4/10: Extracting ISO contents..."
mount -o loop,ro "$ISO_PATH" "$MOUNT_DIR" || error "Failed to mount ISO"
rsync -a "$MOUNT_DIR/" "$EXTRACT_DIR/"
umount "$MOUNT_DIR"
success "ISO extracted"

# Step 5: Extract squashfs
progress "Step 5/10: Extracting filesystem..."
SQUASHFS="$EXTRACT_DIR/casper/filesystem.squashfs"
unsquashfs -q -d "$CHROOT_DIR" "$SQUASHFS" || error "Failed to extract squashfs"
success "Filesystem extracted"

# Step 6: Prepare chroot environment
progress "Step 6/10: Preparing chroot environment..."

# Mount necessary filesystems
mount --bind /dev "$CHROOT_DIR/dev"
mount --bind /proc "$CHROOT_DIR/proc"
mount --bind /sys "$CHROOT_DIR/sys"
mount --bind /run "$CHROOT_DIR/run"

# Copy DNS configuration
cp /etc/resolv.conf "$CHROOT_DIR/etc/"

success "Chroot environment ready"

# Step 7: Customize in chroot
progress "Step 7/10: Customizing Tide OS (this may take 10-15 minutes)..."

# Create customization script
cat > "$CHROOT_DIR/tmp/customize.sh" << 'CHROOT_EOF'
#!/bin/bash
set -e

# Update package lists
apt-get update -qq

# Install Tide OS dependencies
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    git curl wget vim nano \
    htop tree ripgrep fd-find \
    neofetch figlet lolcat \
    toilet cowsay fortune \
    bash-completion \
    plymouth plymouth-themes \
    grub2-common \
    2>/dev/null || true

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Create tide user
useradd -m -s /bin/bash -G sudo tide || true
echo "tide:tide" | chpasswd
echo "tide ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set hostname
echo "tide-os" > /etc/hostname

# Configure hosts
cat > /etc/hosts << EOF
127.0.0.1   localhost
127.0.1.1   tide-os
EOF

# Create Tide OS directories
mkdir -p /opt/tide-os
mkdir -p /etc/tide-os
mkdir -p /usr/share/tide-os

# Install Tide application
cd /opt/tide-os
python3 -m venv venv
source venv/bin/activate

# Copy Tide files (these will be copied before chroot)
# The actual files are copied in step 8

echo "Tide OS ${TIDE_VERSION}" > /etc/tide-os/version
echo "Install Date: $(date)" >> /etc/tide-os/version

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*
rm -rf /var/tmp/*

echo "Customization complete!"
CHROOT_EOF

chmod +x "$CHROOT_DIR/tmp/customize.sh"

# Run customization in chroot
chroot "$CHROOT_DIR" /tmp/customize.sh || error "Customization failed"

success "Customization complete"

# Step 8: Copy Tide files into chroot
progress "Step 8/10: Installing Tide application..."

# Copy Tide v2
cp -r ../tide_v2 "$CHROOT_DIR/opt/tide-os/"
cp ../tide-v2.py "$CHROOT_DIR/opt/tide-os/"
cp ../tide.json "$CHROOT_DIR/opt/tide-os/config/"
cp ../install-tide-os.sh "$CHROOT_DIR/tmp/"

# Run branding script in chroot
chroot "$CHROOT_DIR" /tmp/install-tide-os.sh || true

success "Tide installed"

# Step 9: Configure branding
progress "Step 9/10: Configuring Tide OS branding..."

# GRUB Theme
mkdir -p "$CHROOT_DIR/boot/grub/themes/tide"

# Create GRUB theme
cat > "$CHROOT_DIR/boot/grub/themes/tide/theme.txt" << 'EOF'
title-text: ""

+ boot_menu {
    left = 15%
    width = 70%
    top = 30%
    height = 50%
    item_color = "#cccccc"
    selected_item_color = "#00aaff"
    item_height = 30
    item_spacing = 10
}

+ label {
    text = "🌊 Tide OS 2.0"
    color = "#00aaff"
    font = "DejaVu Sans Bold 32"
    left = 15%
    top = 15%
}

+ label {
    text = "Professional AI Coding Environment"
    color = "#888888"
    font = "DejaVu Sans 16"
    left = 15%
    top = 22%
}
EOF

# Update GRUB config
cat > "$CHROOT_DIR/etc/default/grub" << 'EOF'
GRUB_DEFAULT=0
GRUB_TIMEOUT=10
GRUB_DISTRIBUTOR="Tide OS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""
GRUB_THEME=/boot/grub/themes/tide/theme.txt
GRUB_GFXMODE=1024x768
EOF

# Plymouth Theme
mkdir -p "$CHROOT_DIR/usr/share/plymouth/themes/tide"

cat > "$CHROOT_DIR/usr/share/plymouth/themes/tide/tide.plymouth" << 'EOF'
[Plymouth Theme]
Name=Tide OS
Description=Tide OS Boot Theme
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/tide
ScriptFile=/usr/share/plymouth/themes/tide/tide.script
EOF

# Create simple Plymouth script
cat > "$CHROOT_DIR/usr/share/plymouth/themes/tide/tide.script" << 'EOF'
logo = Image("logo.png");
logo_sprite = Sprite(logo);
logo_sprite.SetX(Window.GetWidth() / 2 - logo.GetWidth() / 2);
logo_sprite.SetY(Window.GetHeight() / 2 - logo.GetHeight() / 2);
EOF

# Set default Plymouth theme
chroot "$CHROOT_DIR" plymouth-set-default-theme tide || true

# MOTD
cat > "$CHROOT_DIR/etc/update-motd.d/99-tide-os" << 'EOF'
#!/bin/bash
echo ""
echo "  🌊 Tide OS v2.0 - Professional AI Coding Environment"
echo "  Powered by Ollama • Based on charmbracelet/crush"
echo ""
echo "  Quick Start:"
echo "    tide-chat    - Start AI assistant"
echo "    tide-tools   - List available tools"
echo "    ollama list  - Show AI models"
echo ""
EOF
chmod +x "$CHROOT_DIR/etc/update-motd.d/99-tide-os"

# Desktop Background
mkdir -p "$CHROOT_DIR/usr/share/backgrounds/tide"

# Create simple background script (would normally include actual image)
cat > "$CHROOT_DIR/usr/share/tide-os/set-wallpaper.sh" << 'EOF'
#!/bin/bash
# Set Tide OS wallpaper
gsettings set org.gnome.desktop.background picture-uri file:///usr/share/backgrounds/tide/tide-wallpaper.png || true
gsettings set org.gnome.desktop.background primary-color '#0066cc' || true
EOF
chmod +x "$CHROOT_DIR/usr/share/tide-os/set-wallpaper.sh"

success "Branding configured"

# Step 10: Repack ISO
progress "Step 10/10: Building Tide OS ISO..."

# Unmount chroot filesystems
umount "$CHROOT_DIR/dev" 2>/dev/null || true
umount "$CHROOT_DIR/proc" 2>/dev/null || true
umount "$CHROOT_DIR/sys" 2>/dev/null || true
umount "$CHROOT_DIR/run" 2>/dev/null || true

# Recreate squashfs
progress "  → Creating filesystem..."
rm -f "$EXTRACT_DIR/casper/filesystem.squashfs"
mksquashfs "$CHROOT_DIR" "$EXTRACT_DIR/casper/filesystem.squashfs" \
    -comp xz -e boot -quiet || error "Failed to create squashfs"

# Update manifest
chroot "$CHROOT_DIR" dpkg-query -W --showformat='${Package} ${Version}\n' > \
    "$EXTRACT_DIR/casper/filesystem.manifest" 2>/dev/null || true

# Update filesystem size
echo -n $(du -s --block-size=1 "$CHROOT_DIR" | cut -f1) > \
    "$EXTRACT_DIR/casper/filesystem.size"

# Create ISO
progress "  → Creating ISO image..."
OUTPUT_ISO="$OUTPUT_DIR/tide-os-${TIDE_VERSION}-amd64.iso"

# Use grub-mkrescue for UEFI/BIOS support
grub-mkrescue -o "$OUTPUT_ISO" \
    "$EXTRACT_DIR" \
    --modules="part_gpt part_msdos fat iso9660 zfs zfscrypt zfsinfo linux boot linuxefi configfile normal regexp minicmd gzio xzio lzopio png gfxterm all_video efi_gop efi_uga font gfxtermgfxmenu echo test true loadenv reset" \
    --quiet 2>/dev/null || \
xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "TIDE_OS_${TIDE_VERSION}" \
    -eltorito-boot boot/grub/grub.img \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    --eltorito-catalog boot/grub/boot.cat \
    -output "$OUTPUT_ISO" \
    "$EXTRACT_DIR" || error "Failed to create ISO"

# Calculate checksum
progress "  → Generating checksums..."
cd "$OUTPUT_DIR"
sha256sum "tide-os-${TIDE_VERSION}-amd64.iso" > "tide-os-${TIDE_VERSION}-amd64.iso.sha256"
md5sum "tide-os-${TIDE_VERSION}-amd64.iso" > "tide-os-${TIDE_VERSION}-amd64.iso.md5"
cd - > /dev/null

# Set permissions
chmod 644 "$OUTPUT_ISO"

success "ISO created successfully!"

# Cleanup
progress "Cleaning up..."
rm -rf "$BUILD_DIR"
success "Cleanup complete"

# Final output
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║   ✅ Tide OS ISO Build Complete!                               ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Output:${NC} $OUTPUT_ISO"
echo -e "${CYAN}Size:${NC}   $(du -h "$OUTPUT_ISO" | cut -f1)"
echo -e "${CYAN}SHA256:${NC} $(cat "$OUTPUT_DIR/tide-os-${TIDE_VERSION}-amd64.iso.sha256" | cut -d' ' -f1 | cut -c1-16)..."
echo ""
echo "To test the ISO:"
echo "  qemu-system-x86_64 -m 4G -cdrom $OUTPUT_ISO"
echo ""
echo "To write to USB:"
echo "  sudo dd if=$OUTPUT_ISO of=/dev/sdX bs=4M status=progress"
echo ""
