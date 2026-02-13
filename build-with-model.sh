#!/bin/bash
#
# Build Tide OS Docker with pre-downloaded model
#

echo "🌊 Building Tide OS Docker with AI Model"
echo "========================================="
echo ""
echo "This will:"
echo "  1. Build base Docker image"
echo "  2. Download qwen3 model (4-8 GB, takes 10-20 min)"
echo "  3. Create ready-to-use image"
echo ""

read -p "Continue? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    exit 1
fi

cd /home/snoozescript/tide-os

# Step 1: Build base image
echo ""
echo "➜ Step 1: Building base image..."
sudo docker build -t tide-os:base .

# Step 2: Run container and download model
echo ""
echo "➜ Step 2: Downloading AI model (10-20 minutes)..."
sudo docker run -d --name tide-model-downloader tide-os:base sleep 3600

# Download model
sudo docker exec tide-model-downloader bash -c "
    ollama serve &
    sleep 5
    echo 'Downloading qwen3 model...'
    ollama pull qwen3:latest
    echo 'Model downloaded!'
"

# Step 3: Commit container to new image
echo ""
echo "➜ Step 3: Creating final image..."
sudo docker stop tide-model-downloader
sudo docker commit tide-model-downloader tide-os:latest
sudo docker rm tide-model-downloader

echo ""
echo "✅ Tide OS Docker with model created!"
echo ""
echo "To run:"
echo "  sudo docker run -it tide-os:latest"
echo ""
echo "Image size:"
sudo docker images tide-os:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
