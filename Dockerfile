# Tide OS - Docker Image with Model Selection Support
# Branded AI Coding Agent Environment

FROM ubuntu:22.04

# Build argument for model selection
ARG MODEL=llama3.1:8b
ENV TIDE_MODEL=${MODEL}

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

# Set Tide branding
ENV TIDE_OS_VERSION="2.0.0"
ENV TIDE_OS_NAME="Tide OS"
ENV PS1="🌊 \u@tide-os:\w\$ "

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    ripgrep \
    fd-find \
    neofetch \
    figlet \
    lolcat \
    bash-completion \
    sudo \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create tide user
RUN useradd -m -s /bin/bash -G sudo tide && \
    echo "tide ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up Tide OS branding
RUN echo "" >> /etc/bash.bashrc && \
    echo "# Tide OS Configuration" >> /etc/bash.bashrc && \
    echo 'export PS1="🌊 \u@tide-os:\w\$ "' >> /etc/bash.bashrc && \
    echo "neofetch" >> /etc/bash.bashrc

# Create Tide OS welcome banner
RUN cat > /etc/update-motd.d/99-tide << 'EOF'
#!/bin/bash
echo ""
figlet -f slant "TIDE OS" | lolcat
echo "  🌊 Professional AI Coding Environment" | lolcat
echo "  Version 2.0.0 | Powered by Ollama" | lolcat
echo ""
echo "  Quick Start:"
echo "    tide-chat    - Start AI assistant"
echo "    tide-tools   - List available tools"
echo "    tide-models  - List/Select AI models"
echo "    ollama list  - Show installed models"
echo ""
EOF
RUN chmod +x /etc/update-motd.d/99-tide

# Switch to tide user
USER tide
WORKDIR /home/tide

# Create virtual environment
RUN python3 -m venv /home/tide/.tide-env

# Copy Tide application
COPY --chown=tide:tide tide_v2 /home/tide/tide_v2/
COPY --chown=tide:tide tide-v2.py /home/tide/
COPY --chown=tide:tide tide.json /home/tide/

# Install Python dependencies
RUN /home/tide/.tide-env/bin/pip install --upgrade pip && \
    /home/tide/.tide-env/bin/pip install \
    rich \
    requests \
    prompt-toolkit

# Create .local/bin directory and tide commands
RUN mkdir -p /home/tide/.local/bin && \
    echo '#!/bin/bash' > /home/tide/.local/bin/tide-chat && \
    echo 'source /home/tide/.tide-env/bin/activate' >> /home/tide/.local/bin/tide-chat && \
    echo 'cd /home/tide && python3 tide-v2.py "$@"' >> /home/tide/.local/bin/tide-chat && \
    chmod +x /home/tide/.local/bin/tide-chat && \
    echo '#!/bin/bash' > /home/tide/.local/bin/tide-tools && \
    echo 'source /home/tide/.tide-env/bin/activate' >> /home/tide/.local/bin/tide-tools && \
    echo 'cd /home/tide && python3 tide-v2.py --tools' >> /home/tide/.local/bin/tide-tools && \
    chmod +x /home/tide/.local/bin/tide-tools && \
    echo '#!/bin/bash' > /home/tide/.local/bin/tide-models && \
    echo 'source /home/tide/.tide-env/bin/activate' >> /home/tide/.local/bin/tide-models && \
    echo 'cd /home/tide && python3 tide-v2.py --models' >> /home/tide/.local/bin/tide-models && \
    chmod +x /home/tide/.local/bin/tide-models

# Add local bin to PATH
ENV PATH="/home/tide/.local/bin:${PATH}"

# Set up bash profile
RUN echo "" >> /home/tide/.bashrc && \
    echo "# Tide OS" >> /home/tide/.bashrc && \
    echo 'export PS1="🌊 \u@tide-os:\w\$ "' >> /home/tide/.bashrc && \
    echo "alias ll='ls -la'" >> /home/tide/.bashrc && \
    echo "alias la='ls -A'" >> /home/tide/.bashrc && \
    echo "alias ..='cd ..'" >> /home/tide/.bashrc && \
    echo "" >> /home/tide/.bashrc && \
    echo "# Tide AI shortcuts" >> /home/tide/.bashrc && \
    echo "alias tide='tide-chat'" >> /home/tide/.bashrc && \
    echo "alias ttools='tide-tools'" >> /home/tide/.bashrc && \
    echo "alias tmodels='tide-models'" >> /home/tide/.bashrc && \
    echo 'export TIDE_MODEL="'${MODEL}'"' >> /home/tide/.bashrc

# Expose Ollama port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Default command
CMD ["/bin/bash"]
