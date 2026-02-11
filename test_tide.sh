#!/bin/bash
# Quick test script for Tide CLI with Ollama
# Run this after model download completes

set -e

PI_BIN="/home/snoozescript/tide-os/third_party/pi-mono/packages/coding-agent/dist/cli.js"
MODEL="glm-4.7-flash:latest"

echo "=========================================="
echo "   Tide CLI - Quick Test"
echo "=========================================="
echo ""

# 1. Check Ollama
echo "1. Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is running"
else
    echo "   ❌ Ollama not running. Starting..."
    ollama serve &
    sleep 5
fi

# 2. Check model
echo ""
echo "2. Checking model..."
if ollama list | grep -q "$MODEL"; then
    echo "   ✅ Model $MODEL is available"
else
    echo "   ❌ Model not found. Run: ollama pull $MODEL"
    exit 1
fi

# 3. Setup config
echo ""
echo "3. Setting up config..."
mkdir -p ~/.tide/agent
cp /home/snoozescript/tide-os/packaging/models.json ~/.tide/agent/

cat > ~/.tide/agent/settings.json << EOF
{
  "defaultProvider": "ollama",
  "defaultModel": "$MODEL",
  "defaultThinkingLevel": "off",
  "quietStartup": false
}
EOF
echo "   ✅ Config created at ~/.tide/agent/"

# 4. Test CLI
echo ""
echo "4. Testing Tide CLI..."
echo ""
echo "Running: node $PI_BIN --provider ollama --model $MODEL 'Say hello'"
echo "-------------------------------------------"
export PI_CONFIG_DIR="$HOME/.tide/agent"
node "$PI_BIN" --provider ollama --model "$MODEL" "Say hello in one sentence."

echo ""
echo "-------------------------------------------"
echo ""
echo "✅ Test complete!"
echo ""
echo "To use Tide CLI:"
echo "  cd /home/snoozescript/tide-os/third_party/pi-mono"
echo "  export PI_CONFIG_DIR=~/.tide/agent"
echo "  node packages/coding-agent/dist/cli.js --provider ollama --model $MODEL"
echo ""
echo "Or after running install script:"
echo "  tide"
echo ""
