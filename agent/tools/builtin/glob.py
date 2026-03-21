"""Glob tool - Find files by pattern."""

import glob as glob_module
from agent.tools.base import Tool, ToolResult


class GlobTool(Tool):
    """Find files matching a pattern."""

    name = "glob"
    description = "Find files matching a glob pattern."

    def execute(self, pattern: str, path: str = ".") -> ToolResult:
        """Find files matching pattern in path."""
        try:
            full_pattern = f"{path}/{pattern}" if path != "." else pattern
            matches = glob_module.glob(full_pattern, recursive=True)
            output = "\n".join(matches) if matches else "No matches found."
            return ToolResult(
                tool_call_id="",
                output=output,
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
