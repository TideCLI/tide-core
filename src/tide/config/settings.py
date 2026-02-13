"""
Tide OS Configuration Settings
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Settings:
    """Tide OS Settings Manager"""
    
    DEFAULT_CONFIG = {
        "model": "qwen3:latest",
        "ollama_host": "http://localhost:11434",
        "timeout": 120,
        "temperature": 0.7,
        "max_tokens": 4096,
        "auto_setup": True,
        "show_banner": True,
        "color_scheme": "default",
        "tools": {
            "bash": {
                "require_confirmation": True,
                "timeout": 30,
                "banned_commands": ["rm -rf /", "dd if=", ":(){:|:&};:", "mkfs", "fdisk"]
            },
            "edit": {
                "require_confirmation": True,
                "max_file_size": 5242880  # 5MB
            },
            "view": {
                "max_file_size": 5242880,
                "show_line_numbers": True
            }
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.environ.get(
            "TIDE_CONFIG",
            str(Path.home() / ".config" / "tide" / "settings.json")
        )
        self._config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        config = self.DEFAULT_CONFIG.copy()
        
        # Try to load from file
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception:
                pass
                
        # Override with environment variables
        if "TIDE_MODEL" in os.environ:
            config["model"] = os.environ["TIDE_MODEL"]
        if "OLLAMA_HOST" in os.environ:
            config["ollama_host"] = os.environ["OLLAMA_HOST"]
            
        return config
    
    def save(self):
        """Save configuration to file"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, "w") as f:
            json.dump(self._config, f, indent=2)
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default
        
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def to_dict(self) -> Dict:
        """Return configuration as dict"""
        return self._config.copy()
        
    def select_model_interactive(self) -> str:
        """Interactive model selection"""
        from rich.console import Console
        from rich.prompt import Prompt
        
        console = Console()
        
        # Get available models
        from ..utils.ollama_client import OllamaClient
        client = OllamaClient()
        installed = client.list_models()
        
        console.print("\n[bold cyan]Select AI Model:[/bold cyan]\n")
        
        # Show recommended models
        options = list(self.RECOMMENDED_MODELS.keys())
        
        for i, model in enumerate(options, 1):
            info = self.RECOMMENDED_MODELS[model]
            installed_mark = "✓" if model in installed else ""
            recommended = "⭐" if info.get("recommended") else ""
            console.print(f"  {i}. {model} {installed_mark} {recommended}")
            console.print(f"     {info['description']}\n")
            
        choice = Prompt.ask(
            "Enter number or model name",
            default="1"
        )
        
        # Parse choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
                
        # Check if it's a model name
        if choice in options:
            return choice
            
        return self.DEFAULT_CONFIG["model"]
        
    RECOMMENDED_MODELS = {
        "qwen3:latest": {
            "name": "Qwen 3",
            "description": "Fast, capable multilingual model - recommended",
            "recommended": True
        },
        "llama3.1:8b": {
            "name": "Llama 3.1 8B", 
            "description": "Meta's latest instruction-following model",
            "recommended": True
        },
        "codellama:7b": {
            "name": "CodeLlama 7B",
            "description": "Specialized for code generation",
            "recommended": False
        },
    }
    
    @property
    def model(self) -> str:
        return self._config.get("model", "qwen3:latest")
    
    @model.setter
    def model(self, value: str):
        self._config["model"] = value
        self.save()
        
    @property
    def ollama_host(self) -> str:
        return self._config.get("ollama_host", "http://localhost:11434")
    
    @ollama_host.setter
    def ollama_host(self, value: str):
        self._config["ollama_host"] = value
        self.save()
