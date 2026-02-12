"""
Main UI Application - IDE-like interface
"""

import sys
from pathlib import Path
from typing import Set, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

from internal.config.settings import Settings
from internal.agent.agent import Agent
from internal.agent.session import Session
from internal.ui.tui_interactive import TideInteractiveTUI


class TideApp:
    """Main application"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.console = Console()
        self.agent: Optional[Agent] = None
        self.session: Optional[Session] = None
        self.selected_files: Set[str] = set()
        self.current_file: Optional[str] = None
        self.working_dir = Path.cwd()
    
    def run(self):
        """Main entry point"""
        self.show_banner()
        
        # Main loop
        while True:
            try:
                self.show_main_menu()
                choice = Prompt.ask("Select", choices=["1", "2", "3", "q"], default="1")
                
                if choice == "1":
                    # Use interactive TUI
                    interactive = TideInteractiveTUI(self.settings)
                    interactive.run()
                elif choice == "2":
                    self.simple_chat()
                elif choice == "3":
                    self.show_tools()
                elif choice == "q":
                    self.console.print("\n[dim]👋 Goodbye![/dim]\n")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[dim]👋 Goodbye![/dim]\n")
                break
    
    def show_banner(self):
        """Show welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗       ║
║   ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝       ║
║      ██║   ██║██║  ██║█████╗      ██║   ██║███████╗       ║
║      ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║       ║
║      ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║       ║
║      ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝       ║
║                                                           ║
║                 🌊 AI-Powered Coding Agent                ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold blue")
    
    def show_main_menu(self):
        """Show main menu"""
        self.console.print("\n[bold cyan]Main Menu[/bold cyan]\n")
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Option", style="green")
        table.add_column("Description", style="white")
        
        table.add_row("1", "🏗️  IDE Interface", "File explorer + Code viewer + Chat")
        table.add_row("2", "💬 Simple Chat", "Basic chat mode")
        table.add_row("3", "🔧 View Tools", "List all available tools")
        table.add_row("q", "❌ Quit", "Exit")
        
        self.console.print(table)
    
    def ide_interface(self):
        """IDE-like interface"""
        self.console.print("\n[bold green]Starting IDE Interface...[/bold green]")
        self.console.print("[dim]Commands: add, remove, open, chat, tools, save, exit[/dim]\n")
        
        while True:
            try:
                # Show current state
                self.show_ide_layout()
                
                # Get command
                cmd = Prompt.ask("\nCommand").strip().lower()
                
                if cmd in ["exit", "quit", "back"]:
                    break
                elif cmd == "add":
                    self.add_file()
                elif cmd == "remove":
                    self.remove_file()
                elif cmd == "open":
                    self.open_file()
                elif cmd == "chat":
                    self.chat_with_files()
                elif cmd == "tools":
                    self.show_tools_list()
                elif cmd == "save":
                    self.save_session()
                elif cmd:
                    # Treat as direct chat
                    self.chat(cmd)
                    
            except KeyboardInterrupt:
                break
    
    def show_ide_layout(self):
        """Show IDE layout"""
        # Build file tree
        tree = self.build_file_tree()
        
        # Show file content if selected
        if self.current_file:
            content = self.read_file(self.current_file)
            try:
                syntax = Syntax(content, "python", line_numbers=True, theme="monokai")
                file_panel = syntax
            except:
                file_panel = content[:1000]
        else:
            file_panel = "[dim]No file selected. Use 'open' to view a file.[/dim]"
        
        # Show selected files
        selected_text = "\n".join([f"✓ {f}" for f in sorted(self.selected_files)]) or "[dim]No files in context[/dim]"
        
        # Layout
        self.console.print(Panel(tree, title="📁 Files", border_style="cyan", width=40))
        self.console.print(Panel(selected_text, title="📌 Context", border_style="yellow"))
        self.console.print(Panel(file_panel, title=f"📄 {self.current_file or 'Editor'}", border_style="green"))
    
    def build_file_tree(self) -> Tree:
        """Build file tree"""
        tree = Tree(f"📁 {self.working_dir.name}")
        
        try:
            for item in sorted(self.working_dir.iterdir())[:15]:
                if item.name.startswith('.'):
                    continue
                
                icon = "📁" if item.is_dir() else self.get_icon(item.name)
                style = "bold yellow" if item.name in self.selected_files else None
                
                if item.is_dir():
                    branch = tree.add(f"{icon} {item.name}/", style=style)
                    try:
                        for sub in sorted(item.iterdir())[:3]:
                            branch.add(f"{self.get_icon(sub.name)} {sub.name}")
                    except:
                        pass
                else:
                    tree.add(f"{icon} {item.name}", style=style)
        except:
            pass
        
        return tree
    
    def get_icon(self, filename: str) -> str:
        """Get file icon"""
        ext = Path(filename).suffix.lower()
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.json': '📋',
            '.md': '📝', '.txt': '📄', '.yml': '⚙️', '.yaml': '⚙️',
            '.sh': '⚡', '.html': '🌐', '.css': '🎨'
        }
        return icons.get(ext, '📄')
    
    def read_file(self, filepath: str) -> str:
        """Read file content"""
        try:
            path = self.working_dir / filepath
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return "Error reading file"
    
    def add_file(self):
        """Add file to context"""
        files = [f.name for f in self.working_dir.iterdir() if f.is_file()]
        
        self.console.print("\n[dim]Available files:[/dim]")
        for i, f in enumerate(files, 1):
            status = "✓" if f in self.selected_files else " "
            self.console.print(f"  [{status}] {i}. {f}")
        
        choice = Prompt.ask("File number or name")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                self.selected_files.add(files[idx])
                self.console.print(f"[green]✓ Added {files[idx]}[/green]")
        except:
            if choice in files:
                self.selected_files.add(choice)
    
    def remove_file(self):
        """Remove file from context"""
        if not self.selected_files:
            self.console.print("[yellow]No files selected[/yellow]")
            return
        
        files = sorted(self.selected_files)
        for i, f in enumerate(files, 1):
            self.console.print(f"  {i}. {f}")
        
        choice = Prompt.ask("File number to remove")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                self.selected_files.remove(files[idx])
        except:
            pass
    
    def open_file(self):
        """Open file for viewing"""
        files = [f.name for f in self.working_dir.iterdir() if f.is_file()]
        
        for i, f in enumerate(files, 1):
            self.console.print(f"  {i}. {f}")
        
        choice = Prompt.ask("File number")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                self.current_file = files[idx]
                self.selected_files.add(files[idx])
        except:
            pass
    
    def chat_with_files(self):
        """Chat with file context"""
        message = Prompt.ask("\n[green]You[/green]")
        if message:
            self.chat(message)
    
    def chat(self, message: str):
        """Process chat message"""
        # Build context from selected files
        context = ""
        for f in list(self.selected_files)[:2]:
            content = self.read_file(f)
            context += f"\nFile: {f}\n```\n{content[:800]}\n```\n"
        
        full_prompt = context + "\nUser: " + message if context else message
        
        with self.console.status("[bold blue]🤔 Thinking...[/bold blue]"):
            response = self.agent.chat(full_prompt)
        
        self.console.print(f"\n[bold cyan]Tide:[/bold cyan]\n{response.content}\n")
        input("Press Enter to continue...")
    
    def simple_chat(self):
        """Simple chat mode"""
        self.console.print("\n[bold]Chat Mode[/bold] (type 'exit' to quit)\n")
        
        while True:
            message = Prompt.ask("You")
            if message.lower() in ["exit", "quit"]:
                break
            
            with self.console.status("[bold blue]Thinking...[/bold blue]"):
                response = self.agent.chat(message)
            
            self.console.print(f"[bold cyan]Tide:[/bold cyan] {response.content}\n")
    
    def show_tools(self):
        """Show tools menu"""
        self.show_tools_list()
        input("\nPress Enter to continue...")
    
    def show_tools_list(self):
        """List all tools"""
        from internal.tools.registry import ToolRegistry
        
        tools = ToolRegistry()
        
        table = Table(title="Available Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Category", style="yellow")
        
        for name, tool in tools.tools.items():
            cat = tool.category
            table.add_row(name, tool.description[:40] + "...", cat)
        
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(tools.list_all())} tools[/dim]")
    
    def save_session(self):
        """Save current session"""
        if self.session:
            path = self.settings.sessions_dir / f"{self.session.name}.json"
            self.session.save(path)
            self.console.print(f"[green]✓ Saved: {self.session.name}[/green]")
