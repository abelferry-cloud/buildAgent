"""BackgroundCancel tool - Cancel a running background job."""

from agent.tools.base import Tool, ToolResult
from agent.core.background import BackgroundManager

_background_manager: BackgroundManager | None = None


def set_background_manager(bm: BackgroundManager) -> None:
    """Set the global background manager instance."""
    global _background_manager
    _background_manager = bm


class BackgroundCancelTool(Tool):
    """Cancel a running background job."""

    name = "background_cancel"
    description = "Cancel a running background job."

    def execute(self, job_id: str) -> ToolResult:
        """Cancel a background job."""
        if _background_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="BackgroundManager not initialized",
            )

        cancelled = _background_manager.cancel(job_id)
        if cancelled:
            return ToolResult(
                tool_call_id="",
                output=f"Cancelled job: {job_id}",
            )
        else:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Job '{job_id}' not found or already completed",
            )
