#!/bin/bash
# Tide OS Lite - First Boot Setup Script
# Runs on first boot to ensure Ollama + model are ready

set -e

LOG_FILE="/var/log/tide-firstboot.log"
DEFAULT_MODEL="nemotron-3-nano:latest"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting Tide OS first boot setup..."

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# 1. Ensure Ollama service is running
log "Starting Ollama service..."
systemctl enable ollama 2>/dev/null || true
systemctl start ollama 2>/dev/null || true

# Wait for Ollama to be ready
log "Waiting for Ollama API..."
for i in {1..60}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log "Ollama API is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        log "ERROR: Ollama failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

# 2. Check if default model exists, pull if not
log "Checking for default model: $DEFAULT_MODEL"
if ! ollama list | grep -q "$DEFAULT_MODEL"; then
    log "Model not found. Pulling $DEFAULT_MODEL..."
    ollama pull "$DEFAULT_MODEL" 2>&1 | tee -a "$LOG_FILE" || {
        log "WARNING: Failed to pull model. User may need to pull manually."
    }
else
    log "Model $DEFAULT_MODEL already present"
fi

# 3. Ensure config directories exist for all users
for home in /home/* /root; do
    if [ -d "$home" ]; then
        mkdir -p "$home/.tide/agent"
        chown -R "$(stat -c '%U:%G' "$home" 2>/dev/null || echo 'root:root')" "$home/.tide" 2>/dev/null || true
    fi
done

# 4. Run health check
log "Running health check..."
if command -v tide-doctor &> /dev/null; then
    tide-doctor >> "$LOG_FILE" 2>&1
fi

# 5. Mark firstboot as complete
touch /etc/tide/.firstboot-complete
log "First boot setup complete!"

exit 0
