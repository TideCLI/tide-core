#!/bin/bash
#
# Start Tide OS ISO Build
# Run this to create the bootable ISO
#

echo "🌊 Starting Tide OS ISO Build"
echo "=============================="
echo ""
echo "⚠️  This will take 30-60 minutes"
echo "⚠️  Requires 25-30 GB disk space"
echo "⚠️  Requires internet connection"
echo ""
read -p "Continue? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    cd /home/snoozescript/tide-os/iso-build
    sudo ./live-build-auto.sh 2>&1 | tee iso-build.log
else
    echo "Build cancelled."
    exit 1
fi
