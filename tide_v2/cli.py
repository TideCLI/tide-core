"""
Tide v2 CLI - Professional command-line interface
Based on crush's architecture with Ollama integration
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.tree import Tree
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.status import Status

from .agent import TideAgent
from .tools.base import ToolResult


console = Console()


def show_banner():
    """Show Tide banner"""
    banner = """
[bold blue]╔═══════════════════════════════════════════════════════════════╗[/bold blue]
[bold blue]║                                                               ║[/bold blue]
[bold blue]║[/bold blue]   [bold white]🌊[/bold white] [bold cyan]Tide v2[/bold cyan] - [white]Professional AI Coding Agent[/white]              [bold blue]║[/bold blue]
[bold blue]║[/bold blue]                                                                [bold blue]║[/bold blue]
[bold blue]║[/bold blue]   Powered by [green]Ollama[/green] • Based on [purple]charmbracelet/crush[/purple]       [bold blue]║[/bold blue]
[bold blue]║[/bold blue]                                                                [bold blue]║[/bold blue]
[bold blue]╚═══════════════════════════════════════════════════════════════╝[/bold blue]
"""
    console.print(banner)


def show_tools_table(agent: TideAgent):
    """Show available tools in a table"""
    table = Table(title="🔧 Available Tools", box=box.ROUNDED)
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="white")
    table.add_column("Confirmation", style="dim")
    
    for name in agent.get_available_tools():
        info = agent.get_tool_info(name)
        if info:
            table.add_row(
                name,
                info.get("category", ""),
                info.get("description", "")[:45] + "...",
                "✓" if info.get("requires_confirmation") else ""
            )
    
    console.print(table)


def interactive_mode(agent: TideAgent):
    """Interactive chat mode"""
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("[dim]Type 'help' for commands, 'exit' to quit\n[/dim]")
    
    while True:
        try:
            # Get input
            user_input = Prompt.ask("[bold green]➜[/bold green]").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[dim]👋 Goodbye![/dim]\n")
                break
            
            elif user_input.lower() == 'help':
                show_help()
                continue
            
            elif user_input.lower() == 'tools':
                show_tools_table(agent)
                continue
            
            elif user_input.lower().startswith('tool '):
                # Direct tool execution
                parts = user_input[5:].split(maxsplit=1)
                if len(parts) >= 1:
                    tool_name = parts[0]
                    params_str = parts[1] if len(parts) > 1 else "{}"
                    try:
                        import json
                        params = json.loads(params_str)
                        
                        with Status(f"[bold blue]Running {tool_name}...[/bold blue]", spinner="dots"):
                            result = agent.execute_tool_directly(tool_name, params)
                        
                        if result.success:
                            console.print(Panel(
                                result.output[:2000],
                                title=f"✅ {tool_name}",
                                border_style="green"
                            ))
                        else:
                            console.print(Panel(
                                result.error,
                                title=f"❌ {tool_name}",
                                border_style="red"
                            ))
                    except json.JSONDecodeError:
                        console.print("[red]Invalid JSON parameters[/red]")
                continue
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                console.print("[dim]History cleared[/dim]")
                continue
            
            elif user_input.lower() == 'stats':
                stats = agent.get_stats()
                console.print(f"Model: {stats['model']}")
                console.print(f"Messages: {stats['messages']}")
                console.print(f"Tools: {stats['tools']['total_tools']}")
                continue
            
            # Regular chat
            with Status("[bold blue]🤔 Thinking...[/bold blue]", spinner="dots"):
                response = agent.chat(user_input)
            
            # Show response
            if response.tool_calls:
                console.print(f"\n[dim]Tools used: {', '.join(response.tools_used)}[/dim]")
            
            console.print(Panel(
                Markdown(response.content),
                title="[bold blue]● Tide[/bold blue]",
                border_style="blue",
                box=box.ROUNDED
            ))
            
        except KeyboardInterrupt:
            console.print("\n\n[dim]👋 Goodbye![/dim]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


def show_help():
    """Show help information"""
    help_text = """
[bold cyan]Tide v2 Commands[/bold cyan]

[bold]Chat Commands:[/bold]
  Just type your message to chat with AI

[bold]Special Commands:[/bold]
  [bold]tools[/bold]              - List all available tools
  [bold]tool <name> {...}[/bold]  - Execute tool directly (e.g., tool ls {"path": "."})
  [bold]clear[/bold]             - Clear chat history
  [bold]stats[/bold]             - Show agent statistics
  [bold]help[/bold]              - Show this help
  [bold]exit[/bold]              - Quit Tide

