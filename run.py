#!/usr/bin/env python3
"""
Tide - AI-Powered Coding Agent
Launcher script
"""

import sys
import os

# Add tide to path
current_dir = os.path.dirname(os.path.abspath(__file__))
tide_dir = os.path.join(current_dir, 'tide')

if tide_dir not in sys.path:
    sys.path.insert(0, tide_dir)

try:
    from internal.ui.app import TideApp
    from internal.config.settings import Settings

    def main():
        """Main entry point"""
        try:
            settings = Settings()
            app = TideApp(settings)
            app.run()
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing Tide components: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)
