#!/bin/bash
#
# Quick Tide OS Branding Demo
# Shows Tide OS branding WITHOUT building ISO
#

echo "🌊 Creating Tide OS Demo Environment"
echo "====================================="
echo ""

# Create demo directory
mkdir -p ~/tide-os-demo
cd ~/tide-os-demo

# Create simulated boot menu
cat > boot-menu.txt << 'EOF'
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   🌊 TIDE OS 2.0                                               │
│   Professional AI Coding Environment                           │
│                                                                │
│   ┌──────────────────────────────────────────────────────┐    │
│   │  🌊 Start Tide OS (Live)                            │    │
│   │  🌊 Start Tide OS (Safe Graphics)                   │    │
│   │  🔧 Install Tide OS                                 │    │
│   │  🧪 Memory Test                                     │    │
│   └──────────────────────────────────────────────────────┘    │
│                                                                │
│   Use ↑ and ↓ keys to select, ENTER to boot                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
EOF

# Create simulated desktop
cat > desktop.txt << 'EOF'
┌────────────────────────────────────────────────────────────────┐
│ 🌊 Activities | Tide OS 2.0                          🔊 🔋 ⏰ │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │  🗂️️      │  │  🖥️      │  │  🌐      │                     │
│  │ Files    │  │ Terminal │  │ Browser  │                     │
│  └──────────┘  └──────────┘  └──────────┘                     │
│                                                                │
│  Tide OS Wallpaper (Blue wave theme)                           │
│                                                                │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│ 🌊 user@tide-os:~$ tide-chat                                  │
│ 🌊 Tide OS v2.0 - 15 tools ready                              │
└────────────────────────────────────────────────────────────────┘
EOF

# Create simulated terminal
cat > terminal.txt << 'EOF'
  _______       _     ___  ____  
 |_   _(_) __ _| |   / _ \/ ___|  🌊 Tide OS v2.0
   | | | |/ _` | |  | | | \___ \  Professional AI Coding
   | | | | (_| | |__| |_| |___) | Environment
   |_| |_|\__, |_____\___/|____/  Powered by Ollama
          |___/

  Quick Start:
    tide-chat    - Start AI assistant
    tide-tools   - List available tools
    ollama list  - Show AI models

🌊 user@tide-os:~$ 
EOF

# Create system info
cat > system-info.txt << 'EOF'
OS Name:     Tide OS
Version:     2.0.0 (Wave)
Hostname:    tide-os
Username:    tide
Prompt:      🌊 user@tide-os:~$
Tools:       15 professional tools
AI Engine:   Ollama (local)
Based on:    Ubuntu 22.04 LTS

Tide OS is READY!
EOF

echo "✅ Demo files created in ~/tide-os-demo/"
echo ""
echo "View the branding:"
echo "  cat ~/tide-os-demo/boot-menu.txt    # Boot menu"
echo "  cat ~/tide-os-demo/desktop.txt      # Desktop"
echo "  cat ~/tide-os-demo/terminal.txt     # Terminal"
echo "  cat ~/tide-os-demo/system-info.txt  # System info"
echo ""
echo "To see ACTUAL branding on YOUR system:"
echo "  cd /home/snoozescript/tide-os"
echo "  sudo ./install-tide-os.sh"
echo "  # Then reboot - your system becomes Tide OS!"
