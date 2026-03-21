"""Base classes for the tool system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ToolResult:
    """Result from a tool execution."""

    tool_call_id: str
    output: str
    error: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class ToolCall:
    """A call to a tool."""

    id: str
    name: str
    arguments: dict[str, Any]


class Tool(ABC):
    """Base class for all tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given arguments."""
        pass

    def to_dict(self) -> dict:
        """Convert tool to a dictionary for LLM tool definitions."""
        return {
            "name": self.name,
            "description": self.description,
        }
