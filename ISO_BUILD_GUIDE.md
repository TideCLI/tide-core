# 🖥️ Tide OS - ISO Build Guide

## Overview

This guide explains how to create a **bootable Tide OS ISO** for distribution.

## ⚠️ Important Note for Final Year Project

**Given the deadline (Feb 14, 2026), creating a full ISO is NOT recommended** because:
- Building a custom Linux ISO takes 4-8 hours
- Requires 20GB+ disk space
- Complex testing and validation needed

## 🚀 Recommended Alternatives (Ready Now)

### Option 1: Docker Image (Fastest - 5 minutes)
```bash
cd /home/snoozescript/tide-os
docker build -t tide-os:latest .
docker run -it tide-os:latest
```

### Option 2: System Branding Script (Ready)
```bash
cd /home/snoozescript/tide-os
sudo ./install-tide-os.sh
```
This brands your existing Ubuntu as "Tide OS" instantly!

### Option 3: Pre-configured VM (Quick)
Create a VirtualBox VM with:
- Ubuntu 22.04
- Tide pre-installed
- Export as OVA file

## 📀 Full ISO Build Process (For Future)

### Prerequisites
```bash
# Need 20GB+ free space
# Ubuntu 20.04+ or Debian 11+
sudo apt install -y \
    squashfs-tools \
    genisoimage \
    syslinux-utils \
    isolinux \
    grub-pc-bin \
    mtools \
    xorriso
```

### Method 1: Using Cubic (Easiest)

```bash
# Install Cubic
sudo apt-add-repository ppa:cubic-wizard/release
sudo apt update
sudo apt install cubic

# Launch Cubic
cubic

# Steps:
# 1. Select original Ubuntu ISO
# 2. Customize:
#    - Install Tide: sudo ./install-tide-os.sh
#    - Install Ollama
#    - Pre-download models: ollama pull qwen3
#    - Set branding
# 3. Generate new ISO
```

### Method 2: Manual ISO Build

```bash
# 1. Create working directory
mkdir -p ~/tide-os-iso/{mnt,squashfs,custom}

# 2. Mount original Ubuntu ISO
sudo mount -o loop ubuntu-22.04.iso ~/tide-os-iso/mnt

# 3. Copy contents
cp -r ~/tide-os-iso/mnt/* ~/tide-os-iso/custom/
sudo cp -r ~/tide-os-iso/mnt/.disk ~/tide-os-iso/custom/

# 4. Extract squashfs
sudo unsquashfs -d ~/tide-os-iso/squashfs \
    ~/tide-os-iso/mnt/casper/filesystem.squashfs

# 5. Chroot and customize
sudo mount --bind /dev ~/tide-os-iso/squashfs/dev
sudo mount --bind /proc ~/tide-os-iso/squashfs/proc
sudo mount --bind /sys ~/tide-os-iso/squashfs/sys

sudo chroot ~/tide-os-iso/squashfs

# Inside chroot:
# - Install Tide OS
# - Configure everything
# - Exit

# 6. Create new squashfs
sudo mksquashfs ~/tide-os-iso/squashfs \
    ~/tide-os-iso/custom/casper/filesystem.squashfs \
    -comp xz -e boot

# 7. Update manifest
sudo cp ~/tide-os-iso/mnt/casper/filesystem.manifest \
    ~/tide-os-iso/custom/casper/

# 8. Create ISO
sudo grub-mkrescue -o tide-os-2.0.iso \
    ~/tide-os-iso/custom/
```

## 📁 Files for ISO Creation

### Required Files Structure
```
tide-os-iso/
├── custom/                 # ISO root
│   ├── .disk/             # CD info
│   ├── boot/              # Boot files
│   ├── casper/            # Live system
│   │   ├── filesystem.squashfs
│   │   ├── filesystem.manifest
│   │   └── initrd
│   ├── isolinux/          # BIOS bootloader
│   ├── EFI/               # UEFI bootloader
│   └── preseed/           # Auto-install config
└── squashfs/              # Extracted system
```

### Tide OS Customizations

#### 1. GRUB Theme
```bash
# Create custom GRUB theme
cat > /boot/grub/themes/tide/theme.txt << 'EOF'
# Tide OS GRUB Theme
title-text: "Tide OS 2.0"
desktop-image: "background.png"
EOF
```

#### 2. Plymouth Theme (Boot Animation)
```bash
# Create boot animation
mkdir -p /usr/share/plymouth/themes/tide
cat > /usr/share/plymouth/themes/tide/tide.plymouth << 'EOF'
[Plymouth Theme]
Name=Tide OS
Description=Tide OS Boot Theme
ModuleName=two-step
EOF
```

