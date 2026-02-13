"""
Modern TUI Application using Textual
Provides a rich chat interface with model selection
"""
import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Input, Static, Button, 
    Select, Markdown, LoadingIndicator, TabbedContent, TabPane, Label
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.worker import Worker, WorkerState
from textual.screen import Screen
from textual.widgets import DataTable

from ..agent import Agent
from ..config import Config


class Message(Static):
    """A compact chat message widget"""
    
    def __init__(self, content: str, is_user: bool = False, model_name: str = "", **kwargs):
        self.message_content = content
        self.is_user = is_user
        self.model_name = model_name
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        if self.is_user:
            role = "👤 You"
            style = "user-message"
        else:
            model_indicator = f" ({self.model_name})" if self.model_name else ""
            role = f"🌊 Tide{model_indicator}"
            style = "bot-message"
        
        # Compact layout - role and content on same line for user, stacked for bot
        if self.is_user:
            with Horizontal(classes=f"message-container {style}"):
                yield Static(f"[bold]{role}:[/] ", classes="message-role")
                yield Markdown(self._compact_content(), classes="message-content")
        else:
            with Vertical(classes=f"message-container {style}"):
                yield Static(f"[bold]{role}[/]", classes="message-role")
                yield Markdown(self._compact_content(), classes="message-content")
    
    def _compact_content(self) -> str:
        """Compact markdown content"""
        # Keep it simple - just return the content
        return self.message_content


class ModelDialog(Screen):
    """Model selection dialog with better display"""
    
    def __init__(self, config: Config, **kwargs):
        self.config = config
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label("[bold cyan]🤖 Select Model[/]", classes="dialog-title")
            
            current_model = self.config.model
            models = self.config.models
            
            # Build better options
            options = []
            for alias, info in models.items():
                is_current = info['name'] == current_model
                speed = info.get('speed', 'medium')
                provider = info.get('provider', 'ollama')
                speed_icon = "⚡" if speed == "fast" else "🚀"
                provider_icon = "☁️" if provider == 'minimax' else "🏠"
                current_marker = "▶ " if is_current else "  "
                
                label = f"{current_marker}{alias.upper():10} {provider_icon} {speed_icon}"
                options.append((label, alias))
            
            yield Label("[dim]Click dropdown to see available models:[/]", classes="dialog-hint")
            
            yield Select(options, id="model-select-dialog", prompt="▼ Select a model")
            
            # Show current selection
            current_alias = None
            for alias, info in models.items():
                if info['name'] == current_model:
                    current_alias = alias
                    break
            
            yield Label(f"[dim]Currently using: {current_alias or 'unknown'}[/]", classes="dialog-current")
            
            with Horizontal(classes="dialog-buttons"):
                yield Button("Select", variant="primary", id="select-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select-btn":
            select = self.query_one("#model-select-dialog", Select)
            if select.value:
                self.dismiss(select.value)
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)


class Sidebar(Static):
    """Sidebar with info"""
    
    def __init__(self, config: Config, **kwargs):
        self.config = config
        super().__init__(**kwargs)
    
    def get_current_model_display(self) -> str:
        """Get current model display info"""
        current_name = self.config.model
        
        for alias, info in self.config.models.items():
            if info['name'] == current_name:
                speed = info.get('speed', 'medium')
                size = info.get('size', '?')
                provider = info.get('provider', 'ollama')
                speed_icon = "⚡" if speed == 'fast' else "🚀"
                provider_icon = "☁️" if provider == 'minimax' else "🏠"
                return f"[bold white on_blue]{alias.upper()}[/]\n[dim]{provider_icon} {provider} | {speed_icon} {speed}[/]"
        
        # Fallback to shortened name
        short_name = current_name.split('/')[-1][:20]
        return f"[bold white on_blue]{short_name}...[/]"
    
    def update_model_display(self) -> None:
        """Update the model display after config changes"""
        try:
            model_display = self.query_one("#model-display", Static)
            model_display.update("[bold]Active Model:[/]\n" + self.get_current_model_display())
        except Exception:
            pass
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="sidebar-content"):
            # Logo/Branding
            yield Static(
                "[bold blue]🌊 Tide OS[/]\n[dim]v3.0.0 - AI Coding Agent[/]",
                classes="sidebar-brand"
            )
            
            # Current Model - Cleaner display
            yield Static(
                "[bold]Active Model:[/]\n" + self.get_current_model_display(),
                classes="sidebar-model",
                id="model-display"
            )
            
            yield Button("🤖 Switch Model", id="change-model-btn", variant="primary")
            
            yield Static("[bold]Keyboard Shortcuts:[/]\n[dim]Ctrl+M - Switch Model[/]\n[dim]Ctrl+L - Clear Chat[/]\n[dim]Ctrl+C - Quit[/]", classes="sidebar-help")
            
            # Tools summary
            yield Static("[bold]23 Tools Available[/]", classes="sidebar-tools-header")
            yield Static(
                "[dim]"
                "📁 Files (7)\n"
                "💻 Code (5)\n"
                "📦 Git (6)\n"
                "🔧 System (3)\n"
                "🌐 Web (2)"
                "[/]", 
                classes="sidebar-tools"
            )


