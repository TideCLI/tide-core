#!/bin/bash
#
# Build BOTH Tide OS ISO and Docker
# Complete distribution package
#

set -e

echo "🌊 Tide OS - Complete Build System"
echo "=================================="
echo ""
echo "This will build:"
echo "  1. 🐳 Docker image (with llama3.1:8b model)"
echo "  2. 💿 ISO file (bootable Linux distribution)"
echo ""
echo "Estimated time: 60-90 minutes"
echo "Required space: 40-50 GB"
echo ""

read -p "Start building? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create output directory
mkdir -p /home/snoozescript/tide-os/output
cd /home/snoozescript/tide-os

echo ""
echo "========================================"
echo "STEP 1/2: Building Docker Image"
echo "========================================"
echo ""

# Build Docker with your model
docker build --build-arg MODEL=llama3.1:8b -t tide-os:latest . 2>&1 | tee output/docker-build.log

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    docker save tide-os:latest > output/tide-os-docker.tar
    echo "✅ Docker exported to output/tide-os-docker.tar"
    docker images tide-os:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" >> output/build-summary.txt
else
    echo "❌ Docker build failed! Check output/docker-build.log"
fi

echo ""
echo "========================================"
echo "STEP 2/2: Building ISO"
echo "========================================"
echo ""
echo "⚠️  This will take 30-60 minutes!"
echo ""

# Build ISO using live-build
cd iso-build
chmod +x live-build-auto.sh

# Run with logging
timeout 120m ./live-build-auto.sh 2>&1 | tee ../output/iso-build.log

# Check if ISO was created
if [ -f "../tide-os-2.0.0-amd64.iso" ]; then
    mv ../tide-os-2.0.0-amd64.iso ../output/
    mv ../tide-os-2.0.0-amd64.iso.sha256 ../output/ 2>/dev/null || true
    echo "✅ ISO build successful!"
else
    echo "❌ ISO build may have failed. Check output/iso-build.log"
fi

echo ""
echo "========================================"
echo "BUILD COMPLETE"
echo "========================================"
echo ""

cd ../output

echo "📦 Output Files:"
echo ""
ls -lh | grep -E "docker|iso|txt" || echo "No files found"
echo ""

if [ -f "tide-os-docker.tar" ]; then
    echo "🐳 Docker: tide-os-docker.tar ($(du -h tide-os-docker.tar | cut -f1))"
fi

if [ -f "tide-os-2.0.0-amd64.iso" ]; then
    echo "💿 ISO:     tide-os-2.0.0-amd64.iso ($(du -h tide-os-2.0.0-amd64.iso | cut -f1))"
fi

echo ""
echo "Next steps:"
echo "  1. Test Docker: docker load < output/tide-os-docker.tar"
echo "  2. Test ISO:    qemu-system-x86_64 -m 4G -cdrom output/tide-os-2.0.0-amd64.iso"
echo "  3. Create submission: zip -r tide-os-final.zip output/"
echo ""
