#!/usr/bin/env python3
"""
Tide OS - Agentic TUI Interface
A beautiful, interactive terminal user interface for Tide AI Agent
Powered by Ollama for local LLM inference
"""

import os
import sys
import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.tree import Tree
from rich import box
from rich.style import Style
from rich.colors import Color

from tide.agents.agent import TideAgent
from tide.config.settings import Settings
from tide.utils.model_manager import ModelManager


console = Console()


# Color scheme for Tide OS
TIDE_COLORS = {
    "primary": "#00D4FF",      # Cyan
    "secondary": "#7B68EE",     # Purple
    "accent": "#00FF88",       # Green
    "warning": "#FFB347",      # Orange
    "error": "#FF6B6B",        # Red
    "background": "#0D1117",   # Dark
    "surface": "#161B22",      # Darker
    "text": "#E6EDF3",         # Light gray
    "muted": "#8B949E",        # Gray
}


class TideTUI:
    """Main TUI class for Tide OS"""
    
    def __init__(self):
        self.console = Console()
        self.settings = Settings()
        self.model_manager = ModelManager()
        self.agent: Optional[TideAgent] = None
        self.chat_history: List[Dict[str, str]] = []
        self.running = True
        
    def show_banner(self):
        """Display the Tide OS banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    [cyan]🌊[/cyan]  [bold white]Tide OS[/bold white] - [bold cyan]Agentic AI Terminal[/bold cyan]                        [cyan]🌊[/cyan]   ║
║                                                                              ║
║    [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]  ║
║                                                                              ║
║       [green]●[/green] Local AI [dim]•[/dim] Privacy First [dim]•[/dim] Offline Ready                           ║
║       [green]●[/green] Powered by [purple]Ollama[/purple] [dim]•[/dim] Open Source [dim]•[/dim] No Cloud Required                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        self.console.print(banner)
        
    def show_welcome(self):
        """Show welcome message"""
        welcome = """
[bold cyan]Welcome to Tide OS![/bold cyan]

[dim]Tide OS is your local AI-powered coding assistant.[/dim]

[yellow]Quick Commands:[/yellow]
  [green]chat[/green] <message>   - Chat with AI
  [green]models[/green]           - Manage AI models
  [green]pull[/green] <model>     - Download a model
  [green]tools[/green]            - List available tools
  [green]config[/green]           - Configure settings
  [green]clear[/green]            - Clear chat history
  [green]help[/green]             - Show this help
  [green]quit[/green]             - Exit Tide OS

