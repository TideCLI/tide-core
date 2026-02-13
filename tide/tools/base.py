"""
Base tool class with validation - crush-inspired architecture
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class ParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class Parameter:
    """Tool parameter definition with validation"""
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None
    
    def validate(self, value: Any) -> Optional[str]:
        """Validate a value against this parameter. Returns error message or None."""
        if value is None:
            if self.required:
                return f"Required parameter '{self.name}' is missing"
            return None
        
        # Type checking
        type_map = {
            ParameterType.STRING: str,
            ParameterType.INTEGER: int,
            ParameterType.BOOLEAN: bool,
            ParameterType.ARRAY: list,
            ParameterType.OBJECT: dict,
        }
        
        expected_type = type_map.get(self.type)
        if expected_type and not isinstance(value, expected_type):
            return f"Parameter '{self.name}' must be {self.type.value}, got {type(value).__name__}"
        
        # Enum checking
        if self.enum and value not in self.enum:
            return f"Parameter '{self.name}' must be one of: {', '.join(self.enum)}"
        
        return None


@dataclass
class ValidationResult:
    """Result of parameter validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class ToolContext:
    """Context passed to tools during execution"""
    working_dir: str
    config: Dict[str, Any] = field(default_factory=dict)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)


@dataclass
class ToolResult:
    """Result of tool execution - like crush's result tracking"""
    success: bool
    output: str = ""
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(cls, output: str = "", **data) -> "ToolResult":
        return cls(success=True, output=output, data=data)
    
    @classmethod
    def error_result(cls, error: str, output: str = "") -> "ToolResult":
        return cls(success=False, error=error, output=output)


class Tool(ABC):
    """
    Base tool class - crush-inspired with:
    - Parameter validation
    - Confirmation prompts for risky operations
    - Rich result tracking
    """
    
    # Tool metadata
    name: str = ""
    description: str = ""
    parameters: Dict[str, Parameter] = {}
    
    # Safety settings
    require_confirmation: bool = False
    dangerous: bool = False
    
    # Categories for organization
    category: str = "general"  # filesystem, system, code, etc.
    
    def __init__(self, context: Optional[ToolContext] = None):
        self.context = context or ToolContext(working_dir=".")
    
    def validate(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate parameters against tool schema.
        Like crush's parameter validation.
        """
        errors = []
        
        # Check for unknown parameters
        unknown = set(params.keys()) - set(self.parameters.keys())
        if unknown:
            errors.append(f"Unknown parameters: {', '.join(unknown)}")
        
        # Validate each parameter
        for name, param in self.parameters.items():
            value = params.get(name)
            error = param.validate(value)
            if error:
                errors.append(error)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def confirm(self, params: Dict[str, Any]) -> bool:
        """
        Ask for confirmation before executing dangerous operations.
        Override for custom confirmation logic.
        """
        if not self.require_confirmation:
            return True
        
        # Default confirmation prompt
        print(f"\n⚠️  {self.name} requires confirmation")
        print(f"   Description: {self.description}")
        print(f"   Parameters: {params}")
        
        response = input("Proceed? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def execute(self, **params) -> ToolResult:
        """
        Execute the tool with validation and confirmation.
        This is the main entry point.
        """
        # Validate
        validation = self.validate(params)
        if not validation.valid:
            return ToolResult.error_result(
                f"Validation failed: {'; '.join(validation.errors)}"
            )
        
        # Execute (confirmation handled by caller if needed)
        try:
            return self._execute(**params)
        except Exception as e:
            return ToolResult.error_result(f"Execution error: {str(e)}")
    
    @abstractmethod
    def _execute(self, **params) -> ToolResult:
        """Override this with actual tool logic"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for this tool"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "require_confirmation": self.require_confirmation,
            "parameters": {
                name: {
                    "type": param.type.value,
                    "description": param.description,
                    "required": param.required,
                    **({"enum": param.enum} if param.enum else {}),
                    **({"default": param.default} if param.default is not None else {})
                }
                for name, param in self.parameters.items()
            }
        }
