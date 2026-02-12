#!/usr/bin/env python3
"""
Tide Advanced TUI - Professional IDE Interface
Rich visual interface with live updates and advanced tool calling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import json

from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.syntax import Syntax
from rich.tree import Tree
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from rich.live import Live
from rich.status import Status
from rich.markdown import Markdown
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.columns import Columns
from rich.padding import Padding

from internal.agent.agent import Agent
from internal.agent.session import Session
from internal.tools.registry import ToolRegistry
from internal.config.settings import Settings


@dataclass
class ToolCall:
    """Represents a tool call"""
    name: str
    parameters: Dict
    result: Optional[str] = None
    status: str = "pending"  # pending, running, completed, error
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TideAdvancedTUI:
    """Advanced IDE-like TUI"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.console = Console()
        self.agent: Optional[Agent] = None
        self.session: Optional[Session] = None
        self.tool_registry = ToolRegistry()
        
        # State
        self.working_dir = Path.cwd()
        self.selected_files: Set[str] = set()
        self.current_file: Optional[str] = None
        self.chat_history: List[Dict] = []
        self.tool_calls: List[ToolCall] = []
        self.current_tool: Optional[ToolCall] = None
        
        # UI State
        self.active_panel = "files"  # files, editor, chat
        self.show_tool_output = False
        self.last_output = ""
        
    def create_layout(self) -> Layout:
        """Create professional IDE layout"""
        layout = Layout(name="root")
        
        # Split into: header, body, footer
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Body split: sidebar | main
        layout["body"].split_row(
            Layout(name="sidebar", size=35),
            Layout(name="main")
        )
        
        # Sidebar split: files | tools
        layout["sidebar"].split_column(
            Layout(name="files", ratio=2),
            Layout(name="tool_panel", ratio=1)
        )
        
        # Main split: editor | chat
        layout["main"].split_column(
            Layout(name="editor", ratio=3),
            Layout(name="chat", ratio=2)
        )
        
        return layout
    
    def update_header(self) -> Panel:
        """Update header panel"""
        title = Text()
        title.append("🌊 ", style="bold blue")
        title.append("Tide Agent", style="bold blue")
        title.append("  │  ", style="dim")
        title.append(f"{self.working_dir.name}", style="cyan")
        title.append("  │  ", style="dim")
        title.append(f"Model: {self.settings.model}", style="green")
        title.append("  │  ", style="dim")
        title.append(f"Files: {len(self.selected_files)}", style="yellow")
        
        if self.current_tool:
            title.append("  │  ", style="dim")
            title.append(f"🔧 {self.current_tool.name}", style="magenta")
        
        return Panel(title, box=box.DOUBLE, style="blue")
    
    def update_files_panel(self) -> Panel:
        """Update files panel with tree"""
        tree = Tree(f"📁 {self.working_dir.name}", guide_style="cyan")
        
        try:
            items = list(self.working_dir.iterdir())
            dirs = [d for d in items if d.is_dir() and not d.name.startswith('.')]
            files = [f for f in items if f.is_file() and not f.name.startswith('.')]
            
            # Add directories
            for d in sorted(dirs)[:8]:
                branch = tree.add(f"📁 {d.name}/")
                try:
                    subitems = list(d.iterdir())[:3]
                    for sub in sorted(subitems):
                        icon = self._get_icon(sub.name)
                        branch.add(f"{icon} {sub.name}")
                except:
                    pass
            
            # Add files
            for f in sorted(files)[:12]:
                icon = self._get_icon(f.name)
                if f.name in self.selected_files:
                    tree.add(f"[bold yellow]{icon} {f.name} ✓[/bold yellow]")
                elif f.name == self.current_file:
                    tree.add(f"[bold green]{icon} {f.name} ◄[/bold green]")
                else:
                    tree.add(f"{icon} {f.name}")
                    
        except Exception as e:
            tree.add(f"[red]Error: {e}[/red]")
        
        return Panel(tree, title="📂 Explorer", border_style="cyan", box=box.ROUNDED)
    
    def update_tool_panel(self) -> Panel:
        """Update tool status panel"""
        content = []
        
        # Show recent tool calls
        if self.tool_calls:
            content.append("[bold]Recent Tools:[/bold]\n")
            for tc in reversed(self.tool_calls[-5:]):
                status_icon = {
                    "pending": "⏳",
                    "running": "🔧",
                    "completed": "✅",
                    "error": "❌"
                }.get(tc.status, "❓")
                
                content.append(f"{status_icon} {tc.name}")
        else:
            content.append("[dim]No tools executed yet[/dim]")
        
        return Panel("\n".join(content), title="🔧 Tools", border_style="magenta", box=box.ROUNDED)
    
    def update_editor_panel(self) -> Panel:
        """Update editor/code panel"""
        if self.current_file:
            content = self._read_file(self.current_file)
            
            # Determine language for syntax highlighting
            lang = self._get_language(self.current_file)
            
            # Create syntax highlighted content
            try:
                syntax = Syntax(
                    content[:3000],  # Limit content
                    lang,
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True
                )
                title = f"📄 {self.current_file} ({len(content)} chars)"
                border = "green"
            except:
                syntax = content[:2000]
                title = f"📄 {self.current_file}"
                border = "yellow"
            
            return Panel(syntax, title=title, border_style=border, box=box.ROUNDED)
        else:
            # Show selected files summary
            if self.selected_files:
                content = []
                content.append("[bold]Selected Files:[/bold]\n")
                for f in sorted(self.selected_files):
                    size = self._get_file_size(f)
                    content.append(f"✓ {f} [{size}]")
                
                if self.last_output:
                    content.append(f"\n[bold]Last Output:[/bold]\n{self.last_output[:500]}")
                
                return Panel("\n".join(content), title="📋 Context", border_style="yellow", box=box.ROUNDED)
            else:
                help_text = """[dim]No file selected.

Commands:
  [bold]open <file>[/bold]  - Open file
  [bold]add <file>[/bold]   - Add to context
  [bold]chat <msg>[/bold]   - Chat with AI
  
Tip: Select files to include them in AI context.[/dim]"""
                return Panel(help_text, title="💡 Help", border_style="dim", box=box.ROUNDED)
    
    def update_chat_panel(self) -> Panel:
        """Update chat panel"""
        messages = []
        
        # Show last 8 messages
        for msg in self.chat_history[-8:]:
            if msg['role'] == 'user':
                messages.append(f"[bold green]▶ You:[/bold green] {msg['content'][:150]}")
            else:
                content = msg['content']
                # Truncate if too long
                if len(content) > 300:
                    content = content[:300] + "..."
                messages.append(f"[bold blue]● Tide:[/bold blue] {content}")
            messages.append("")
        
        if not messages:
            messages.append("[dim]Start chatting... Type your message below.[/dim]")
        
        chat_content = "\n".join(messages)
        
        return Panel(chat_content, title="💬 Chat", border_style="blue", box=box.ROUNDED)
    
    def update_footer(self) -> Panel:
        """Update footer with commands"""
        commands = [
            "[bold cyan]Commands:[/bold cyan]",
            "[bold]open[/bold] <file> - View file",
            "[bold]add[/bold] <file> - Add to context",
            "[bold]remove[/bold] <file> - Remove",
            "[bold]chat[/bold] <msg> - Chat",
            "[bold]tools[/bold] - List tools",
            "[bold]clear[/bold] - Clear context",
            "[bold]exit[/bold] - Quit"
        ]
        
        return Panel("  │  ".join(commands), box=box.SIMPLE, style="dim")
    
    def update_layout(self, layout: Layout):
        """Update all layout sections"""
        layout["header"].update(self.update_header())
        layout["files"].update(self.update_files_panel())
        layout["tool_panel"].update(self.update_tool_panel())
        layout["editor"].update(self.update_editor_panel())
        layout["chat"].update(self.update_chat_panel())
        layout["footer"].update(self.update_footer())
    
    def _get_icon(self, filename: str) -> str:
        """Get file icon"""
        ext = Path(filename).suffix.lower()
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.json': '📋',
            '.md': '📝', '.txt': '📄', '.yml': '⚙️', '.yaml': '⚙️',
            '.sh': '⚡', '.html': '🌐', '.css': '🎨', '.rs': '🦀',
            '.go': '🐹', '.java': '☕', '.cpp': '⚡', '.c': '⚡',
            '.h': '📋', '.rs': '🦀', '.rb': '💎', '.php': '🐘'
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
            '.java': 'java', '.cpp': 'cpp', '.c': 'c',
            '.h': 'c', '.rb': 'ruby', '.php': 'php'
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
    
    def _get_file_size(self, filepath: str) -> str:
        """Get human-readable file size"""
        try:
            path = self.working_dir / filepath
            size = path.stat().st_size
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f}KB"
            else:
                return f"{size/(1024*1024):.1f}MB"
        except:
            return "?"
    
    def run(self):
        """Main run loop"""
        self.console.clear()
        
        # Initialize agent
        self.agent = Agent(self.settings)
        self.session = Session()
        
        # Show welcome
        self.show_welcome()
        
        # Main loop with Live display
        with Live(self.create_layout(), refresh_per_second=4, screen=True) as live:
            layout = self.create_layout()
            
            while True:
                self.update_layout(layout)
                live.update(layout)
                
                # Get command (this blocks until input)
                try:
                    cmd = self.console.input("\n[bold cyan]Command:[/bold cyan] ").strip()
                    if cmd:
                        self.handle_command(cmd, layout, live)
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
    
    def show_welcome(self):
        """Show welcome message"""
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌊 Tide Advanced - Professional AI Coding Agent         ║
║                                                           ║
║   Features:                                               ║
║   • IDE-like interface with file explorer                 ║
║   • Syntax highlighting for code                          ║
║   • Real-time tool execution display                      ║
║   • Multi-file context support                            ║
║   • 16 professional tools                                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(welcome, style="bold blue")
        self.console.print("\n[dim]Press Enter to start...[/dim]")
        input()
    
    def handle_command(self, cmd: str, layout: Layout, live: Live):
        """Handle user commands"""
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if action in ['exit', 'quit', 'q']:
            raise KeyboardInterrupt
        
        elif action == 'open':
            self.cmd_open(arg)
        
        elif action == 'add':
            self.cmd_add(arg)
        
        elif action == 'remove':
            self.cmd_remove(arg)
        
        elif action == 'clear':
            self.selected_files.clear()
            self.current_file = None
            self.last_output = "Context cleared"
        
        elif action == 'chat':
            self.cmd_chat(arg, layout, live)
        
        elif action == 'tools':
            self.cmd_tools()
        
        elif action == 'analyze':
            self.cmd_analyze(arg, layout, live)
        
        elif action == 'help':
            self.cmd_help()
        
        else:
            # Treat as chat message
            self.cmd_chat(cmd, layout, live)
    
    def cmd_open(self, filename: str):
        """Open file"""
        if not filename:
            # Show file picker
            files = [f.name for f in self.working_dir.iterdir() if f.is_file()][:15]
            for i, f in enumerate(files, 1):
                self.console.print(f"  {i}. {f}")
            choice = self.console.input("File number: ")
            try:
                filename = files[int(choice) - 1]
            except:
                return
        
        if (self.working_dir / filename).exists():
            self.current_file = filename
            self.selected_files.add(filename)
            self.last_output = f"Opened {filename}"
    
    def cmd_add(self, filename: str):
        """Add file to context"""
        if filename and (self.working_dir / filename).exists():
            self.selected_files.add(filename)
            self.last_output = f"Added {filename} to context"
    
    def cmd_remove(self, filename: str):
        """Remove file from context"""
        if filename in self.selected_files:
            self.selected_files.remove(filename)
            if self.current_file == filename:
                self.current_file = None
            self.last_output = f"Removed {filename}"
    
    def cmd_chat(self, message: str, layout: Layout, live: Live):
        """Chat with AI"""
        if not message:
            message = self.console.input("Message: ")
        
        if not message:
            return
        
        # Add to history
        self.chat_history.append({'role': 'user', 'content': message})
        
        # Build context from selected files
        context = ""
        for f in list(self.selected_files)[:3]:
            content = self._read_file(f)
            context += f"\n--- {f} ---\n{content[:800]}\n"
        
        full_prompt = f"{context}\n\nUser: {message}" if context else message
        
        # Show thinking status
        self.current_tool = ToolCall("thinking", {})
        self.current_tool.status = "running"
        self.update_layout(layout)
        live.update(layout)
        
        try:
            # Get response
            response = self.agent.chat(full_prompt)
            
            # Record any tool calls
            for tool_name in response.tools_used:
                tc = ToolCall(tool_name, {}, status="completed")
                self.tool_calls.append(tc)
            
            # Add response to history
            self.chat_history.append({
                'role': 'assistant',
                'content': response.content
            })
            
            self.last_output = response.content[:200]
            
        except Exception as e:
            self.chat_history.append({
                'role': 'assistant',
                'content': f"Error: {e}"
            })
            self.last_output = f"Error: {e}"
        
        self.current_tool = None
    
    def cmd_tools(self):
        """List all tools"""
        table = Table(title="Available Tools", box=box.ROUNDED)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Category", style="yellow")
        
        for name, tool in self.tool_registry.tools.items():
            table.add_row(name, tool.description[:45], tool.category)
        
        self.console.print(table)
        self.console.input("\nPress Enter to continue...")
    
    def cmd_analyze(self, filename: str, layout: Layout, live: Live):
        """Analyze code file"""
        if not filename:
            if self.current_file:
                filename = self.current_file
            else:
                self.last_output = "No file selected"
                return
        
        self.last_output = f"Analyzing {filename}..."
        self.update_layout(layout)
        live.update(layout)
        
        # Use the analyze_code tool
        tool = self.tool_registry.get("analyze_code")
        if tool:
            result = tool.execute({"path": filename})
            self.last_output = result.output if result.success else result.error
            
            tc = ToolCall("analyze_code", {"path": filename}, 
                         result=self.last_output[:100], status="completed")
            self.tool_calls.append(tc)
    
    def cmd_help(self):
        """Show help"""
        help_text = """
[bold cyan]Tide Advanced Commands[/bold cyan]

[bold]File Operations:[/bold]
  open <file>     - Open and view file
  add <file>      - Add file to AI context
  remove <file>   - Remove file from context
  clear           - Clear all context

[bold]AI Commands:[/bold]
  chat <message>  - Chat with AI about selected files
  analyze [file]  - Analyze code structure
  <message>       - Quick chat (no command needed)

[bold]System:[/bold]
  tools           - List all available tools
  help            - Show this help
  exit            - Quit

[bold]Tips:[/bold]
• Select files to include them in AI context
• Use 'analyze' for detailed code structure
• The AI can see all selected files when chatting
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        self.console.input("\nPress Enter to continue...")


def main():
    """Entry point"""
    settings = Settings()
    app = TideAdvancedTUI(settings)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")


if __name__ == "__main__":
    main()
