#!/bin/bash
#
# Quick Tide OS ISO Builder
# One-command ISO creation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🌊 Tide OS Quick ISO Builder                                 ║"
echo "║   One-Command Distribution Creation                            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo $0${NC}"
    exit 1
fi

# Check prerequisites
echo -e "${CYAN}Checking prerequisites...${NC}"

# Check disk space
AVAILABLE=$(df / | tail -1 | awk '{print $4}')
NEEDED=30000000  # ~30GB in KB

if [ "$AVAILABLE" -lt "$NEEDED" ]; then
    echo -e "${RED}❌ Insufficient disk space. Need ~30GB free.${NC}"
    echo "Available: $(df -h / | tail -1 | awk '{print $4}')"
    exit 1
fi

# Check architecture
if [ "$(uname -m)" != "x86_64" ]; then
    echo -e "${YELLOW}⚠️  Warning: Building on non-x86_64 architecture${NC}"
fi

# Check internet
if ! ping -c 1 google.com &> /dev/null; then
    echo -e "${RED}❌ No internet connection. Required for package downloads.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Present options
echo "Select build method:"
echo ""
echo "  1) ${CYAN}live-build (Recommended)${NC}"
echo "     • Professional quality"
echo "     • UEFI + BIOS support"
echo "     • Takes 30-60 minutes"
echo ""
echo "  2) ${CYAN}Quick remaster (Faster)${NC}"
echo "     • Modifies Ubuntu ISO"
echo "     • Faster build"
echo "     • Good for testing"
echo ""
echo "  3) ${CYAN}Docker-based (Easiest)${NC}"
echo "     • No ISO build needed"
echo "     • Instant distribution"
echo "     • Run in container"
echo ""
read -p "Choice [1-3]: " choice

case $choice in
    1)
        echo -e "${CYAN}Starting live-build...${NC}"
        cd iso-build
        chmod +x live-build-auto.sh
        ./live-build-auto.sh
        ;;
    2)
        echo -e "${CYAN}Starting quick remaster...${NC}"
        cd iso-build
        chmod +x build-iso.sh
        ./build-iso.sh
        ;;
    3)
        echo -e "${CYAN}Building Docker image...${NC}"
        docker build -t tide-os:latest ..
        echo -e "${GREEN}✅ Docker image built!${NC}"
        echo ""
        echo "Run with: docker run -it tide-os:latest"
        echo ""
        echo "To export as 'ISO-like' container:"
        echo "  docker save tide-os:latest > tide-os-docker.tar"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║   ✅ Tide OS Build Complete!                                   ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Output location: iso-build/output/"
echo ""
echo "Next steps:"
echo "  1. Test the ISO in a VM"
echo "  2. Write to USB for live testing"
echo "  3. Submit for evaluation"
echo ""
