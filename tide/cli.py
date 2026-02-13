"""
CLI interface - Rich-based
"""
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .agent import Agent
from .config import Config
from .tools.registry import get_registry


console = Console()


def print_banner():
    """Print Tide OS banner"""
    banner = r"""
[bold blue]  _______       _     ___  ____  [/]
[bold blue] |_   _(_) __ _| |   / _ \/ ___| [/] 🌊 [bold cyan]Tide OS v3.0.0[/]
[bold blue]   | | | |/ _` | |  | | | \\___ \ [/] [dim]Professional AI Coding Agent[/]
[bold blue]   | | | | (_| | |__| |_| |___) |[/] [dim]Powered by Ollama[/]
[bold blue]   |_| |_|\\__, |_____\\___/|____/ [/]
[bold blue]          |___/                   [/]
"""
    console.print(banner)


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--model', '-m', help='Model to use (nanbeige, llama3.1, qwen3)')
@click.pass_context
def cli(ctx, config, verbose, model):
    """🌊 Tide OS - Professional AI Coding Agent"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config)
    
    if model:
        if not ctx.obj['config'].set_model(model):
            console.print(f"[red]Unknown model: {model}[/]")
            console.print("[dim]Available: nanbeige, llama3.1, qwen3[/]")
            sys.exit(1)
    
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat, config=config)


@cli.command()
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def chat(ctx, config):
    """Start interactive CLI chat session"""
    print_banner()
    
    try:
        cfg = ctx.obj.get('config', Config(config)) if ctx.obj else Config(config)
        agent = Agent(cfg)
        
        console.print("[dim]Checking Ollama connection...[/]")
        if not agent.check_model():
            console.print("[yellow]⚠️  Model not found. Available models:[/]")
            for model in agent.list_models():
                console.print(f"   • {model}")
            console.print(f"\n[dim]Please pull the model: ollama pull {cfg.model}[/]")
            return
        
        console.print(f"[green]✓ Connected ({cfg.model.split('/')[-1]})[/]")
        console.print("[dim]Type 'exit' or 'quit' to exit, 'help' for commands\n[/]")
        
        while True:
            try:
                user_input = console.input("[bold blue]➜[/] ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('exit', 'quit', 'q'):
                    console.print("[dim]Goodbye! 👋[/]")
                    break
                
                if user_input.lower() == 'help':
                    print_help()
                    continue
                
                if user_input.lower() == 'clear':
                    agent.reset()
                    console.print("[dim]Conversation cleared[/]")
                    continue
                
                if user_input.lower() == 'tools':
                    print_tools()
                    continue
                
                if user_input.lower().startswith('model '):
                    alias = user_input[6:].strip()
                    if cfg.set_model(alias):
                        model_info = cfg.get_model_info(alias)
                        console.print(f"[green]✓ Switched to {alias}[/]")
                        if model_info:
                            console.print(f"[dim]  {model_info['name']}[/]")
                        agent = Agent(cfg)
                    else:
                        console.print(f"[red]✗ Unknown model: {alias}[/]")
                        console.print(f"[dim]  Available: {', '.join(cfg.models.keys())}[/]")
                    continue
                
                # Process message with tool handling
                with console.status("[bold cyan]🤔 Thinking...", spinner="dots"):
                    result = agent.chat(user_input)
                
                # Handle tool confirmation
                if result.get("needs_confirmation"):
                    tool_name = result.get("tool_name")
                    params = result.get("tool_params", {})
                    
                    console.print(f"\n[yellow]⚠️  Tool Confirmation Required[/]")
                    console.print(f"   Tool: [cyan]{tool_name}[/]")
                    console.print(f"   Parameters: {params}")
                    
                    confirm = console.input("\nExecute? [y/N]: ").strip().lower()
                    
                    if confirm in ('y', 'yes'):
                        with console.status("[bold cyan]🔧 Executing...", spinner="dots"):
                            tool_result = agent.execute_confirmed_tool({
                                "tool": tool_name,
                                "params": params
                            })
                        
                        if tool_result.success:
                            console.print(f"[green]✅ Success:[/] {tool_result.output[:200]}")
                            
                            # Get follow-up response
                            with console.status("[bold cyan]💬 Getting response...", spinner="dots"):
                                agent.session.add_message("assistant", f"Using tool: {tool_name}")
                                agent.session.add_message("tool", tool_result.output)
                                follow_up = agent.client.chat(
                                    model=agent.config.model,
                                    messages=agent.session.messages
                                )
                                response = follow_up.content
                                agent.session.add_message("assistant", response)
                        else:
                            console.print(f"[red]❌ Error:[/] {tool_result.error}")
                            response = f"Tool failed: {tool_result.error}"
                    else:
                        console.print("[dim]Cancelled[/]")
                        response = "Tool execution cancelled by user."
                else:
                    response = result.get("response", "No response")
                
                # Print response
                console.print(f"\n[bold cyan]● Tide[/]")
                console.print(Panel(response, border_style="cyan", padding=(0, 1)))
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted. Type 'exit' to quit.[/]")
                continue
            except EOFError:
                break
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def tui(ctx, config):
    """Launch TUI interface"""
    try:
        from .ui.app import run_tui
        cfg = ctx.obj.get('config', Config(config)) if ctx.obj else Config(config)
        run_tui(cfg)
    except ImportError as e:
        console.print(f"[red]TUI not available: {e}[/]")
        console.print("[dim]Falling back to CLI mode...[/]")
        ctx.invoke(chat, config=config)


@cli.command()
def tools():
    """List all available tools"""
    print_banner()
    print_tools()


def print_tools():
    """Print tools in a nice table"""
    registry = get_registry()
    tools_by_cat = registry.get_tools_by_category()
    
    console.print("\n[bold]Available Tools[/]\n")
    
    for category, tools in sorted(tools_by_cat.items()):
        console.print(f"[bold yellow]{category.upper()}[/]")
        
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Confirm", style="dim")
        
        for tool in sorted(tools, key=lambda t: t['name']):
            confirm = "⚠️" if tool['require_confirmation'] else ""
            table.add_row(tool['name'], tool['description'], confirm)
        
        console.print(table)
        console.print()


@cli.command('show-config')
@click.pass_context
def show_config(ctx):
    """Show current configuration"""
    cfg = ctx.obj.get('config', Config()) if ctx.obj else Config()
    
    console.print("\n[bold cyan]⚙️  Configuration[/]\n")
    
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Model", f"[green]{cfg.model}[/]")
    table.add_row("Ollama Host", cfg.ollama_host)
    table.add_row("Ollama Timeout", f"{cfg.ollama_timeout}s")
    
    console.print(table)
    
    console.print("\n[bold]Configured Models:[/]")
    for alias, info in cfg.models.items():
        current = " [green](current)" if info['name'] == cfg.model else ""
        console.print(f"  • [cyan]{alias}[/]: {info['description']}{current}")


@cli.command()
@click.option('--set', 'set_model', help='Set model by alias')
@click.pass_context
def models(ctx, set_model):
    """List and manage models"""
    print_banner()
    
    cfg = ctx.obj.get('config', Config()) if ctx.obj else Config()
    
    if set_model:
        if cfg.set_model(set_model):
            console.print(f"[green]✓ Model set to: {set_model}[/]")
            model_info = cfg.get_model_info(set_model)
            if model_info:
                console.print(f"  [dim]{model_info['name']}[/]")
        else:
            console.print(f"[red]✗ Unknown model alias: {set_model}[/]")
            console.print("\n[dim]Available aliases:[/]")
            for alias in cfg.models.keys():
                console.print(f"  • {alias}")
        return
    
    console.print("\n[bold cyan]🤖 Configured Models[/]\n")
    
    table = Table(show_header=True, box=box.ROUNDED)
    table.add_column("Alias", style="cyan", no_wrap=True)
    table.add_column("Model", style="green")
    table.add_column("Description", style="white")
    table.add_column("Size", style="dim")
    
    current = cfg.model
    
    for alias, info in cfg.models.items():
        is_current = info['name'] == current
        marker = "▶ " if is_current else "  "
        size = info.get('size', '?')
        
        table.add_row(
            f"{marker}{alias}",
            info['name'][:50] + "..." if len(info['name']) > 50 else info['name'],
            info.get('description', ''),
            size
        )
    
    console.print(table)
    console.print(f"\n[bold]Current:[/] [green]{current}[/]")


@cli.command()
@click.argument('message')
@click.pass_context
def ask(ctx, message):
    """Send a single message and get response"""
    try:
        cfg = ctx.obj.get('config', Config()) if ctx.obj else Config()
        agent = Agent(cfg)
        
        result = agent.chat(message, auto_confirm=True)
        console.print(result.get("response", "No response"))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


def print_help():
    """Print help information"""
    help_text = """
[bold]Available Commands:[/]

[bold cyan]During chat:[/]
  [cyan]help[/]       - Show this help
  [cyan]tools[/]      - List available tools
  [cyan]clear[/]      - Clear conversation history
  [cyan]model NAME[/] - Change model (nanbeige, llama3.1, qwen3)
  [cyan]exit/quit[/]  - Exit the chat

[bold cyan]CLI Commands:[/]
  [cyan]tide[/]            - Start interactive chat
  [cyan]tide tools[/]      - List all tools
  [cyan]tide models[/]     - List and manage models
  [cyan]tide show-config[/]- Show configuration
  [cyan]tide ask "..."[/]  - Send a single message

[bold cyan]Examples:[/]
  tide
  tide -m nanbeige
  tide models --set llama3.1
  tide ask "List all Python files"
"""
    console.print(Panel(help_text, title="Help", border_style="cyan"))


def main():
    """Entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted[/]")
        sys.exit(0)


if __name__ == '__main__':
    main()
