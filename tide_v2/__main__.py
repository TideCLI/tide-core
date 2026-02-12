#!/usr/bin/env python3
"""
Tide v2 - Main entry point
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tide_v2.cli import main

if __name__ == "__main__":
    sys.exit(main())
