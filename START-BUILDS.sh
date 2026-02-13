#!/bin/bash
# Start both Docker and ISO builds

echo "🌊 Starting Tide OS Builds"
echo "=========================="
echo ""

mkdir -p /home/snoozescript/tide-os/output
cd /home/snoozescript/tide-os

echo "STEP 1: Docker Build (10-15 minutes)"
echo "====================================="
docker build --build-arg MODEL=llama3.1:8b -t tide-os:latest . 2>&1 | tee output/docker-build.log &
DOCKER_PID=$!

echo "Docker build started (PID: $DOCKER_PID)"
echo "Log: output/docker-build.log"
echo ""

echo "STEP 2: ISO Build (60-90 minutes)"
echo "=================================="
cd iso-build
chmod +x live-build-auto.sh
./live-build-auto.sh 2>&1 | tee ../output/iso-build.log &
ISO_PID=$!

echo "ISO build started (PID: $ISO_PID)"
echo "Log: output/iso-build.log"
echo ""

echo "Both builds running in parallel!"
echo ""
echo "Monitor progress:"
echo "  Docker: tail -f output/docker-build.log"
echo "  ISO:    tail -f output/iso-build.log"
echo ""
echo "Wait for completion (could take 90 minutes)..."

# Wait for both
wait $DOCKER_PID
DOCKER_STATUS=$?
wait $ISO_PID
ISO_STATUS=$?

echo ""
echo "========================================"
echo "BUILD STATUS"
echo "========================================"
echo ""

if [ $DOCKER_STATUS -eq 0 ]; then
    echo "✅ Docker: SUCCESS"
    docker save tide-os:latest > ../output/tide-os-docker.tar
    echo "   Exported to: output/tide-os-docker.tar"
else
    echo "❌ Docker: FAILED"
fi

if [ $ISO_STATUS -eq 0 ] && [ -f "../tide-os-2.0.0-amd64.iso" ]; then
    echo "✅ ISO: SUCCESS"
    mv ../tide-os-2.0.0-amd64.iso ../output/
    echo "   Location: output/tide-os-2.0.0-amd64.iso"
else
    echo "❌ ISO: FAILED or INCOMPLETE"
fi

echo ""
echo "Check output/ directory for results"
