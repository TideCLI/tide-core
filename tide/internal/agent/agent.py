"""
Core Agent Implementation
"""

import json
import http.client
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from internal.tools.registry import ToolRegistry
from internal.agent.session import Session
from internal.agent.executor import ToolExecutor
from internal.config.settings import Settings


@dataclass
class AgentResponse:
    """Agent response"""
    content: str
    tools_used: List[str]
    success: bool


class Agent:
    """Main AI Agent"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tools = ToolRegistry()
        self.executor = ToolExecutor(self.tools)
        self.session: Optional[Session] = None
        self.max_iterations = 10
        
    def chat(self, message: str) -> AgentResponse:
        """Process message with tools"""
        if not self.session:
            self.session = Session()
        
        self.session.add_message("user", message)
        
        # Build conversation
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.session.messages[-10:]
        ]
        
        tools_used = []
        response_content = ""
        
        for iteration in range(self.max_iterations):
            # Call LLM
            ai_response = self._call_llm(history)
            
            # Check for tool calls
            tool_calls = self._extract_tool_calls(ai_response)
            
            if not tool_calls:
                response_content = ai_response
                break
            
            # Execute tools
            for tool_call in tool_calls:
                result = self.executor.execute(tool_call)
                tools_used.append(tool_call.get("name", "unknown"))
                
                # Add to history
                history.append({
                    "role": "assistant",
                    "content": f"Used tool: {tool_call.get('name')}"
                })
                history.append({
                    "role": "user",
                    "content": f"Result: {result.output if result.success else result.error}"
                })
        
        self.session.add_message("assistant", response_content, tools_used)
        
        return AgentResponse(
            content=response_content,
            tools_used=tools_used,
            success=True
        )
    
    def _call_llm(self, messages: List[Dict]) -> str:
        """Call Ollama API"""
        try:
            # Build system prompt with tools
            tools_desc = json.dumps(self.tools.to_schema(), indent=2)
            system_prompt = f"""You are Tide, an AI coding assistant.
Available tools:
{tools_desc}

Use tools by responding with:
<tool>{{"name": "tool_name", "parameters": {{}}}}</tool>
"""
            
            payload = {
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": system_prompt}
                ] + messages,
                "stream": False
            }
            
            conn = http.client.HTTPConnection(
                self.settings.ollama_host,
                self.settings.ollama_port,
                timeout=120
            )
            conn.request(
                "POST", "/api/chat",
                body=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            conn.close()
            
            return data.get("message", {}).get("content", "")
            
        except Exception as e:
            return f"Error: {e}"
    
    def _extract_tool_calls(self, text: str) -> List[Dict]:
        """Extract tool calls from response"""
        import re
        pattern = r'<tool>\s*(\{[^}]+\})\s*</tool>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        tool_calls = []
        for match in matches:
            try:
                tool_calls.append(json.loads(match))
            except:
                continue
        
        return tool_calls