class ChatInterface(Container):
    """Main chat interface"""
    
    def __init__(self, agent: Agent, **kwargs):
        self.agent = agent
        self.messages = []
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="chat-container"):
            # Messages area
            with Container(id="messages", classes="messages-area"):
                yield Static(
                    "[dim]Type a message to start[/]",
                    id="welcome-message"
                )
            
            # Input area
            with Container(classes="input-area"):
                yield Input(
                    placeholder="Message...", 
                    id="message-input"
                )


class TideApp(App):
    """Main TUI Application"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    .main-container {
        width: 100%;
        height: 100%;
    }
    
    .sidebar {
        width: 20%;
        height: 100%;
        background: $surface-darken-2;
        padding: 0 1;
        border-right: solid $primary;
    }
    
    .sidebar-content {
        height: 100%;
    }
    
    .sidebar-brand {
        text-align: center;
        padding: 1;
        border-bottom: solid $primary 50%;
        margin-bottom: 1;
    }
    
    .sidebar-model {
        padding: 1;
        background: $surface-darken-1;
        margin: 1 0;
        border: solid $success;
        text-align: center;
    }
    
    .sidebar-help {
        padding: 1;
        margin: 1 0;
    }
    
    .sidebar-tools-header {
        padding: 1;
        margin-top: 2;
        border-top: solid $primary 50%;
    }
    
    .sidebar-tools {
        padding: 0 1;
    }
    
    #change-model-btn {
        margin: 1 0;
    }
    
    .chat-area {
        width: 80%;
        height: 100%;
    }
    
    .chat-container {
        height: 100%;
    }
    
    .messages-area {
        height: 100%;
        overflow-y: auto;
        padding: 0;
    }
    
    .input-area {
        height: auto;
        padding: 0;
        border-top: solid $primary;
    }
    
    .message-container {
        padding: 0;
        margin: 1 0;
    }

    .user-message {
        background: $surface-darken-1;
    }

    .bot-message {
        border: none;
    }
    
    .message-role {
        text-style: bold;
        margin-bottom: 0;
    }
    
    .message-content {
        margin: 0;
        padding: 0;
    }
    
    .loading-message {
        color: $primary;
        padding: 0;
        margin: 0;
    }
    
    .message-role {
        text-style: bold;
        margin-bottom: 0;
    }
    
    #message-input {
        width: 100%;
    }
    
    /* Dialog styles */
    .dialog {
        background: $surface;
        padding: 2;
        border: solid $primary;
        width: 60%;
        height: auto;
    }
    
    .dialog-title {
        text-align: center;
        margin-bottom: 1;
    }
    
    .dialog-buttons {
        margin-top: 2;
        align: center middle;
    }
    
    .dialog-buttons Button {
        margin: 0 1;
    }
    
    .dialog-current {
        text-align: center;
        margin: 1 0;
        color: $success;
    }
    
    .dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #model-select-dialog {
        width: 100%;
        margin: 1 0;
        border: solid $primary;
        padding: 1;
    }
    
    #model-select-dialog:focus {
        border: solid $success;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear", "Clear Chat", show=True),
        Binding("ctrl+m", "change_model", "Change Model", show=True),
    ]
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.agent = Agent(self.config)
        self.current_worker: Optional[Worker] = None
        
        # Check if MiniMax is selected but no API key
        if 'MiniMax' in self.config.model:
            import os
            if not os.getenv('MINIMAX_API_KEY'):
                print("⚠️  Warning: MiniMax model selected but MINIMAX_API_KEY not set!")
                print("   Set with: export MINIMAX_API_KEY='your-key'")
        
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(classes="main-container"):
            # Sidebar
            yield Sidebar(self.config, classes="sidebar")
            
            # Chat area
            with Container(classes="chat-area"):
                yield ChatInterface(self.agent)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        self.title = "🌊 Tide OS v3.0.0"
        self.sub_title = "AI Coding Agent"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "change-model-btn":
            self.action_change_model()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission"""
        if event.input.id == "message-input":
            message = event.value.strip()
            if message:
                self.send_message(message)
                event.input.value = ""
    
    def send_message(self, message: str) -> None:
        """Send a message and get response"""
        # Remove welcome message on first message (if it exists)
        try:
            welcome = self.query_one("#welcome-message", Markdown)
            welcome.remove()
        except Exception:
            pass  # Welcome message already removed or not present
        
        # Add user message
        messages = self.query_one("#messages", Container)
        messages.mount(Message(message, is_user=True))
        messages.scroll_end()
        
        # Show loading with thinking indicator
        model_name = self._get_model_short_name()
        loading_text = f"🌊 Tide ({model_name})..."
        messages.mount(Static(loading_text, classes="loading-message"))
        messages.scroll_end()
        
        # Run agent in background worker
        self.current_worker = self.run_worker(
            self.get_response(message),
            thread=True
        )
    
    def _get_model_short_name(self) -> str:
        """Get short model name for display"""
        model = self.config.model
        if 'MiniMax' in model:
            return "MiniMax"
        elif 'nanbeige' in model.lower():
            return "Nanbeige"
        elif 'llama' in model.lower():
            return "Llama"
        elif 'qwen' in model.lower():
            return "Qwen"
        return model.split(':')[0][:10]
    
    async def get_response(self, message: str) -> str:
        """Get response from agent with timeout"""
        try:
            # Run chat in executor with timeout
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self.agent.chat, message),
                timeout=60.0  # 60 second timeout
            )
            
            # Handle confirmation needed
            if result.get("needs_confirmation"):
                tool_name = result.get("tool_name")
                params = result.get("tool_params", {})
                
                # Show what tool will be called
                tool_msg = f"🔧 Executing: {tool_name}\n"
                tool_msg += f"```json\n{params}\n```"
                
                # Auto-execute the tool (in TUI we don't have interactive confirmation yet)
                tool_result = await asyncio.wait_for(
                    loop.run_in_executor(None, self.agent.execute_confirmed_tool, {
                        "tool": tool_name,
                        "params": params
                    }),
                    timeout=30.0
                )
                
                if tool_result.success:
                    return f"✅ {tool_name} executed successfully!\n\n{tool_result.output[:500]}"
                else:
                    return f"❌ {tool_name} failed:\n{tool_result.error}"
            
            return result.get("response", "No response")
            
        except asyncio.TimeoutError:
            return "⏱️ Response timed out (60s). Try:\n• Switch to a faster model\n• Simpler requests\n• Check 'ollama ps'"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion"""
        if event.state == WorkerState.SUCCESS:
            try:
                # Get messages container
                messages = self.query_one("#messages", Container)
                
                # Remove loading messages
                try:
                    for msg in messages.query(".loading-message"):
                        msg.remove()
                except:
                    pass
                
                # Get model name for display
                model_name = self._get_model_short_name()
                
                # Add bot response with model name
                response = event.worker.result
                messages.mount(Message(response, is_user=False, model_name=model_name))
                messages.scroll_end()
            except Exception as e:
                # Handle any errors gracefully
                self.notify(f"Error: {e}", severity="warning")
    
    def action_change_model(self) -> None:
        """Show model selection dialog"""
        async def check_model(alias):
            if alias:
                try:
                    if self.config.set_model(alias):
                        model_info = self.config.get_model_info(alias)
                        if model_info:
                            # Update agent with new model
                            self.agent = Agent(self.config)
                            
                            # Update sidebar display
                            sidebar = self.query_one(Sidebar)
                            if sidebar:
                                sidebar.update_model_display()
                            
                            # Show notification
                            model_name = model_info.get('name', alias)
                            self.notify(f"🤖 Switched to {alias.upper()} ({model_name})", severity="information", timeout=3)
                    else:
                        self.notify(f"❌ Failed to switch to {alias}", severity="error")
                except Exception as e:
                    self.notify(f"❌ Error: {str(e)[:100]}", severity="error")
        
        self.push_screen(ModelDialog(self.config), check_model)
    
    def action_clear(self) -> None:
        """Clear chat history"""
        messages = self.query_one("#messages", Container)
        messages.remove_children()
        messages.mount(Markdown("[dim]Chat cleared. Start a new conversation![/]"))        
        self.agent.reset()


def run_tui(config: Optional[Config] = None):
    """Run the TUI application"""
    app = TideApp(config)
    app.run()
