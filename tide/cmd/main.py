#!/usr/bin/env python3
"""
Tide - AI-Powered Coding Agent
Main entry point
"""

import sys
import os

# Add tide to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from internal.ui.app import TideApp
from internal.config.settings import Settings

def main():
    """Main entry point"""
    settings = Settings()
    app = TideApp(settings)
    app.run()

if __name__ == "__main__":
    main()
