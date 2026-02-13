"""Configuration management - inspired by crush's config system"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    Configuration management with file-based loading.
    
    Priority (highest to lowest):
        1. .tide.json (current directory, hidden)
        2. tide.json (current directory)
        3. ~/.config/tide/config.json (global config)
        4. Built-in defaults
    """
    
    DEFAULT_CONFIG: Dict[str, Any] = {
        "model": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
        "ollama": {
            "host": "http://localhost:11434",
            "timeout": 120,
            "stream": True
        },
        "models": {
            "nanbeige": {
                "name": "hf.co/Edge-Quant/Nanbeige4.1-3B-Q4_K_M-GGUF:Q4_K_M",
                "description": "Edge-Quant Nanbeige 4.1 3B - Fast & Efficient (2.4GB)",
                "size": "2.4 GB",
                "recommended": True,
                "speed": "fast",
                "provider": "ollama"
            },
            "llama3.1": {
                "name": "llama3.1:8b",
                "description": "Llama 3.1 8B - High Quality (4.9GB)",
                "size": "4.9 GB",
                "recommended": True,
                "speed": "medium",
                "provider": "ollama"
            },
            "qwen3": {
                "name": "qwen3:latest",
                "description": "Qwen 3 - Latest Generation",
                "size": "Variable",
                "recommended": True,
                "speed": "medium",
                "provider": "ollama"
            },
            "minimax-25": {
                "name": "MiniMax-M2.5",
                "description": "MiniMax M2.5 - AI Coding (Coding Plan)",
                "size": "API",
                "recommended": False,
                "speed": "fast",
                "provider": "minimax"
            }
        },
        "tools": {
            "bash": {
                "require_confirmation": True,
                "timeout": 30,
                "banned_commands": [
                    "rm -rf /", "mkfs", "dd", "format",
                    ":(){ :|:& };:", "> /dev/sda"
                ]
            },
            "ls": {
                "max_depth": 5,
                "max_files": 1000,
                "ignore": [".git", "node_modules", "__pycache__", ".venv", ".tox"]
            },
            "edit": {
                "create_backup": True,
                "show_diff": True
            },
            "grep": {
                "max_results": 100,
                "context_lines": 3
            }
        },
        "ui": {
            "theme": "blue",
            "syntax_theme": "monokai",
            "show_line_numbers": True,
            "compact_mode": False
        },
        "permissions": {
            "confirm_write": True,
            "confirm_delete": True,
            "confirm_bash": True,
            "allow_outside_working_dir": False
        }
    }
    
    def __init__(self, path: Optional[str] = None):
        self._data = {}
        if path:
            self._load_from_file(path)
        else:
            self._load_default()
    
    def _load_default(self) -> None:
        """Load config following priority order"""
        self._data = self.DEFAULT_CONFIG.copy()
        
        # Priority 3: Global config
        global_config = Path.home() / ".config" / "tide" / "config.json"
        if global_config.exists():
            self._merge_config(global_config)
        
        # Priority 2: tide.json in current dir
        local_config = Path("tide.json")
        if local_config.exists():
            self._merge_config(local_config)
        
        # Priority 1: .tide.json (hidden) in current dir
        hidden_config = Path(".tide.json")
        if hidden_config.exists():
            self._merge_config(hidden_config)
    
    def _load_from_file(self, path: str) -> None:
        """Load config from specific file"""
        self._data = self.DEFAULT_CONFIG.copy()
        self._merge_config(Path(path))
    
    def _merge_config(self, path: Path) -> None:
        """Merge config file into current data"""
        try:
            with open(path, 'r') as f:
                user_config = json.load(f)
            self._deep_merge(self._data, user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge two dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot notation (e.g., 'tools.bash.timeout')"""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def model(self) -> str:
        return self._data.get("model", "llama3.1:8b")
    
    @property
    def ollama_host(self) -> str:
        return self._data.get("ollama", {}).get("host", "http://localhost:11434")
    
    @property
    def ollama_timeout(self) -> int:
        return self._data.get("ollama", {}).get("timeout", 120)
    
    @property
    def tool_config(self, tool_name: str) -> Dict[str, Any]:
        return self._data.get("tools", {}).get(tool_name, {})
    
    @property
    def models(self) -> Dict[str, Dict[str, Any]]:
        """Get configured models"""
        return self._data.get("models", {})
    
    def get_model_info(self, alias: str) -> Optional[Dict[str, Any]]:
        """Get model info by alias (nanbeige, llama3.1, qwen3)"""
        return self._data.get("models", {}).get(alias)
    
    def set_model(self, alias: str) -> bool:
        """Set current model by alias"""
        models = self._data.get("models", {})
        if alias in models:
            self._data["model"] = models[alias]["name"]
            return True
        return False
    
    def add_model(self, alias: str, name: str, description: str = "", 
                  size: str = "", recommended: bool = False, speed: str = "medium") -> None:
        """Add a new model to configuration"""
        if "models" not in self._data:
            self._data["models"] = {}
        
        self._data["models"][alias] = {
            "name": name,
            "description": description,
            "size": size,
            "recommended": recommended,
            "speed": speed
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Return full config as dictionary"""
        return self._data.copy()
    
    def save(self, path: str) -> None:
        """Save current config to file"""
        with open(path, 'w') as f:
            json.dump(self._data, f, indent=2)
