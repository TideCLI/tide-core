#!/bin/bash
# Startup script for Tide OS Docker with Ollama

echo "🌊 Starting Tide OS..."

# Start Ollama service in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Starting Ollama service..."
sleep 3

# Check if model exists, if not offer to download
if ! ollama list | grep -q "qwen3"; then
    echo ""
    echo "⚠️  No AI model found. Downloading qwen3 (this may take 5-10 minutes)..."
    ollama pull qwen3:latest
    echo "✅ Model ready!"
fi

echo ""
echo "✅ Tide OS is ready!"
echo ""
echo "Available commands:"
echo "  tide-chat    - Start AI assistant"
echo "  tide-tools   - List available tools"
echo "  ollama list  - Show installed models"
echo ""

# Start bash shell
exec /bin/bash
