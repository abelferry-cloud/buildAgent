"""Read tool - Read file contents."""

import os
from agent.tools.base import Tool, ToolResult


class ReadTool(Tool):
    """Read file contents."""

    name = "read"
    description = "Read the contents of a file."

    def execute(self, path: str, offset: int = 0, limit: int = None) -> ToolResult:
        """Read file at path, optionally with offset and limit."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                if offset > 0:
                    f.seek(offset)
                content = f.read(limit) if limit else f.read()
            return ToolResult(
                tool_call_id="",
                output=content,
            )
        except FileNotFoundError:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"File not found: {path}",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
