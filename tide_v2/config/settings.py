"""
Tide OS Settings with Model Selection Support
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class Settings:
    """Tide OS Configuration Settings"""
    
    # Default configuration
    DEFAULTS = {
        "model": "qwen3:latest",
        "ollama": {
            "host": "http://localhost:11434",
            "timeout": 120
        },
        "tools": {
            "bash": {
                "require_confirmation": True,
                "timeout": 30
            },
            "ls": {
                "max_depth": 5,
                "max_files": 1000
            },
            "edit": {
                "create_backup": True,
                "show_diff": True
            },
            # Git tools
            "git_status": {
                "require_confirmation": False,
                "timeout": 15
            },
            "git_diff": {
                "require_confirmation": False,
                "timeout": 30,
                "max_output": 30000
            },
            "git_commit": {
                "require_confirmation": True,
                "timeout": 15
            },
            "git_log": {
                "require_confirmation": False,
                "timeout": 15,
                "max_commits": 100
            },
            # Filesystem tools
            "file_move": {
                "require_confirmation": True,
                "allow_overwrite": False
            },
            "file_delete": {
                "require_confirmation": True,
                "protected_paths": [".git", ".env", ".ssh", "node_modules"]
            },
            # Planning tools
            "planner": {
                "require_confirmation": False,
                "persist": True
            },
            "context_manager": {
                "require_confirmation": False,
                "context_window": 8192
            },
            # Memory tools
            "undo": {
                "require_confirmation": False,
                "max_snapshots": 100,
                "snapshot_dir": ".tide/snapshots"
            },
            "session_memory": {
                "require_confirmation": False,
                "persist": True
            },
            "project_index": {
                "require_confirmation": False,
                "cache_ttl": 3600,
                "max_files": 5000
            },
            # Testing tools
            "run_tests": {
                "require_confirmation": False,
                "timeout": 120,
                "auto_detect": True
            },
            "diff_preview": {
                "require_confirmation": False,
                "context_lines": 3
            },
            "code_transform": {
                "require_confirmation": True,
                "timeout": 30
            },
            "error_recovery": {
                "require_confirmation": False,
                "auto_fix": False
            }
        },
        "ui": {
            "theme": "blue",
            "show_line_numbers": True
        }
    }
    
    # Available models with descriptions
    AVAILABLE_MODELS = {
        "llama3.1:8b": {
            "name": "Llama 3.1 (8B)",
            "description": "Best coding performance, large context window",
            "size": "4.9 GB",
            "recommended": True
        },
        "qwen3:latest": {
            "name": "Qwen 3",
            "description": "Excellent code generation and reasoning",
            "size": "4-8 GB",
            "recommended": True
        },
        "codellama:latest": {
            "name": "CodeLlama",
            "description": "Specialized for code tasks",
            "size": "4-8 GB",
            "recommended": True
        },
        "llama3:latest": {
            "name": "Llama 3",
            "description": "General purpose, good reasoning",
            "size": "4-8 GB",
            "recommended": False
        },
        "mistral:latest": {
            "name": "Mistral",
            "description": "Fast and efficient",
            "size": "4-5 GB",
            "recommended": False
        },
        "phi3:latest": {
            "name": "Phi-3",
            "description": "Compact, good for laptops",
            "size": "2-4 GB",
            "recommended": False
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()
        self.model = self._get_model()
        self.ollama_host = self._get_ollama_host()
    
    def _find_config_file(self) -> str:
        """Find configuration file"""
        possible_paths = [
            "tide.json",
            "/home/snoozescript/.config/tide/tide.json",
            "/etc/tide-os/config/tide.json",
            "/opt/tide-os/config/tide.json"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return "tide.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config = self.DEFAULTS.copy()
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        return config
    
    def _get_model(self) -> str:
        """Get model from config or environment"""
        # Priority: Environment > Config > Default
        env_model = os.environ.get('TIDE_MODEL')
        if env_model:
            return env_model
        
        return self.config.get('model', self.DEFAULTS['model'])
    
    def _get_ollama_host(self) -> str:
        """Get Ollama host from config or environment"""
        env_host = os.environ.get('OLLAMA_HOST')
        if env_host:
            return env_host
        
        return self.config.get('ollama', {}).get('host', 
                                                  self.DEFAULTS['ollama']['host'])
    
    def select_model_interactive(self) -> str:
        """Interactive model selection"""
        from ..ollama_client import OllamaClient
        
        print("\n🤖 Select AI Model for Tide OS")
        print("=" * 60)
        
        # Get installed models
        try:
            client = OllamaClient.__new__(OllamaClient)
            client.host = self.ollama_host
            installed = client.list_models()
        except:
            installed = []
        
        print("\n📦 Installed Models:")
        if installed:
            for i, model in enumerate(installed, 1):
                info = self.AVAILABLE_MODELS.get(model, {})
                name = info.get('name', model)
                desc = info.get('description', 'Custom model')
                size = info.get('size', 'Unknown')
                print(f"  {i}. {name}")
                print(f"     Model: {model}")
                print(f"     {desc}")
                print(f"     Size: {size}")
                print()
        else:
            print("  No models found!")
            print("  Run: ollama pull llama3.1:8b")
        
        print("\n⭐ Recommended Models (Install with 'ollama pull <model>'):")
        for model, info in self.AVAILABLE_MODELS.items():
            if info.get('recommended') and model not in installed:
                print(f"  • {info['name']} ({model})")
                print(f"    {info['description']}")
                print(f"    Size: {info['size']}")
                print()
        
        # Selection
        print("=" * 60)
        if installed:
            choice = input(f"Select model (1-{len(installed)}) or enter model name [1]: ").strip()
            
            if not choice:
                return installed[0]
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(installed):
                    return installed[idx]
            
            if choice in installed:
                return choice
            
            # Try to find partial match
            for model in installed:
                if choice.lower() in model.lower():
                    return model
        
        # Default
        return "qwen3:latest"
    
    def save(self):
        """Save configuration to file"""
        self.config['model'] = self.model
        
        try:
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model': self.model,
            'ollama_host': self.ollama_host,
            'config_file': self.config_file
        }
