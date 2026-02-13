#!/usr/bin/env python3
"""
Tide CLI - Command Line Interface
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.table import Table

from tide import TideAgent, Settings, ModelManager
from tide.tui.interface import TideTUI


console = Console()


def show_banner():
    """Show Tide banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🌊  Tide OS - AI-Powered Terminal v2.0.0                                 ║
║                                                                              ║
║    Powered by Ollama • Local AI • Privacy First                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    console.print(banner)


def cmd_chat(args):
    """Chat command"""
    import asyncio
    
    async def run():
        tui = TideTUI()
        if args.message:
            await tui.handle_chat(args.message)
        else:
            await tui.run()
            
    asyncio.run(run())


def cmd_models(args):
    """List models command"""
    mm = ModelManager()
    models = mm.list_installed_models()
    
    table = Table(title="📦 Installed Models")
    table.add_column("Model", style="cyan")
    table.add_column("Size", style="yellow")
    
    for model in models:
        size_gb = model.get("size", 0) / (1024**3)
        table.add_row(model.get("name", "unknown"), f"{size_gb:.1f} GB")
        
    console.print(table)
    

def cmd_pull(args):
    """Pull model command"""
    mm = ModelManager()
    result = mm.pull_model(args.model)
    
    if result["success"]:
        console.print(f"[green]✓ Pulled {args.model}[/green]")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")
        

def cmd_tools(args):
    """List tools command"""
    settings = Settings()
    agent = TideAgent(model=settings.model)
    
    tools = agent.get_available_tools()
    
    table = Table(title="🔧 Available Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="white")
    
    for tool in tools:
        info = agent.get_tool_info(tool)
        if info:
            table.add_row(tool, info.get("category", ""), info.get("description", "")[:50])
            
    console.print(table)


def cmd_config(args):
    """Config command"""
    settings = Settings()
    
    if args.list:
        for key, value in settings.to_dict().items():
            console.print(f"[cyan]{key}[/cyan]: {value}")
    elif args.set:
        key, value = args.set.split("=", 1)
        settings.set(key, value)
        console.print(f"[green]✓ Set {key} = {value}[/green]")
    else:
        # Interactive selection
        model = settings.select_model_interactive()
        settings.model = model
        console.print(f"[green]✓ Selected model: {model}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Tide OS - AI-Powered Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start chat")
    chat_parser.add_argument("message", nargs="?", help="Message to send")
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List installed models")
    
    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Download a model")
    pull_parser.add_argument("model", help="Model name")
    
    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure Tide")
    config_parser.add_argument("--list", action="store_true", help="List config")
    config_parser.add_argument("--set", help="Set config (key=value)")
    
    # TUI command
    tui_parser = subparsers.add_parser("tui", help="Launch TUI (default)")
    
    args = parser.parse_args()
    
    show_banner()
    
    if not args.command or args.command == "tui":
        import asyncio
        asyncio.run(TideTUI().run())
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "pull":
        cmd_pull(args)
    elif args.command == "tools":
        cmd_tools(args)
    elif args.command == "config":
        cmd_config(args)


if __name__ == "__main__":
    main()
