#!/usr/bin/env bash
###############################################################################
# build-iso.sh — Build a bootable Tide OS ISO (tide-os.iso)
#
# Creates a live Linux ISO based on Debian (minimal) with the Tide OS
# AI coding agent pre-installed and auto-launched on boot.
#
# Requirements:
#   sudo apt-get install -y debootstrap squashfs-tools xorriso \
#       isolinux syslinux-common grub-efi-amd64-bin grub-common mtools
#
# Usage:
#   sudo bash scripts/build-iso.sh
#
###############################################################################
set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────
ISO_NAME="tide-os"
ISO_LABEL="TIDE_OS"
ISO_OUTPUT=".build/iso/tide-os.iso"
WORK_DIR="/tmp/tide-os-build"
CHROOT_DIR="${WORK_DIR}/chroot"
ISO_DIR="${WORK_DIR}/iso"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}[TIDE-OS]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ─── Pre-flight checks ──────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (sudo)."
    echo "Usage: sudo bash scripts/build-iso.sh"
    exit 1
fi

for cmd in debootstrap mksquashfs xorriso grub-mkstandalone rsync mkfs.vfat mcopy; do
    if ! command -v "$cmd" &>/dev/null; then
        err "Missing required command: $cmd"
        echo "Install with: sudo apt-get install -y debootstrap squashfs-tools xorriso grub-efi-amd64-bin grub-common"
        exit 1
    fi
done

# ─── Clean previous build ───────────────────────────────────────────────────
log "Cleaning previous build artifacts..."
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"/{boot/grub,live,isolinux,.disk}

# ─── Step 1: Bootstrap minimal Debian system ─────────────────────────────────
log "Bootstrapping minimal Debian system (this may take a few minutes)..."
debootstrap --arch=amd64 --variant=minbase trixie "${CHROOT_DIR}" http://deb.debian.org/debian

# ─── Step 2: Configure the chroot ───────────────────────────────────────────
log "Configuring chroot environment..."

# Set hostname
echo "tide-os" > "${CHROOT_DIR}/etc/hostname"
cat > "${CHROOT_DIR}/etc/hosts" <<EOF
127.0.0.1   localhost
127.0.1.1   tide-os
::1         localhost ip6-localhost ip6-loopback
EOF

# Configure APT sources
cat > "${CHROOT_DIR}/etc/apt/sources.list" <<EOF
deb http://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb http://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
EOF

# Mount required filesystems for chroot
mount --bind /dev "${CHROOT_DIR}/dev"
mount --bind /dev/pts "${CHROOT_DIR}/dev/pts"
mount -t proc proc "${CHROOT_DIR}/proc"
mount -t sysfs sys "${CHROOT_DIR}/sys"

