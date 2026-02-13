"""
Model Manager - Download and manage Ollama models
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


class ModelManager:
    """Manages Ollama model downloads and operations"""
    
    RECOMMENDED_MODELS = {
        "qwen3:latest": {
            "name": "Qwen 3",
            "description": "Fast, capable multilingual model - recommended for Tide OS",
            "size": "~4.7GB",
            "category": "general",
            "recommended": True
        },
        "llama3.1:8b": {
            "name": "Llama 3.1 8B", 
            "description": "Meta's latest instruction-following model",
            "size": "~4.9GB",
            "category": "general",
            "recommended": True
        },
        "codellama:7b": {
            "name": "CodeLlama 7B",
            "description": "Specialized for code generation and understanding",
            "size": "~3.8GB",
            "category": "coding",
            "recommended": True
        },
        "mistral:7b": {
            "name": "Mistral 7B",
            "description": "Balanced performance for various tasks",
            "size": "~4.1GB",
            "category": "general",
            "recommended": False
        },
        "phi3:mini": {
            "name": "Phi-3 Mini",
            "description": "Lightweight and efficient model",
            "size": "~2.3GB",
            "category": "lightweight",
            "recommended": False
        },
        "llama3:8b": {
            "name": "Llama 3 8B",
            "description": "Previous generation Llama model",
            "size": "~4.9GB",
            "category": "general",
            "recommended": False
        },
        "nomic-embed-text:latest": {
            "name": "Nomic Embed Text",
            "description": "High-quality text embeddings",
            "size": "~274MB",
            "category": "embeddings",
            "recommended": False
        },
    }
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.ollama_path = self._find_ollama()
        
    def _find_ollama(self) -> str:
        """Find ollama executable"""
        # Check PATH
        path = shutil.which("ollama")
        if path:
            return path
            
        # Common locations
        common_paths = [
            "/usr/bin/ollama",
            "/usr/local/bin/ollama",
            "~/.local/bin/ollama",
            "/opt/ollama/bin/ollama"
        ]
        
        for p in common_paths:
            expanded = os.path.expanduser(p)
            if os.path.exists(expanded):
                return expanded
                
        return "ollama"  # Fallback
        
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.ollama_host}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
            
    def list_installed_models(self) -> List[Dict]:
        """List installed models"""
        try:
            import urllib.request
            import json
            req = urllib.request.Request(f"{self.ollama_host}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data.get("models", [])
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
            
    def pull_model(self, model_name: str, progress: bool = True) -> Dict:
        """Pull a model from Ollama registry"""
        print(f"Pulling model: {model_name}")
        
        try:
            cmd = [self.ollama_path, "pull", model_name]
            if progress:
                result = subprocess.run(cmd, capture_output=False, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            if result.returncode == 0:
                return {"success": True, "model": model_name}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def remove_model(self, model_name: str) -> Dict:
        """Remove a model"""
        try:
            cmd = [self.ollama_path, "rm", model_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "model": model_name}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get model information"""
        try:
            cmd = [self.ollama_path, "show", model_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "info": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def run_model_interactive(self, model_name: str):
        """Run model in interactive mode"""
        try:
            cmd = [self.ollama_path, "run", model_name]
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error running model: {e}")
            
    def show_recommended(self):
        """Show recommended models"""
        print("\n📦 Recommended Models for Tide OS:\n")
        
        for name, info in self.RECOMMENDED_MODELS.items():
            recommended = "⭐" if info.get("recommended") else "  "
            print(f"  {recommended} {name}")
            print(f"      {info['description']}")
            print(f"      Size: {info['size']}")
            print()
            
    def auto_setup(self):
        """Auto-setup: install recommended models"""
        print("\n🚀 Auto-setting up Tide OS models...\n")
        
        # Install recommended model if none exist
        models = self.list_installed_models()
        
        if not models:
            print("No models found. Installing recommended model...")
            result = self.pull_model("qwen3:latest")
            
            if result["success"]:
                print("✓ Successfully installed qwen3:latest")
            else:
                print(f"✗ Failed: {result.get('error')}")
        else:
            print(f"✓ Found {len(models)} installed models")


import shutil
