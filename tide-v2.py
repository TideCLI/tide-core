#!/usr/bin/env python3
"""
Tide v2 Launcher
Professional AI Coding Agent based on charmbracelet/crush
"""

import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tide_v2.cli import main
    sys.exit(main())
