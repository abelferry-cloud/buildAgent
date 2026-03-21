"""BackgroundWait tool - Wait for a background job to complete."""

from typing import Optional

from agent.tools.base import Tool, ToolResult
from agent.core.background import BackgroundManager

_background_manager: BackgroundManager | None = None


def set_background_manager(bm: BackgroundManager) -> None:
    """Set the global background manager instance."""
    global _background_manager
    _background_manager = bm


class BackgroundWaitTool(Tool):
    """Wait for a background job to complete."""

    name = "background_wait"
    description = "Wait for a background job to complete and get its result."

    def execute(self, job_id: str, timeout: Optional[float] = None) -> ToolResult:
        """Wait for a job to complete."""
        if _background_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="BackgroundManager not initialized",
            )

        try:
            result = _background_manager.wait(job_id, timeout=timeout)
            return ToolResult(
                tool_call_id="",
                output=f"Job {job_id} completed: {result}",
            )
        except TimeoutError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
        except KeyError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
        except RuntimeError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
