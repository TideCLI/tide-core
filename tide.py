#!/usr/bin/env python3
"""
Tide OS - Main Launcher
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run CLI
from tide.cli.main import main

if __name__ == "__main__":
    main()