# ─── Step 3: Install packages inside chroot ──────────────────────────────────
log "Installing base system packages..."
chroot "${CHROOT_DIR}" /bin/bash -c "
    set -e
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y --no-install-recommends \
        linux-image-amd64 \
        live-boot \
        systemd \
        systemd-sysv \
        dbus \
        network-manager \
        curl \
        wget \
        ca-certificates \
        git \
        unzip \
        sudo \
        bash \
        vim-tiny \
        htop \
        openssh-client \
        iproute2 \
        iputils-ping \
        net-tools \
        locales \
        console-setup \
        build-essential \
        python3 \
        python3-pip

    # Set locale
    echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen
    locale-gen
    update-locale LANG=en_US.UTF-8

    # Clean apt cache
    apt-get clean
    rm -rf /var/lib/apt/lists/*
"

# ─── Step 4: Install Bun runtime ─────────────────────────────────────────────
log "Installing Bun runtime..."
chroot "${CHROOT_DIR}" /bin/bash -c "
    set -e
    mkdir -p /opt/bun
    export BUN_INSTALL=/opt/bun
    export HOME=/root
    curl -fsSL https://bun.sh/install | bash
    ln -sf /opt/bun/bin/bun /usr/local/bin/bun
    ln -sf /opt/bun/bin/bunx /usr/local/bin/bunx
    chmod -R a+rX /opt/bun
"

# ─── Step 5: Copy and install Tide OS agent ──────────────────────────────────
log "Installing Tide OS coding agent..."

# Copy project files (excluding unnecessary dirs)
mkdir -p "${CHROOT_DIR}/opt/tide-os"
rsync -a --exclude='node_modules' \
         --exclude='target' \
         --exclude='.git' \
         --exclude='.backup' \
         "${PROJECT_DIR}/" "${CHROOT_DIR}/opt/tide-os/"

chroot "${CHROOT_DIR}" /bin/bash -c "
    export HOME=/root
    export PATH=\"/opt/bun/bin:\$PATH\"
    cd /opt/tide-os
    bun install --production 2>/dev/null || bun install 2>/dev/null || true
    chmod -R a+rX /opt/tide-os
"

# ─── Step 6: Configure Tide OS branding & auto-login ─────────────────────────
log "Configuring Tide OS branding..."

# Create Tide OS banner / MOTD
cat > "${CHROOT_DIR}/etc/motd" <<'MOTD'

████████╗██╗██████╗ ███████╗     ██████╗ ███████╗
╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝
   ██║   ██║██║  ██║█████╗      ██║   ██║███████╗
   ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║
   ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║
   ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝

  AI-Powered Coding Operating System
  Type 'tide' to launch the Tide OS coding agent.
  Type 'help' for available commands.

MOTD

# Create /etc/os-release
cat > "${CHROOT_DIR}/etc/os-release" <<'OSRELEASE'
PRETTY_NAME="Tide OS 1.0"
NAME="Tide OS"
VERSION_ID="1.0"
VERSION="1.0 (Wave)"
VERSION_CODENAME=wave
ID=tide-os
ID_LIKE=debian
HOME_URL="https://github.com/SnoozeScript/tide-os"
SUPPORT_URL="https://github.com/SnoozeScript/tide-os/issues"
BUG_REPORT_URL="https://github.com/SnoozeScript/tide-os/issues"
ANSI_COLOR="0;36"
OSRELEASE

# Create /etc/lsb-release
cat > "${CHROOT_DIR}/etc/lsb-release" <<'LSBRELEASE'
DISTRIB_ID=TideOS
DISTRIB_RELEASE=1.0
DISTRIB_CODENAME=wave
DISTRIB_DESCRIPTION="Tide OS 1.0 (Wave)"
LSBRELEASE

# Create custom issue banner
cat > "${CHROOT_DIR}/etc/issue" <<'ISSUE'

  ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗
  ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝
     ██║   ██║██║  ██║█████╗      ██║   ██║███████╗
     ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║
     ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║
     ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝

  Tide OS 1.0 — AI-Powered Coding OS
  Kernel: \r on \m
  Login: \l

ISSUE

# Create the 'tide' launcher command
cat > "${CHROOT_DIR}/usr/local/bin/tide" <<'TIDECMD'
#!/usr/bin/env bash
export PATH="/opt/bun/bin:$PATH"
cd /opt/tide-os
exec bun packages/coding-agent/src/cli.ts "$@"
TIDECMD
chmod +x "${CHROOT_DIR}/usr/local/bin/tide"

# Create a custom neofetch-like info command
cat > "${CHROOT_DIR}/usr/local/bin/tide-info" <<'TIDEINFO'
#!/usr/bin/env bash
echo ""
echo -e "\033[36m  ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗\033[0m"
echo -e "\033[36m  ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝\033[0m"
echo -e "\033[36m     ██║   ██║██║  ██║█████╗      ██║   ██║███████╗\033[0m"
echo -e "\033[36m     ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║\033[0m"
echo -e "\033[36m     ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║\033[0m"
echo -e "\033[36m     ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝\033[0m"
echo ""
echo -e "  \033[1mOS:\033[0m          Tide OS 1.0 (Wave)"
echo -e "  \033[1mKernel:\033[0m      $(uname -r)"
echo -e "  \033[1mUptime:\033[0m      $(uptime -p 2>/dev/null || echo 'N/A')"
echo -e "  \033[1mShell:\033[0m       $(basename $SHELL)"
echo -e "  \033[1mBun:\033[0m         $(bun --version 2>/dev/null || echo 'not installed')"
echo -e "  \033[1mNode:\033[0m        $(node --version 2>/dev/null || echo 'not installed')"
echo -e "  \033[1mMemory:\033[0m      $(free -h 2>/dev/null | awk '/Mem:/ {print $3 "/" $2}' || echo 'N/A')"
echo -e "  \033[1mDisk:\033[0m        $(df -h / 2>/dev/null | awk 'NR==2 {print $3 "/" $2}' || echo 'N/A')"
echo -e "  \033[1mAgent:\033[0m       Tide OS Coding Agent"
echo ""
TIDEINFO
chmod +x "${CHROOT_DIR}/usr/local/bin/tide-info"

# Create a help command
cat > "${CHROOT_DIR}/usr/local/bin/tide-help" <<'TIDEHELP'
#!/usr/bin/env bash
echo ""
echo -e "\033[1;36mTide OS — Available Commands\033[0m"
echo ""
echo -e "  \033[1mtide\033[0m            Launch the Tide OS AI coding agent"
echo -e "  \033[1mtide-info\033[0m       Display system information"
echo -e "  \033[1mtide-help\033[0m       Show this help message"
echo ""
echo -e "\033[1;36mSystem Commands\033[0m"
echo ""
echo -e "  \033[1mgit\033[0m             Version control"
echo -e "  \033[1mvim\033[0m             Text editor (vim-tiny)"
echo -e "  \033[1mhtop\033[0m            Process monitor"
echo -e "  \033[1mpython3\033[0m         Python interpreter"
echo ""
TIDEHELP
chmod +x "${CHROOT_DIR}/usr/local/bin/tide-help"

# ─── Step 7: Create user and configure auto-login ────────────────────────────
log "Setting up user and auto-login..."
chroot "${CHROOT_DIR}" /bin/bash -c "
    set -e
    # Create tide user (ok if already present)
    useradd -m -s /bin/bash -G sudo tide 2>/dev/null || true
    echo 'tide:tide' | chpasswd
    echo 'root:tide' | chpasswd

    # Allow tide user to sudo without password
    echo 'tide ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/tide
    chmod 440 /etc/sudoers.d/tide
"

# Setup auto-login on tty1
mkdir -p "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d"
cat > "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d/autologin.conf" <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin tide --noclear %I \$TERM
EOF

# Auto-display info on login — append to both root and tide bashrc
TIDE_BASHRC_SNIPPET=$(cat <<'BASHRC'

# Tide OS customization
export PATH="/opt/bun/bin:/usr/local/bin:$PATH"
alias help='tide-help'
alias info='tide-info'

# Show welcome on first login
if [ -z "$TIDE_WELCOMED" ]; then
    export TIDE_WELCOMED=1
    tide-info
fi
BASHRC
)

echo "$TIDE_BASHRC_SNIPPET" >> "${CHROOT_DIR}/root/.bashrc"
if [ -f "${CHROOT_DIR}/home/tide/.bashrc" ]; then
    echo "$TIDE_BASHRC_SNIPPET" >> "${CHROOT_DIR}/home/tide/.bashrc"
    chroot "${CHROOT_DIR}" chown tide:tide /home/tide/.bashrc
fi

# ─── Step 8: Clean up chroot & unmount ───────────────────────────────────────
log "Cleaning up chroot..."
chroot "${CHROOT_DIR}" /bin/bash -c "
    apt-get clean
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
    rm -f /var/log/*.log /var/log/apt/*.log
"

# Unmount everything
umount "${CHROOT_DIR}/dev/pts" 2>/dev/null || true
umount "${CHROOT_DIR}/dev" 2>/dev/null || true
umount "${CHROOT_DIR}/proc" 2>/dev/null || true
umount "${CHROOT_DIR}/sys" 2>/dev/null || true

# ─── Step 9: Create squashfs filesystem ──────────────────────────────────────
log "Creating squashfs filesystem (this will take a few minutes)..."
mksquashfs "${CHROOT_DIR}" "${ISO_DIR}/live/filesystem.squashfs" \
    -comp xz -Xbcj x86 -b 1M -no-duplicates -no-recovery

# ─── Step 10: Copy kernel and initrd ─────────────────────────────────────────
log "Setting up kernel and initrd..."
VMLINUZ=$(find "${CHROOT_DIR}/boot" -name "vmlinuz-*" | sort -V | tail -1)
INITRD=$(find "${CHROOT_DIR}/boot" -name "initrd.img-*" | sort -V | tail -1)

if [[ -z "$VMLINUZ" || -z "$INITRD" ]]; then
    err "Could not find kernel or initrd in chroot!"
    exit 1
fi

cp "$VMLINUZ" "${ISO_DIR}/boot/vmlinuz"
cp "$INITRD" "${ISO_DIR}/boot/initrd.img"

# ─── Step 11: Configure GRUB (UEFI boot) ─────────────────────────────────────
log "Configuring GRUB bootloader..."

cat > "${ISO_DIR}/boot/grub/grub.cfg" <<GRUBCFG
set timeout=5
set default=0

# Locate the ISO filesystem by its volume label so kernel/initrd paths resolve
search --set=root --no-floppy --label ${ISO_LABEL}

insmod all_video
insmod gfxterm
insmod png
terminal_output gfxterm

set gfxmode=auto
set gfxpayload=keep

set color_normal=cyan/black
set color_highlight=white/cyan
set menu_color_normal=cyan/black
set menu_color_highlight=white/cyan

menuentry "Tide OS 1.0 — Live (Default)" {
    linux /boot/vmlinuz boot=live quiet splash
    initrd /boot/initrd.img
}

menuentry "Tide OS 1.0 — Live (Verbose)" {
    linux /boot/vmlinuz boot=live
    initrd /boot/initrd.img
}

menuentry "Tide OS 1.0 — Live (Safe Mode)" {
    linux /boot/vmlinuz boot=live nomodeset
    initrd /boot/initrd.img
}

menuentry "Tide OS 1.0 — Live (RAM)" {
    linux /boot/vmlinuz boot=live toram quiet splash
    initrd /boot/initrd.img
}
GRUBCFG

# Minimal embedded config that the UEFI binary uses to find the real grub.cfg
# on the ISO. Keeping it tiny avoids module-loading issues inside the EFI image.
cat > "${WORK_DIR}/embed.cfg" <<EMBED
search --set=root --no-floppy --label ${ISO_LABEL}
configfile /boot/grub/grub.cfg
EMBED

# Create UEFI boot image with all modules needed to read an ISO9660 filesystem,
# locate the volume by label, and load a Linux kernel + initrd. Missing any of
# these modules causes the "you need to load the kernel first" error.
grub-mkstandalone \
    --format=x86_64-efi \
    --output="${WORK_DIR}/bootx64.efi" \
    --locales="" \
    --fonts="" \
    --modules="part_gpt part_msdos fat iso9660 loopback normal configfile search search_label search_fs_uuid search_fs_file linux echo all_video gfxterm gfxmenu efi_gop efi_uga video boot chain reboot halt test ls cat help" \
    "boot/grub/grub.cfg=${WORK_DIR}/embed.cfg"

# Create FAT EFI system partition image
dd if=/dev/zero of="${ISO_DIR}/boot/grub/efi.img" bs=1M count=10
mkfs.vfat "${ISO_DIR}/boot/grub/efi.img"
mmd -i "${ISO_DIR}/boot/grub/efi.img" ::/EFI ::/EFI/BOOT
mcopy -i "${ISO_DIR}/boot/grub/efi.img" "${WORK_DIR}/bootx64.efi" ::/EFI/BOOT/BOOTX64.EFI

# ─── Step 12: Configure ISOLINUX (BIOS boot) ─────────────────────────────────
log "Configuring ISOLINUX for BIOS boot..."

ISOLINUX_BIN="/usr/lib/ISOLINUX/isolinux.bin"
LDLINUX_C32="/usr/lib/syslinux/modules/bios/ldlinux.c32"
LIBUTIL_C32="/usr/lib/syslinux/modules/bios/libutil.c32"
MENU_C32="/usr/lib/syslinux/modules/bios/menu.c32"
ISOHDPFX_BIN="/usr/lib/ISOLINUX/isohdpfx.bin"

cp "$ISOLINUX_BIN" "${ISO_DIR}/isolinux/"
cp "$LDLINUX_C32" "${ISO_DIR}/isolinux/" 2>/dev/null || true
cp "$LIBUTIL_C32" "${ISO_DIR}/isolinux/" 2>/dev/null || true
cp "$MENU_C32" "${ISO_DIR}/isolinux/" 2>/dev/null || true

cat > "${ISO_DIR}/isolinux/isolinux.cfg" <<'ISOCFG'
UI menu.c32
PROMPT 0
TIMEOUT 50
DEFAULT live

MENU TITLE Tide OS 1.0 Boot Menu
MENU COLOR title  1;36;40  #ff00ffff #00000000
MENU COLOR border 30;44    #00000000 #00000000
MENU COLOR sel    7;37;40  #ffffffff #ff00aaff
MENU COLOR unsel  37;40    #ff00ffff #00000000
MENU COLOR tabmsg 37;40    #ff999999 #00000000

LABEL live
    MENU LABEL ^Tide OS 1.0 -- Live (Default)
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live quiet splash
    MENU DEFAULT

LABEL live-verbose
    MENU LABEL Tide OS 1.0 -- Live (^Verbose)
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live

LABEL live-safe
    MENU LABEL Tide OS 1.0 -- Live (^Safe Mode)
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live nomodeset

LABEL live-ram
    MENU LABEL Tide OS 1.0 -- Live (to ^RAM)
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live toram quiet splash
ISOCFG

# ─── Step 13: Create disk info ───────────────────────────────────────────────
echo "Tide OS 1.0 \"Wave\" - Live" > "${ISO_DIR}/.disk/info"
echo "full" > "${ISO_DIR}/.disk/cd_type"

# ─── Step 14: Build the ISO ──────────────────────────────────────────────────
log "Building ${ISO_OUTPUT}..."
mkdir -p "$(dirname "${PROJECT_DIR}/${ISO_OUTPUT}")"

xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "${ISO_LABEL}" \
    -appid "Tide OS 1.0" \
    -publisher "Tide OS Team" \
    -preparer "Tide OS Build System" \
    -eltorito-boot isolinux/isolinux.bin \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -isohybrid-mbr "${ISOHDPFX_BIN}" \
    -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
    -output "${PROJECT_DIR}/${ISO_OUTPUT}" \
    "${ISO_DIR}"

# ─── Step 15: Report ─────────────────────────────────────────────────────────
ISO_SIZE=$(du -sh "${PROJECT_DIR}/${ISO_OUTPUT}" | cut -f1)

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  Tide OS ISO built successfully!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BOLD}File:${NC}     ${PROJECT_DIR}/${ISO_OUTPUT}"
echo -e "  ${BOLD}Size:${NC}     ${ISO_SIZE}"
echo -e "  ${BOLD}Label:${NC}    ${ISO_LABEL}"
echo -e "  ${BOLD}Boot:${NC}     BIOS (ISOLINUX) + UEFI (GRUB)"
echo ""
echo -e "  ${BOLD}To test with QEMU:${NC}"
echo -e "    qemu-system-x86_64 -cdrom ${ISO_OUTPUT} -m 2G -boot d"
echo ""
echo -e "  ${BOLD}To burn to USB:${NC}"
echo -e "    sudo dd if=${ISO_OUTPUT} of=/dev/sdX bs=4M status=progress"
echo ""
echo -e "  ${BOLD}Default login:${NC}"
echo -e "    User: tide  |  Password: tide"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# ─── Cleanup ─────────────────────────────────────────────────────────────────
log "Cleaning up build directory..."
rm -rf "${WORK_DIR}"

log "Done! Your ISO is at: ${PROJECT_DIR}/${ISO_OUTPUT}"
