"""
AI Agent - Orchestrates tools and LLM interaction
"""
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from .models.ollama import OllamaClient, ChatMessage, ChatResponse
from .models.minimax import MiniMaxClient, create_minimax_client
from .tools.registry import ToolRegistry, ToolResult, get_registry
from .tools.base import ToolContext
from .config import Config

# Import tools to trigger registration
from .tools import filesystem, system, code, web, git, advanced_edit, lint


@dataclass
class Session:
    """A conversation session"""
    messages: List[ChatMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None):
        self.messages.append(ChatMessage(role=role, content=content, tool_calls=tool_calls))
    
    def to_dict(self) -> List[Dict]:
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
        ]


class Agent:
    """
    AI Agent that manages tool execution and LLM conversations.
    """
    
    # Action keywords that trigger tool usage (file/execution operations)
    ACTION_KEYWORDS = [
        'create', 'make', 'write', 'edit', 'modify', 'delete', 'remove', 'mv', 'cp',
        'mkdir', 'touch', 'cat', 'ls', 'list', 'view', 'read', 'grep', 'find', 'glob',
        'run', 'execute', 'bash', 'python', 'eval'
    ]
    
    SYSTEM_PROMPT = """You are Tide OS - a powerful AI coding assistant like Claude Code, OpenCode, and Codex.

CORE CAPABILITIES:
- Read, write, and edit files
- Run shell commands
- Search and analyze code
- Git operations
- Web search

IMPORTANT: When user asks to analyze codebase, use these tools in order:
1. find_files - Find all code files in the project
2. analyze_code - Analyze individual files for structure
3. search - Search for patterns across files

TOOL CALLING RULES:
- When user asks to CREATE/MAKE/WRITE files -> output JSON: tool call
- When user asks to ANALYZE/EXPLORE codebase -> use find_files + analyze_code
- When user asks to RUN commands -> output JSON: tool call
- When user asks about code -> answer directly

QUICK REFERENCE:
- find_files - Find all code files
- analyze_code - Analyze file structure
- search - Search in files
- read_file - Read file content
- write_file - Write file
- bash - Run shell command

Just output JSON for tool calls. Answer questions directly."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.registry = get_registry()
        self.session = Session()
        
        # Set up tool context
        tool_context = ToolContext(
            working_dir=str(Path.cwd()),
            config=self.config.to_dict()
        )
        self.registry.set_context(tool_context)
        
        # Initialize clients based on model type
        self._init_clients()
        
        # Initialize system message
        self._update_system_prompt()
    
    def _init_clients(self) -> None:
        """Initialize model clients based on configuration"""
        self.ollama_client = OllamaClient(
            host=self.config.ollama_host,
            timeout=self.config.ollama_timeout
        )
        
        # Try to create MiniMax client (only if API key is set)
        self.minimax_client = create_minimax_client(timeout=60)
        
        # Determine which client to use
        self._current_client = None
        self._current_client_type = None
    
    def _get_client(self, model: Optional[str] = None) -> tuple:
        """Get appropriate client for the model
        
        Returns: (client, client_type) where client_type is 'ollama' or 'minimax'
        """
        model_name = model or self.config.model
        
        # Check if it's a MiniMax model (case-insensitive check)
        model_lower = model_name.lower()
        if self.minimax_client and 'minimax' in model_lower:
            if self.minimax_client.is_available():
                return self.minimax_client, 'minimax'
            else:
                raise ValueError(
                    "MiniMax API key not set. "
                    "Set MINIMAX_API_KEY environment variable."
                )
        
        # Default to Ollama
        return self.ollama_client, 'ollama'
    
    def _supports_tools(self, client_type: str) -> bool:
        """Check if the client supports tool calling"""
        return client_type == 'ollama'  # MiniMax M2.5 doesn't support tool calling
    
    def _handle_error(self, error: Exception, context: str = "") -> str:
        """Convert exceptions to user-friendly error messages"""
        error_msg = str(error)
        error_type = type(error).__name__
        
        # Timeout errors
        if "timeout" in error_msg.lower() or error_type == "TimeoutError":
            client_type = getattr(self, '_current_client_type', 'unknown')
            return (
                f"⏱️ {context} timed out.\n\n"
                f"Suggestions:\n"
                f"• Try a smaller/faster model\n"
                f"• Check if {'Ollama is running' if client_type == 'ollama' else 'MiniMax API is available'}\n"
                f"• Simplify your request\n"
                f"• Current timeout: {self.config.ollama_timeout}s"
            )
        
        # Connection errors
        if any(kw in error_msg.lower() for kw in ['connection', 'refused', 'unreachable', 'urlerror']):
            return (
                f"🔌 Connection failed: {error_msg}\n\n"
                f"Check:\n"
                f"• Ollama running? Run: ollama serve\n"
                f"• API key set? (for MiniMax)\n"
                f"• Network connection"
            )
        
        # API errors
        if any(kw in error_msg.lower() for kw in ['api', 'unauthorized', 'key', '401', '403']):
            return (
                f"🔑 API Error: {error_msg}\n\n"
                f"For MiniMax:\n"
                f"• Set MINIMAX_API_KEY env var\n"
                f"• Check API key is valid\n"
                f"• Add credits at minimaxi.com (error 1008 = no balance)\n\n"
                f"For Ollama:\n"
                f"• Check ollama is running"
            )
        
        # Balance/credit errors
        if any(kw in error_msg.lower() for kw in ['balance', 'credit', '1008', 'insufficient']):
            return (
                f"💳 {error_msg}\n\n"
                f"Your MiniMax account has no credits.\n\n"
                f"Solutions:\n"
                f"• Visit https://platform.minimax.io to add balance\n"
                f"• Check your billing dashboard\n"
                f"• Or use a local Ollama model instead:\n"
                f"  tide models --set llama3.1"
            )
        
        # Model not found
        if any(kw in error_msg.lower() for kw in ['not found', '404', 'model']):
            return (
                f"🤖 Model not found: {error_msg}\n\n"
                f"Solutions:\n"
                f"• Pull model: ollama pull {self.config.model.split(':')[0]}\n"
                f"• Check available: ollama list\n"
                f"• Switch model: tide models --set llama3.1"
            )
        
        # Generic error
        return f"❌ {context} failed: {error_msg}"
    
    def _safe_chat(self, model: str, messages: List[ChatMessage], context: str = "Request") -> ChatResponse:
        """Safely send chat request with error handling"""
        try:
            client, client_type = self._get_client(model)
            self._current_client = client
            self._current_client_type = client_type
            
            return client.chat(model=model, messages=messages)
            
        except Exception as e:
            error_msg = self._handle_error(e, context)
            raise Exception(error_msg)
    
    def _update_system_prompt(self) -> None:
        """Update system prompt"""
        # Check if using MiniMax (no tool support)
        _, client_type = self._get_client(self.config.model)
        if client_type == 'minimax':
            # Simple system prompt without tools for MiniMax
            system_prompt = "You are Tide OS, an AI coding assistant. Help the user with coding tasks."
        else:
            # Use the built-in system prompt for Ollama
            system_prompt = self.SYSTEM_PROMPT
        
        # Update or add system message
        if self.session.messages and self.session.messages[0].role == "system":
            self.session.messages[0].content = system_prompt
        else:
            self.session.messages.insert(0, ChatMessage(role="system", content=system_prompt))
    
    def _needs_tool(self, message: str) -> bool:
        """Check if user message likely requires tool usage"""
        msg_lower = message.lower()
        
        # Check for action keywords
        has_action = any(keyword in msg_lower for keyword in self.ACTION_KEYWORDS)
        
        # Check if it's a question about something (not requesting action)
        is_question = any(q in msg_lower for q in ['what is', 'what are', 'how does', 'why is', 'explain', 'tell me about'])
        
        # Needs tool if it has action keywords and isn't just a question
        return has_action and not is_question
    
    def _parse_tool_call(self, content: str) -> Optional[Dict]:
        """Parse a tool call from LLM response"""
        # Pattern 1: Code blocks with json
        code_block_pattern = r'```(?:json)?\s*\n?(\{[\s\S]*?"tool"[\s\S]*?\})\n?\s*```'
        match = re.search(code_block_pattern, content)
        if match:
            try:
                data = json.loads(match.group(1))
                if "tool" in data:
                    if "params" not in data:
                        data["params"] = {}
                    return data
            except json.JSONDecodeError:
                pass
        
        # Pattern 2: Inline JSON with tool and params
        inline_pattern = r'\{\s*"tool"\s*:\s*"([^"]+)"(?:\s*,\s*"params"\s*:\s*(\{[\s\S]*?\}))?\s*\}'
        match = re.search(inline_pattern, content)
        if match:
            try:
                tool_name = match.group(1)
                params_str = match.group(2) or "{}"
                data = {
                    "tool": tool_name,
                    "params": json.loads(params_str)
                }
                return data
            except (json.JSONDecodeError, IndexError):
                pass
        
        # Pattern 3: Try to parse entire content as JSON
        try:
            data = json.loads(content.strip())
            if "tool" in data:
                if "params" not in data:
                    data["params"] = {}
                return data
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _execute_tool(self, tool_call: Dict) -> ToolResult:
        """Execute a tool call"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("params", {})
        
        if not tool_name:
            return ToolResult.error_result("No tool specified")
        
        return self.registry.execute(tool_name, **params)
    
    def chat(self, message: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """
        Send a message and get response with tool execution.
        
        Returns dict with:
        - response: str (AI's text response)
        - tool_call: Optional[Dict] (tool that was called)
        - tool_result: Optional[ToolResult] (result of tool execution)
        - success: bool (overall success)
        """
        result = {
            "response": "",
            "tool_call": None,
            "tool_result": None,
            "success": True
        }
        
        # Detect special commands
        msg_lower = message.lower().strip()
        
        # Quick codebase analysis - no LLM needed!
        if any(kw in msg_lower for kw in ['analyze codebase', 'analyze code', 'explore project', 'what files', 'show project structure', 'project structure']):
            analysis = self.analyze_codebase()
            result["response"] = analysis.get("output", analysis.get("error", "Could not analyze"))
            return result
        
        # Add user message
        self.session.add_message("user", message)
        
        # Check if this likely needs a tool
        needs_tool = self._needs_tool(message)
        
        # Get response from LLM with better error handling
        try:
            response = self._safe_chat(
                model=self.config.model,
                messages=self.session.messages,
                context="AI response"
            )
        except Exception as e:
            result["response"] = str(e)  # Already formatted by _handle_error
            result["success"] = False
            return result
        
        content = response.content
        
        # Always try to parse tool call from response (works for both Ollama and MiniMax)
        # MiniMax may output tool JSON in text form even though it doesn't support function calling
        tool_call = self._parse_tool_call(content)
        
        if tool_call:
            # Store tool call info
            result["tool_call"] = tool_call
            tool_name = tool_call.get("tool", "unknown")
            params = tool_call.get("params", {})
            
            # Check if we need confirmation
            tool = self.registry.get(tool_name)
            confirmed = True
            
            if tool and tool.require_confirmation and not auto_confirm:
                # Return without executing - let UI handle confirmation
                result["needs_confirmation"] = True
                result["tool_name"] = tool_name
                result["tool_params"] = params
                result["response"] = f"🔧 Tool call ready: {tool_name}"
                return result
            
            # Execute tool
            tool_result = self._execute_tool(tool_call)
            result["tool_result"] = tool_result
            
            # Add to conversation history
            self.session.add_message("assistant", f"Using tool: {tool_name}")
            
            result_msg = tool_result.output
            if not tool_result.success:
                result_msg = f"Error: {tool_result.error}\n{tool_result.output}"
            
            self.session.add_message("tool", result_msg)
            
            # Get follow-up response from AI
            try:
                follow_up = self._safe_chat(
                    model=self.config.model,
                    messages=self.session.messages,
                    context="Follow-up response"
                )
                result["response"] = follow_up.content
                self.session.add_message("assistant", follow_up.content)
            except Exception as e:
                error_msg = self._handle_error(e, "Follow-up")
                result["response"] = f"Tool result:\n{result_msg}\n\n{error_msg}"
        else:
            # No tool call, just text response
            result["response"] = content
            self.session.add_message("assistant", content)
        
        return result
    
    def execute_confirmed_tool(self, tool_call: Dict) -> ToolResult:
        """Execute a tool after user confirmation"""
        return self._execute_tool(tool_call)
    
    def reset(self) -> None:
        """Reset the conversation session"""
        self.session = Session()
        self._update_system_prompt()
    
    def list_models(self) -> List[str]:
        """List available models from all providers"""
        all_models = []
        
        # Ollama models
        try:
            if self.ollama_client:
                models = self.ollama_client.list_models()
                all_models.extend([f"[ollama] {m.get('name', 'unknown')}" for m in models])
        except Exception as e:
            all_models.append(f"[ollama] Error: {e}")
        
        # MiniMax models (if available)
        if self.minimax_client and self.minimax_client.is_available():
            try:
                models = self.minimax_client.list_models()
                all_models.extend([f"[minimax] {m.get('name', 'unknown')}" for m in models])
            except Exception as e:
                all_models.append(f"[minimax] Error: {e}")
        
        return all_models if all_models else ["No models available"]
    
    def check_model(self) -> bool:
        """Check if the configured model is available"""
        model_name = self.config.model.lower()
        
        # Check if it's a MiniMax model
        if any(m in model_name for m in ['minimax', 'abab']):
            return self.minimax_client is not None and self.minimax_client.is_available()
        
        # Otherwise check Ollama
        try:
            models = self.ollama_client.list_models()
            model_names = [m.get("name", "").lower() for m in models]
            return any(self.config.model.lower() in name or name in self.config.model.lower() for name in model_names)
        except:
            return False
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Quick analyze of the entire codebase - no LLM needed"""
        from pathlib import Path
        import os
        
        root = Path(".")
        if not root.exists():
            return {"error": "Directory not found"}
        
        # Count files by extension
        stats = {
            "total_files": 0,
            "by_extension": {},
            "largest_files": [],
            "dirs": []
        }
        
        # Scan files
        for ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.yaml', '.yml', '.toml']:
            files = list(root.rglob(f"*{ext}"))
            stats["by_extension"][ext] = len(files)
            stats["total_files"] += len(files)
        
        # Find largest files
        all_files = []
        for f in root.rglob("*"):
            if f.is_file() and f.stat().st_size > 1000:
                all_files.append((f, f.stat().st_size))
        
        all_files.sort(key=lambda x: x[1], reverse=True)
        stats["largest_files"] = [
            {"path": str(f.relative_to(root)), "size": s}
            for f, s in all_files[:10]
        ]
        
        # Count directories
        stats["dirs"] = [str(d.relative_to(root)) for d in root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        # Format output
        output = f"""# 📊 Codebase Analysis

## Summary
- **Total Files:** {stats['total_files']}
- **Directories:** {len(stats['dirs'])}

## Files by Type
"""
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: -x[1]):
            if count > 0:
                output += f"- **{ext}**: {count} files\n"
        
        output += "\n## 📁 Top Directories\n"
        for d in stats['dirs'][:10]:
            output += f"- {d}/\n"
        
        output += "\n## 📄 Largest Files\n"
        for f in stats['largest_files'][:10]:
            output += f"- {f['path']} ({f['size']} bytes)\n"
        
        return {
            "success": True,
            "output": output,
            "stats": stats
        }