#### 3. Desktop Background
```bash
# Set wallpaper
mkdir -p /usr/share/backgrounds/tide/
cp tide-wallpaper.png /usr/share/backgrounds/tide/
```

## 🎨 Branding Elements

### What Gets Branded
1. **Boot Screen** - GRUB menu with Tide logo
2. **Boot Animation** - Plymouth theme
3. **Login Screen** - GDM/LightDM theme
4. **Desktop** - Wallpaper, icons, theme
5. **Terminal** - Tide prompt (🌊)
6. **Applications Menu** - Tide categories
7. **MOTD** - Welcome message
8. **Ollama** - Pre-configured

### Tide OS Identity
```
Name: Tide OS
Version: 2.0.0
Codename: "Wave"
Based on: Ubuntu 22.04 LTS
Desktop: GNOME (customized)
Shell: Bash with Tide theme
Package Manager: apt
Default User: tide
```

## 📦 Distribution Methods

### 1. Live ISO (Recommended)
- Boot without installing
- Try Tide OS instantly
- Install if desired

### 2. Netboot
- Boot over network
- For labs/enterprises
- PXE server setup

### 3. VM Image
- Pre-built VM
- VirtualBox/Vmware/Proxmox
- Import and run

### 4. Docker (Already Done ✅)
```bash
docker pull tide-os:latest
docker run -it tide-os
```

### 5. WSL (Windows)
```bash
# Export rootfs
tar -czf tide-os-wsl.tar.gz -C ~/tide-os-iso/squashfs .
# Import on Windows
wsl --import TideOS C:\WSL\TideOS tide-os-wsl.tar.gz
```

## 🔧 Post-Installation (for ISO)

### Pre-configured Settings
- Ollama service enabled
- qwen3 model pre-downloaded
- Tide commands in PATH
- Welcome screen configured
- Sample projects included

### First Boot Setup
```bash
#!/bin/bash
# /opt/tide-os/first-boot.sh
# Runs on first boot

# Create user
useradd -m -s /bin/bash -G sudo tide

# Pull default model
ollama pull qwen3:latest

# Clone sample projects
cd /home/tide/projects
git clone https://github.com/example/python-samples

# Done
rm /opt/tide-os/first-boot.sh
```

## 📊 Size Estimates

| Component | Size |
|-----------|------|
| Base Ubuntu ISO | 3.5 GB |
| Ollama + qwen3 | 4-8 GB |
| Tide Application | 50 MB |
| Development Tools | 2 GB |
| **Total Tide OS ISO** | **8-14 GB** |

## ✅ Testing Checklist

- [ ] Boots in BIOS mode
- [ ] Boots in UEFI mode
- [ ] Live mode works
- [ ] Installation works
- [ ] Ollama service starts
- [ ] Tide commands work
- [ ] Internet connectivity
- [ ] Sound works
- [ ] Graphics work
- [ ] Keyboard layout correct

## 🎯 For Your Final Year Project

### What's Ready Now (Use This!)
```bash
# ✅ Docker Image (5 minutes)
docker build -t tide-os .
docker run -it tide-os

# ✅ System Branding (2 minutes)
sudo ./install-tide-os.sh

# ✅ Virtual Machine (30 minutes)
# Create VM, install script, export OVA
```

### What's NOT Ready (8+ hours)
```bash
# ❌ Full ISO Build
# - Too time consuming
# - Risk of failure
# - Not needed for demo
```

## 📋 Demo Script for Evaluators

```bash
# Show Tide OS branding
cat /etc/tide-os/version
neofetch

# Show Tide tools
tide-tools

# Start AI assistant
tide-chat

# Show it's based on professional architecture
ls -la /opt/tide-os/
cat /opt/tide-os/tide_v2/agent.py
```

## 📚 Resources

- **Ubuntu ISO Guide**: https://help.ubuntu.com/community/LiveCDCustomization
- **Cubic**: https://github.com/PJ-Singh-001/Cubic
- **Debian Live**: https://live-team.pages.debian.net/live-manual/

## 🚀 Quick Start (DO THIS NOW!)

```bash
cd /home/snoozescript/tide-os

# Option 1: Docker (Easiest for demo)
sudo docker build -t tide-os:latest .
sudo docker run -it tide-os:latest

# Option 2: Brand your system
sudo ./install-tide-os.sh
# Then reboot and show the branded system

# Option 3: Create VM
# Use VirtualBox, install Ubuntu, run install script
```

---

**Bottom Line**: Use Docker or the branding script for your project. Full ISO is overkill for the deadline but documented here for future development! 🌊
