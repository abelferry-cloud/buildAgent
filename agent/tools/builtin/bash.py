"""Bash tool - Execute shell commands."""

import subprocess
from agent.tools.base import Tool, ToolResult


class BashTool(Tool):
    """Execute shell commands."""

    name = "bash"
    description = "Execute a shell command and return the output."

    def execute(self, command: str) -> ToolResult:
        """Execute the bash command."""
        import os
        import platform

        # Windows compatibility: convert 'mkdir -p dir' to 'mkdir dir'
        # since -p is not recognized by Windows cmd.exe
        if platform.system() == "Windows" and command.startswith("mkdir -p "):
            command = "mkdir " + command[9:]

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout + result.stderr
            return ToolResult(
                tool_call_id="",  # Will be set by caller
                output=output,
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}",
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Command timed out after 60 seconds",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
