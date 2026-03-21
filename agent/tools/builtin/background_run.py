"""BackgroundRun tool - Start a job in the background."""

from agent.tools.base import Tool, ToolResult
from agent.core.background import BackgroundManager

_background_manager: BackgroundManager | None = None


def set_background_manager(bm: BackgroundManager) -> None:
    """Set the global background manager instance."""
    global _background_manager
    _background_manager = bm


class BackgroundRunTool(Tool):
    """Start a job in the background."""

    name = "background_run"
    description = "Start a long-running job in the background."

    def execute(self, name: str, coro_ref: str) -> ToolResult:
        """Start a background job."""
        if _background_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="BackgroundManager not initialized",
            )

        try:
            job_id = _background_manager.run_in_background(name, coro_ref)
            return ToolResult(
                tool_call_id="",
                output=f"Started background job: {job_id}",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
