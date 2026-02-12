"""
Settings and Configuration
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings"""
    
    # Ollama settings
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    model: str = "qwen3:latest"
    
    # Paths
    config_dir: Path = Path.home() / ".tide"
    sessions_dir: Path = Path.home() / ".tide" / "sessions"
    
    def __post_init__(self):
        """Ensure directories exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Override from environment
        self.ollama_host = os.environ.get("OLLAMA_HOST", self.ollama_host)
        self.ollama_port = int(os.environ.get("OLLAMA_PORT", self.ollama_port))
        self.model = os.environ.get("TIDE_MODEL", self.model)
