#!/bin/bash
# Tide CLI wrapper - routes to pi with Ollama config
# This is installed as /usr/local/bin/tide

# Set config directory
export PI_CONFIG_DIR="${PI_CONFIG_DIR:-$HOME/.pi/agent}"

# Check for system-wide config if user config doesn't exist
if [ ! -f "$PI_CONFIG_DIR/models.json" ] && [ -f "/etc/tide/agent/models.json" ]; then
    mkdir -p "$PI_CONFIG_DIR"
    cp /etc/tide/agent/models.json "$PI_CONFIG_DIR/"
    [ -f "/etc/tide/agent/settings.json" ] && cp /etc/tide/agent/settings.json "$PI_CONFIG_DIR/"
fi

# Path to pi CLI
PI_BINARY="/opt/tide/bin/pi"

# Check if pi exists
if [ ! -f "$PI_BINARY" ]; then
    echo "❌ Tide CLI not found at $PI_BINARY"
    echo "   Please reinstall Tide OS"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Starting Ollama service..."
    systemctl --user start ollama 2>/dev/null || \
    sudo systemctl start ollama 2>/dev/null || \
    (ollama serve > /dev/null 2>&1 &)
    sleep 3
fi

# Run pi with ollama as default provider
exec node "$PI_BINARY" --provider ollama --model glm-4.7-flash:latest "$@"