[dim]Type your message to start chatting with AI![/dim]
"""
        self.console.print(Panel(welcome, title="🌊 Welcome", border_style="cyan"))
        
    async def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            if not self.model_manager.is_ollama_running():
                self.console.print("[red]✗ Ollama is not running![/red]")
                self.console.print("\n[yellow]Start Ollama with:[/yellow]")
                self.console.print("  [dim]ollama serve[/dim]")
                return False
                
            models = self.model_manager.list_installed_models()
            if not models:
                self.console.print("[yellow]⚠ No models installed![/yellow]")
                self.console.print("\n[dim]Download a model:[/dim]")
                self.console.print("  [green]pull qwen3:latest[/green]")
                self.console.print("  [green]pull llama3.1:8b[/green]")
                return False
                
            return True
        except Exception as e:
            self.console.print(f"[red]Error checking Ollama: {e}[/red]")
            return False
            
    def initialize_agent(self):
        """Initialize the Tide Agent"""
        try:
            model = self.settings.model
            self.agent = TideAgent(model=model)
            self.console.print(f"[green]✓[/green] Agent initialized with [cyan]{model}[/cyan]")
        except Exception as e:
            self.console.print(f"[red]Failed to initialize agent: {e}[/red]")
            
    async def handle_models(self):
        """Handle model management"""
        models = self.model_manager.list_installed_models()
        
        table = Table(title="📦 Installed Models", box=box.ROUNDED)
        table.add_column("Model", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Modified", style="dim")
        
        for model in models:
            table.add_row(
                model.get("name", "unknown"),
                model.get("size", "unknown"),
                model.get("modified_at", "unknown")[:19]
            )
            
        self.console.print(table)
        
        # Show recommended models
        self.console.print("\n[bold cyan]📥 Recommended Models:[/bold cyan]")
        for name, info in self.model_manager.RECOMMENDED_MODELS.items():
            self.console.print(f"  [green]{name}[/green] - {info['description']}")
            
    async def handle_pull_model(self, model_name: str):
        """Pull a new model"""
        self.console.print(f"[cyan]Downloading {model_name}...[/cyan]\n")
        
        try:
            with self.console.status("[bold blue]Pulling model...[/bold blue]", spinner="dots"):
                result = self.model_manager.pull_model(model_name)
                
            if result.get("success"):
                self.console.print(f"\n[green]✓ Successfully pulled {model_name}[/green]")
            else:
                self.console.print(f"\n[red]✗ Failed to pull model: {result.get('error')}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            
    def handle_tools(self):
        """Show available tools"""
        if not self.agent:
            self.console.print("[red]Agent not initialized[/red]")
            return
            
        tools = self.agent.get_available_tools()
        
        table = Table(title="🔧 Available Tools", box=box.ROUNDED)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Description", style="white")
        
        for tool in tools:
            info = self.agent.get_tool_info(tool)
            if info:
                table.add_row(
                    tool,
                    info.get("category", "general"),
                    info.get("description", "")[:50]
                )
                
        self.console.print(table)
        
    def handle_config(self):
        """Show and edit configuration"""
        config_table = Table(title="⚙️ Tide OS Configuration", box=box.ROUNDED)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="yellow")
        
        config = self.settings.to_dict()
        for key, value in config.items():
            config_table.add_row(key, str(value))
            
        self.console.print(config_table)
        
    async def handle_chat(self, message: str):
        """Handle chat message"""
        if not self.agent:
            self.initialize_agent()
            
        if not self.agent:
            self.console.print("[red]Cannot initialize agent. Is Ollama running?[/red]")
            return
            
        # Add to history
        self.chat_history.append({"role": "user", "content": message})
        
        # Show thinking
        with self.console.status("[bold blue]🤔 Thinking...[/bold blue]", spinner="dots"):
            try:
                response = self.agent.chat(message)
                
                # Add to history
                self.chat_history.append({"role": "assistant", "content": response.content})
                
                # Display response
                self.console.print()
                self.console.print(Panel(
                    Markdown(response.content),
                    title="[bold cyan]● Tide[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED
                ))
                
                if response.tools_used:
                    self.console.print(f"\n[dim]Tools used: {', '.join(response.tools_used)}[/dim]")
                    
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                
    async def handle_command(self, cmd: str) -> bool:
        """Handle special commands"""
        parts = cmd.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == "quit" or command == "exit" or command == "q":
            self.console.print("\n[dim]👋 Goodbye from Tide OS![/dim]\n")
            self.running = False
            return True
            
        elif command == "help" or command == "h":
            self.show_welcome()
            return True
            
        elif command == "clear" or command == "c":
            self.chat_history.clear()
            if self.agent:
                self.agent.clear_history()
            self.console.clear()
            self.show_banner()
            return True
            
        elif command == "models" or command == "m":
            await self.handle_models()
            return True
            
        elif command == "pull" and args:
            await self.handle_pull_model(args)
            return True
            
        elif command == "tools" or command == "t":
            self.handle_tools()
            return True
            
        elif command == "config" or command == "cfg":
            self.handle_config()
            return True
            
        elif command == "banner":
            self.show_banner()
            return True
            
        return False
        
    async def run(self):
        """Main run loop"""
        self.show_banner()
        
        # Check Ollama
        if not await self.check_ollama():
            self.console.print("\n[yellow]You can still browse models and configuration.[/yellow]\n")
            
        self.show_welcome()
        
        # Main loop
        while self.running:
            try:
                # Get input
                user_input = Prompt.ask("\n[bold green]➜[/bold green]")
                
                if not user_input.strip():
                    continue
                    
                # Check for special commands
                is_command = await self.handle_command(user_input)
                
                if not is_command:
                    # Regular chat
                    await self.handle_chat(user_input)
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[dim]👋 Goodbye from Tide OS![/dim]\n")
                break
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")


def main():
    """Entry point"""
    tui = TideTUI()
    asyncio.run(tui.run())


if __name__ == "__main__":
    main()
