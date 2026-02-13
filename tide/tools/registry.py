"""
Tool registry - manages all available tools
Inspired by crush's tool management system + Claude Code/OpenCode
"""
from typing import Dict, List, Optional, Type, Any, Callable
from .base import Tool, ToolContext, ToolResult
from . import advanced


class ToolRegistry:
    """Registry for managing and accessing tools"""
    
    def __init__(self):
        self._tools: Dict[str, Type[Tool]] = {}
        self._context: Optional[ToolContext] = None
        self._func_tools: Dict[str, Callable] = {}  # Advanced function tools
    
    def register(self, tool_class: Type[Tool]) -> Type[Tool]:
        """Register a tool class. Can be used as decorator."""
        self._tools[tool_class.name] = tool_class
        return tool_class
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function-based tool (like Claude Code)"""
        self._func_tools[name] = func
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool instance by name"""
        tool_class = self._tools.get(name)
        if tool_class:
            return tool_class(context=self._context)
        return None
    
    def execute(self, name: str, **params) -> ToolResult:
        """Execute a tool by name with parameters"""
        # First try function tools (fast, like Claude Code)
        if name in self._func_tools:
            try:
                func = self._func_tools[name]
                result = func(**params)
                if isinstance(result, ToolResult):
                    return result
                return ToolResult(success=True, output=str(result))
            except Exception as e:
                return ToolResult(success=False, error=str(e))
        
        # Fall back to class tools
        tool = self.get(name)
        if not tool:
            return ToolResult.error_result(f"Unknown tool: {name}")
        return tool.execute(**params)
    
    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all registered tools"""
        tools = list(self._tools.keys())
        tools.extend(list(self._func_tools.keys()))
        return sorted(set(tools))
    
    def get_categories(self) -> List[str]:
        """Get all tool categories"""
        categories = set(cls.category for cls in self._tools.values())
        categories.add("advanced")  # For function tools
        return sorted(categories)
    
    def set_context(self, context: ToolContext) -> None:
        """Set context for all tool instances"""
        self._context = context
    
    def get_all_schemas(self) -> Dict[str, Any]:
        """Get schemas for all registered tools"""
        return {
            name: cls.get_schema(cls()) 
            for name, cls in self._tools.items()
        }
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get OpenAI-style function definitions for all tools"""
        functions = []
        for name, cls in self._tools.items():
            tool = cls()
            schema = tool.get_schema()
            
            # Convert to OpenAI function format
            func = {
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # Add parameters
            for param_name, param_info in schema.get("parameters", {}).items():
                func["function"]["parameters"]["properties"][param_name] = {
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", "")
                }
                if param_info.get("required", False):
                    func["function"]["parameters"]["required"].append(param_name)
            
            functions.append(func)
        
        return functions
    
    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get tools organized by category"""
        result: Dict[str, List[Dict[str, Any]]] = {}
        for name, cls in self._tools.items():
            cat = cls.category
            if cat not in result:
                result[cat] = []
            
            # Create minimal info
            result[cat].append({
                "name": name,
                "description": cls.description,
                "require_confirmation": cls.require_confirmation
            })
        return result


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def register_tool(tool_class: Type[Tool]) -> Type[Tool]:
    """Register a tool with the global registry"""
    return get_registry().register(tool_class)


def get_tool(name: str) -> Optional[Tool]:
    """Get a tool from the global registry"""
    return get_registry().get(name)


def list_tools(category: Optional[str] = None) -> List[str]:
    """List tools from the global registry"""
    return get_registry().list_tools(category)
