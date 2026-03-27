"""
Base Tool Class

Abstract base class for all agent tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.success:
            return str(self.data)
        return f"Error: {self.error}"


class BaseTool(ABC):
    """
    Abstract base class for agent tools.
    
    Subclasses must implement:
        - name: Tool identifier
        - description: What the tool does (shown to LLM)
        - parameters: JSON schema for tool inputs
        - execute: Actual tool logic
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (identifier)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the LLM."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON schema for tool parameters."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
    
    def to_openai_tool(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
