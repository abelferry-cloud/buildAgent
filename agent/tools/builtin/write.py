"""Write tool - Write content to a file."""

import os
from agent.tools.base import Tool, ToolResult


class WriteTool(Tool):
    """Write content to a file."""

    name = "write"
    description = "Write content to a file. Creates the file if it doesn't exist."

    def execute(self, path: str, content: str) -> ToolResult:
        """Write content to file at path."""
        try:
            # Ensure parent directory exists
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(
                tool_call_id="",
                output=f"Successfully wrote to {path}",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
