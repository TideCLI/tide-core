"""
Tide Agent - Main AI agent with tool support
Optimized based on charmbracelet/crush architecture
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

from .ollama_client import OllamaClient, Message, ToolCall
from .tool_registry import ToolRegistry
from .tools.base import ToolResult


@dataclass
class ChatResponse:
    """Response from chat"""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TideAgent:
    """Main AI agent for Tide"""
    
    SYSTEM_PROMPT = """You are Tide, an AI coding assistant powered by local Ollama models.

Your goal is to help users with coding tasks by:
1. Understanding their requirements
2. Reading and analyzing code
3. Making precise edits
4. Running commands when needed

When you need to perform actions, use the available tools by calling them.
Wait for the tool results before continuing.

Be concise but thorough in your responses.
"""
    
    def __init__(self, model: str = "qwen3:latest", working_dir: str = "."):
        self.model = model
        self.working_dir = working_dir
        self.client = OllamaClient(model=model)
        self.tools = ToolRegistry(working_dir)
        self.messages: List[Message] = []
        self._register_default_tools()
        
    def _register_default_tools(self):
        """Register all default tools"""
        from .tools.filesystem import ViewTool, LSTool, EditTool, WriteTool, GlobTool
        from .tools.system import BashTool, PythonTool
        from .tools.code import AnalyzeTool, GrepTool, TodosTool
        
        self.tools.register_all([
            ViewTool, LSTool, EditTool, WriteTool, GlobTool,
            BashTool, PythonTool,
            AnalyzeTool, GrepTool, TodosTool
        ])
    
    def chat(self, user_message: str, context: Optional[str] = None) -> ChatResponse:
        """Send a message and get response with potential tool calls"""
        
        # Build user message
        content = user_message
        if context:
            content = f"{context}\n\nUser: {user_message}"
        
        # Add user message
        self.messages.append(Message(role="user", content=content))
        
        # Get response from Ollama
        tools = self.tools.to_ollama_tools()
        response = self.client.chat(self.messages, tools=tools)
        
        # Check for errors
        if "error" in response:
            return ChatResponse(
                content=f"Error: {response['error']}",
                metadata={"error": response["error"]}
            )
        
        # Parse response
        message = response.get("message", {})
        assistant_content = message.get("content", "")
        
        # Parse tool calls
        tool_calls = self.client.parse_tool_calls(response)
        
        # Execute tools if any
        tools_used = []
        if tool_calls:
            # Add assistant message with tool calls
            self.messages.append(Message(
                role="assistant",
                content=assistant_content,
                tool_calls=[{"id": tc.id, "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}} for tc in tool_calls]
            ))
            
            # Execute each tool
            tool_results = []
            for tc in tool_calls:
                tools_used.append(tc.name)
                result = self.tools.execute(tc.name, tc.arguments)
                
                # Add tool result to messages
                tool_results.append({
                    "tool_call_id": tc.id,
                    "role": "tool",
                    "name": tc.name,
                    "content": result.output if result.success else result.error
                })
                
                self.messages.append(Message(
                    role="tool",
                    content=result.output if result.success else result.error,
                    tool_results=tool_results
                ))
            
            # Get final response after tool execution
            final_response = self.client.chat(self.messages, tools=tools)
            if "message" in final_response:
                assistant_content = final_response["message"].get("content", assistant_content)
        else:
            # Just add assistant message
            self.messages.append(Message(role="assistant", content=assistant_content))
        
        return ChatResponse(
            content=assistant_content,
            tool_calls=tool_calls,
            tools_used=tools_used,
            metadata={
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def execute_tool_directly(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool directly without chat"""
        return self.tools.execute(tool_name, params)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return self.tools.list_all()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a tool"""
        tool = self.tools.get(tool_name)
        if tool:
            return tool.to_dict()
        return None
    
    def clear_history(self):
        """Clear chat history"""
        self.messages.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "model": self.model,
            "messages": len(self.messages),
            "tools": self.tools.get_stats()
        }
