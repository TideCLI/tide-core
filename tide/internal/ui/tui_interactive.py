#!/usr/bin/env python3
"""
Tide Interactive TUI - Fixed input handling with better UX
Professional IDE interface with proper input handling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.syntax import Syntax
from rich.tree import Tree
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.status import Status
from rich.columns import Columns
from rich.padding import Padding

from internal.agent.agent import Agent
from internal.agent.session import Session
from internal.tools.registry import ToolRegistry
from internal.config.settings import Settings


def clean_input(prompt=""):
    """Read input and clean escape sequences"""
    try:
        if prompt:
            print(prompt, end="", flush=True)
        import tty
        import termios
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Set terminal to raw mode temporarily
            tty.setcbreak(sys.stdin)
            result = ""
            while True:
                ch = sys.stdin.read(1)
                if ch == '\n' or ch == '\r':
                    print()
                    break
                elif ch == '\x7f':  # Backspace
                    if result:
                        result = result[:-1]
                        print('\b \b', end="", flush=True)
                elif ord(ch) >= 32:  # Printable character
                    result += ch
                    print(ch, end="", flush=True)
                # Ignore escape sequences (start with ESC)
                elif ch == '\x1b':
                    # Read and discard the rest of escape sequence
                    import select
                    while select.select([sys.stdin], [], [], 0.1)[0]:
                        sys.stdin.read(1)
            return result.strip()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except:
        # Fallback to regular input
        return input(prompt).strip()


class TideInteractiveTUI:
    """Interactive TUI with proper input handling"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.console = Console()
        self.agent: Optional[Agent] = None
        self.session: Optional[Session] = None
        self.tool_registry = ToolRegistry()
        
        self.working_dir = Path.cwd()
        self.selected_files: Set[str] = set()
        self.current_file: Optional[str] = None
        self.chat_history: List[Dict] = []
        
    def clear_screen(self):
        """Clear screen"""
        self.console.clear()
    
    def show_header(self):
        """Show application header"""
        header = Text()
        header.append("🌊 ", style="bold blue")
        header.append("Tide Agent", style="bold blue")
        header.append("  │  ", style="dim")
        header.append(f"{self.working_dir.name}", style="cyan")
        header.append("  │  ", style="dim")
        header.append(f"Model: {self.settings.model}", style="green")
        if self.selected_files:
            header.append(f"  │  Files: {len(self.selected_files)}", style="yellow")
        
        self.console.print(Panel(header, box=box.DOUBLE, style="blue"))
    
    def show_files_panel(self):
        """Show files panel"""
        tree = Tree(f"📁 {self.working_dir.name}", guide_style="cyan")
        
        try:
            items = list(self.working_dir.iterdir())
            dirs = [d for d in items if d.is_dir() and not d.name.startswith('.')]
            files = [f for f in items if f.is_file() and not f.name.startswith('.')]
            
            # Add directories
            for d in sorted(dirs)[:5]:
                branch = tree.add(f"📁 {d.name}/")
                try:
                    for sub in sorted(d.iterdir())[:2]:
                        icon = self._get_icon(sub.name)
                        branch.add(f"{icon} {sub.name}")
                except:
                    pass
            
            # Add files
            for f in sorted(files)[:10]:
                icon = self._get_icon(f.name)
                if f.name in self.selected_files:
                    tree.add(f"[bold yellow]{icon} {f.name} ✓[/bold yellow]")
                elif f.name == self.current_file:
                    tree.add(f"[bold green]{icon} {f.name} ◄[/bold green]")
                else:
                    tree.add(f"{icon} {f.name}")
        except:
            pass
        
        self.console.print(Panel(tree, title="📂 Explorer", border_style="cyan"))
    
    def show_editor_panel(self):
        """Show editor/code panel"""
        if self.current_file:
            content = self._read_file(self.current_file)
            lang = self._get_language(self.current_file)
            
            try:
                syntax = Syntax(
                    content[:2500],
                    lang,
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True
                )
                self.console.print(Panel(
                    syntax, 
                    title=f"📄 {self.current_file}", 
                    border_style="green"
                ))
            except:
                self.console.print(Panel(
                    content[:2000],
                    title=f"📄 {self.current_file}",
                    border_style="yellow"
                ))
        else:
            # Show help or selected files
            if self.selected_files:
                content = ["[bold]Selected Files:[/bold]"]
                for f in sorted(self.selected_files):
                    content.append(f"  ✓ {f}")
                self.console.print(Panel(
                    "\n".join(content),
                    title="📋 Context",
                    border_style="yellow"
                ))
            else:
                help_text = """[dim]
No file selected.

Quick Commands:
  open <file>  - View file
  add <file>   - Add to context  
  chat <msg>   - Chat with AI
  tools        - List tools
  help         - Show all commands
[/dim]"""
                self.console.print(Panel(help_text, title="💡 Help", border_style="dim"))
    
    def show_chat_panel(self):
        """Show chat history with message boxes like modern chat apps"""
        if not self.chat_history:
            # Better empty state
            welcome_text = """[dim]
Welcome to Tide Chat! 👋

Type a message to start chatting with AI.

Quick start:
• [bold]chat "hello"[/bold] - Say hi
• [bold]add <file>[/bold] - Add file to context  
• [bold]analyze <file>[/bold] - Analyze code
• [bold]history[/bold] - View full chat history

The AI can see all files you select.[/dim]"""
            self.console.print(Panel(
                welcome_text,
                title="[bold blue]💬 Chat[/bold blue]",
                border_style="blue",
                box=box.ROUNDED
            ))
            return
        
        # Build chat messages with proper panels
        chat_content = []
        
        for msg in self.chat_history[-5:]:
            if msg['role'] == 'user':
                # User message - green box
                content = msg['content'][:100]
                user_box = Panel(
                    f"[white]{content}[/white]",
                    title="[bold green]▶ You[/bold green]",
                    border_style="green",
                    box=box.ROUNDED,
                    title_align="left"
                )
                chat_content.append(user_box)
            elif msg['role'] == 'assistant':
                # AI message - blue box
                content = msg['content'][:300]
                ai_box = Panel(
                    f"[white]{content}[/white]",
                    title="[bold blue]● Tide[/bold blue]",
                    border_style="blue",
                    box=box.ROUNDED,
                    title_align="left"
                )
                chat_content.append(ai_box)
        
        # Stack messages vertically with spacing
        from rich.padding import Padding
        spaced_content = []
        for i, item in enumerate(chat_content):
            spaced_content.append(item)
            if i < len(chat_content) - 1:
                spaced_content.append("")  # Add spacing between messages
        
        self.console.print(Panel(
            Group(*spaced_content),
            title="💬 Chat",
            border_style="blue",
            box=box.ROUNDED
        ))
    
    def show_footer(self):
        """Show footer with commands"""
        commands = [
            "[bold cyan]Commands:[/bold cyan]",
            "[bold]open[/bold] <file> - View",
            "[bold]add[/bold] <file> - Context",
            "[bold]chat[/bold] <msg> - Chat",
            "[bold]history[/bold] - History",
            "[bold]tools[/bold] - Tools",
            "[bold]exit[/bold] - Quit"
        ]
        self.console.print(Panel("  │  ".join(commands), box=box.SIMPLE))
    
    def refresh_display(self):
        """Refresh the full display"""
        self.clear_screen()
        self.show_header()
        
        # Show panels in layout
        self.console.print()
        self.show_files_panel()
        self.console.print()
        self.show_editor_panel()
        self.console.print()
        self.show_chat_panel()
        self.console.print()
        self.show_footer()
    
    def get_input(self) -> str:
        """Get user input with prompt"""
        self.console.print()
        try:
            self.console.print("[bold cyan]>[/bold cyan]", end="")
            return clean_input()
        except (EOFError, KeyboardInterrupt):
            return "exit"
    
    def run(self):
        """Main run loop"""
        # Initialize
        self.agent = Agent(self.settings)
        self.session = Session()
        
        # Show welcome
        self.show_welcome()
        
        # Main loop
        while True:
            try:
                # Refresh display
                self.refresh_display()
                
                # Get input
                cmd = self.get_input()
                
                if not cmd:
                    continue
                
                # Process command
                if cmd.lower() in ['exit', 'quit', 'q']:
                    self.console.print("\n[dim]👋 Goodbye![/dim]\n")
                    break
                
                self.process_command(cmd)
                
            except KeyboardInterrupt:
                self.console.print("\n\n[dim]👋 Goodbye![/dim]\n")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                self.console.print("\n[dim]Press Enter to continue...[/dim]")
                clean_input()
    
    def show_welcome(self):
        """Show welcome screen"""
        self.clear_screen()
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌊 Tide Interactive - Professional AI Coding Agent      ║
║                                                           ║
║   Features:                                               ║
║   • IDE-like interface with file explorer                 ║
║   • Syntax highlighting for 15+ languages                 ║
║   • 16 professional tools with AST analysis               ║
║   • Multi-file context support                            ║
║   • Git integration                                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(welcome, style="bold blue")
        self.console.print("\n[dim]Press Enter to start...[/dim]")
        clean_input()
    
    def process_command(self, cmd: str):
        """Process user command"""
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if action == 'open':
            self.cmd_open(arg)
        elif action == 'add':
            self.cmd_add(arg)
        elif action == 'remove':
            self.cmd_remove(arg)
        elif action == 'clear':
            self.selected_files.clear()
            self.current_file = None
            self.add_system_message("Context cleared")
        elif action == 'chat':
            self.cmd_chat(arg)
        elif action == 'tools':
            self.cmd_tools()
        elif action == 'analyze':
            self.cmd_analyze(arg)
        elif action == 'history':
            self.cmd_history()
        elif action == 'help':
            self.cmd_help()
        else:
            # Treat as direct chat
            self.cmd_chat(cmd)
    
    def cmd_open(self, filename: str):
        """Open file"""
        if not filename:
            # Show file picker
            files = [f.name for f in self.working_dir.iterdir() if f.is_file()][:15]
            self.console.print("\n[cyan]Available files:[/cyan]")
            for i, f in enumerate(files, 1):
                self.console.print(f"  {i}. {f}")
            try:
                choice = Prompt.ask("File number")
                filename = files[int(choice) - 1]
            except:
                return
        
        if (self.working_dir / filename).exists():
            self.current_file = filename
            self.selected_files.add(filename)
            self.add_system_message(f"Opened {filename}")
    
    def cmd_add(self, filename: str):
        """Add file to context"""
        if filename and (self.working_dir / filename).exists():
            self.selected_files.add(filename)
            self.add_system_message(f"Added {filename}")
        elif not filename:
            # Show picker
            self.cmd_open("")
    
    def cmd_remove(self, filename: str):
        """Remove file from context"""
        if filename in self.selected_files:
            self.selected_files.remove(filename)
            if self.current_file == filename:
                self.current_file = None
            self.add_system_message(f"Removed {filename}")
    
    def cmd_chat(self, message: str):
        """Chat with AI"""
        if not message:
            message = Prompt.ask("Your message")
        
        if not message:
            return
        
        # Add to history
        self.chat_history.append({'role': 'user', 'content': message})
        
        # Build context from selected files
        context = ""
        for f in list(self.selected_files)[:2]:
            content = self._read_file(f)
            context += f"\n--- {f} ---\n{content[:600]}\n"
        
        full_prompt = f"{context}\n\nUser: {message}" if context else message
        
        # Show thinking indicator
        self.refresh_display()
        thinking_box = Panel(
            "[bold blue]🤔 Thinking...[/bold blue]  [dim]Analyzing your request[/dim]",
            border_style="blue",
            box=box.ROUNDED,
            width=50
        )
        self.console.print("\n")
        self.console.print(thinking_box)
        
        try:
            response = self.agent.chat(full_prompt)
            
            self.chat_history.append({
                'role': 'assistant',
                'content': response.content
            })
            
        except Exception as e:
            self.chat_history.append({
                'role': 'assistant',
                'content': f"Error: {e}"
            })
        
        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        clean_input()
    
    def cmd_tools(self):
        """List all tools"""
        self.clear_screen()
        table = Table(title="🔧 Available Tools", box=box.ROUNDED)
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Category", style="yellow")
        
        for name, tool in self.tool_registry.tools.items():
            table.add_row(name, tool.description[:40] + "...", tool.category)
        
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(self.tool_registry.list_all())} tools[/dim]")
        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        clean_input()
    
    def cmd_analyze(self, filename: str):
        """Analyze code file"""
        if not filename and self.current_file:
            filename = self.current_file
        
        if not filename:
            self.add_system_message("No file to analyze")
            return
        
        self.console.print(f"\n[bold]Analyzing {filename}...[/bold]")
        
        tool = self.tool_registry.get("analyze_code")
        if tool:
            result = tool.execute({"path": filename})
            self.chat_history.append({
                'role': 'assistant',
                'content': result.output if result.success else result.error
            })
            self.console.print("\n[dim]Press Enter to continue...[/dim]")
            clean_input()
    
    def cmd_help(self):
        """Show help"""
        self.clear_screen()
        help_text = """
[bold cyan]Tide Interactive Commands[/bold cyan]

[bold]File Operations:[/bold]
  open <file>     - Open and view file with syntax highlighting
  add <file>      - Add file to AI context
  remove <file>   - Remove file from context
  clear           - Clear all selected files

[bold]AI Commands:[/bold]
  chat <message>  - Chat with AI about selected files
  analyze [file]  - Analyze code structure using AST
  <message>       - Quick chat (no command needed)

[bold]System:[/bold]
  tools           - List all 16 available tools
  history         - Show full chat history
  help            - Show this help
  exit            - Quit

[bold]Tips:[/bold]
• Select files to include them in AI context
• Use 'open' to view files with syntax highlighting
• Use 'analyze' for detailed code structure
• The AI can see all selected files when chatting
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        clean_input()
    
    def cmd_history(self):
        """Show full chat history"""
        self.clear_screen()
        
        if not self.chat_history:
            self.console.print("[dim]No chat history yet.[/dim]")
            self.console.print("\n[dim]Press Enter to continue...[/dim]")
            clean_input()
            return
        
        self.console.print(f"[bold cyan]Chat History ({len(self.chat_history)} messages)[/bold cyan]\n")
        
        for i, msg in enumerate(self.chat_history, 1):
            if msg['role'] == 'user':
                user_box = Panel(
                    f"[white]{msg['content']}[/white]",
                    title=f"[bold green]▶ You ({i})[/bold green]",
                    border_style="green",
                    box=box.ROUNDED,
                    title_align="left"
                )
                self.console.print(user_box)
            elif msg['role'] == 'assistant':
                content = msg['content'][:500]  # Longer for history view
                if len(msg['content']) > 500:
                    content += "..."
                ai_box = Panel(
                    f"[white]{content}[/white]",
                    title=f"[bold blue]● Tide ({i})[/bold blue]",
                    border_style="blue",
                    box=box.ROUNDED,
                    title_align="left"
                )
                self.console.print(ai_box)
            self.console.print()
        
        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        clean_input()
    
    def add_system_message(self, msg: str):
        """Add system message to chat"""
        self.chat_history.append({'role': 'system', 'content': msg})
    
    def _get_icon(self, filename: str) -> str:
        """Get file icon"""
        ext = Path(filename).suffix.lower()
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.json': '📋',
            '.md': '📝', '.txt': '📄', '.yml': '⚙️', '.yaml': '⚙️',
            '.sh': '⚡', '.html': '🌐', '.css': '🎨', '.rs': '🦀',
            '.go': '🐹', '.java': '☕', '.cpp': '⚡', '.c': '⚡'
        }
        return icons.get(ext, '📄')
    
    def _get_language(self, filename: str) -> str:
        """Get language for syntax highlighting"""
        ext = Path(filename).suffix.lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.json': 'json', '.md': 'markdown', '.yml': 'yaml',
            '.yaml': 'yaml', '.sh': 'bash', '.html': 'html',
            '.css': 'css', '.rs': 'rust', '.go': 'go',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c'
        }
        return lang_map.get(ext, 'text')
    
    def _read_file(self, filepath: str) -> str:
        """Read file content"""
        try:
            path = self.working_dir / filepath
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return f"Error reading {filepath}"


def main():
    """Entry point"""
    settings = Settings()
    app = TideInteractiveTUI(settings)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")


if __name__ == "__main__":
    main()
