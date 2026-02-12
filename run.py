#!/usr/bin/env python3
"""
Tide - AI-Powered Coding Agent
Launcher script
"""

import sys
import os

# Add tide to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tide'))
sys.path.insert(0, os.path.dirname(__file__))

from tide.cmd.main import main

if __name__ == "__main__":
    main()
