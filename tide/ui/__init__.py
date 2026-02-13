"""UI components for Tide OS"""
try:
    from .app import TideApp, run_tui
    __all__ = ["TideApp", "run_tui"]
except ImportError:
    # Textual not installed
    __all__ = []
