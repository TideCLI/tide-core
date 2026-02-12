"""
Session Management - Chat history and persistence
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class Session:
    """Chat session"""
    
    def __init__(self, name: str = None):
        self.name = name or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.created_at = datetime.now()
        self.messages: List[Dict] = []
        self.working_dir = Path.cwd()
    
    def add_message(self, role: str, content: str, tools_used: List[str] = None):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tools_used": tools_used or []
        })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "working_dir": str(self.working_dir),
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        """Create from dictionary"""
        session = cls(data["name"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.working_dir = Path(data["working_dir"])
        session.messages = data["messages"]
        return session
    
    def save(self, path: Path):
        """Save session to file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> "Session":
        """Load session from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