[bold]Examples:[/bold]
  [dim]> analyze the code in agent.py[/dim]
  [dim]> tool view {"file_path": "README.md"}[/dim]
  [dim]> tool bash {"command": "ls -la"}[/dim]
    """
    console.print(help_text)


def quick_chat(agent: TideAgent, message: str):
    """Single message chat"""
    with Status("[bold blue]🤔 Thinking...[/bold blue]", spinner="dots"):
        response = agent.chat(message)
    
    console.print(Markdown(response.content))
    
    if response.tool_calls:
        console.print(f"\n[dim]Tools used: {', '.join(response.tools_used)}[/dim]")


def check_ollama():
    """Check if Ollama is running"""
    from .ollama_client import OllamaClient
    
    client = OllamaClient()
    if not client.check_connection():
        console.print("[red]❌ Cannot connect to Ollama![/red]")
        console.print("\n[yellow]Please make sure Ollama is running:[/yellow]")
        console.print("  [dim]ollama serve[/dim]")
        return False
    
    models = client.list_models()
    if not models:
        console.print("[yellow]⚠️  No models found in Ollama[/yellow]")
        console.print("\n[dim]Pull a model first:[/dim]")
        console.print("  [dim]ollama pull qwen3:latest[/dim]")
        return False
    
    console.print(f"[green]✓[/green] Connected to Ollama ({len(models)} models available)")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Tide v2 - Professional AI Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tide-v2                          # Start interactive mode
  tide-v2 "analyze agent.py"       # Quick chat
  tide-v2 --model codellama        # Use specific model
  tide-v2 --model llama3.1:8b      # Use Llama 3.1 8B
  tide-v2 --select-model           # Interactive model selection
  tide-v2 --tools                  # List all tools
  tide-v2 --models                 # List available AI models
        """
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="Message to send (if omitted, starts interactive mode)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Ollama model to use (e.g., llama3.1:8b, qwen3, codellama)"
    )
    parser.add_argument(
        "--select-model",
        action="store_true",
        help="Interactive model selection"
    )
    parser.add_argument(
        "--models",
        action="store_true",
        help="List available AI models"
    )
    parser.add_argument(
        "--tools",
        action="store_true",
        help="List all available tools"
    )
    parser.add_argument(
        "--working-dir",
        default=".",
        help="Working directory (default: current)"
    )
    
    args = parser.parse_args()
    
    # Show banner
    show_banner()
    
    # Handle --models (list available models)
    if args.models:
        from .ollama_client import OllamaClient
        client = OllamaClient.__new__(OllamaClient)
        models = client.list_models()
        
        console.print("\n[bold cyan]🤖 Available AI Models[/bold cyan]\n")
        
        if models:
            table = Table(title="Installed Models", box=box.ROUNDED)
            table.add_column("Model", style="green")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Status", style="yellow")
            
            for model in models:
                info = OllamaClient.RECOMMENDED_MODELS.get(model, {})
                name = info.get("name", model)
                desc = info.get("description", "Custom model")
                status = "✓ Recommended" if info.get("recommended") else ""
                table.add_row(model, name, desc, status)
            
            console.print(table)
            
            # Show how to use
            console.print("\n[dim]Use with: tide-v2 --model <model_name>[/dim]")
            console.print("[dim]Or: TIDE_MODEL=<model_name> tide-v2[/dim]\n")
        else:
            console.print("[yellow]No models installed![/yellow]")
            console.print("\nInstall a model:")
            console.print("  ollama pull llama3.1:8b")
            console.print("  ollama pull qwen3:latest")
            console.print("  ollama pull codellama:latest\n")
        
        return 0
    
    # Handle --select-model (interactive selection)
    if args.select_model:
        from .ollama_client import OllamaClient
        client = OllamaClient.__new__(OllamaClient)
        
        # Temporarily create client to use selection
        import os
        os.environ['OLLAMA_HOST'] = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
        # Show interactive selection
        from .config.settings import Settings
        settings = Settings()
        selected_model = settings.select_model_interactive()
        
        # Save to config
        settings.model = selected_model
        settings.save()
        
        console.print(f"\n[green]✓ Selected model: {selected_model}[/green]")
        console.print(f"[dim]Saved to: {settings.config_file}[/dim]\n")
        return 0
    
    # Check Ollama
    if not check_ollama():
        return 1
    
    # Get model from args or use default
    model = args.model
    if not model:
        # Try to get from config or environment
        from .config.settings import Settings
        settings = Settings()
        model = settings.model
    
    # Initialize agent with selected model
    try:
        console.print(f"[dim]Using model: {model}[/dim]\n")
        agent = TideAgent(model=model, working_dir=args.working_dir)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {e}[/red]")
        return 1
    
    # Handle --tools
    if args.tools:
        show_tools_table(agent)
        return 0
    
    # Handle message or interactive mode
    if args.message:
        quick_chat(agent, args.message)
    else:
        interactive_mode(agent)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
