"""TeamStatus tool - Get or set teammate status."""

from typing import Optional

from agent.tools.base import Tool, ToolResult
from agent.core.teams import TeammateManager, TeammateStatus

_teammate_manager: TeammateManager | None = None


def set_teammate_manager(tm: TeammateManager) -> None:
    """Set the global teammate manager instance."""
    global _teammate_manager
    _teammate_manager = tm


class TeamStatusTool(Tool):
    """Get or set the status of a teammate."""

    name = "team_status"
    description = "Get or set the status of a teammate. Status can be: idle, busy, offline."

    def execute(self, name: str, status: Optional[str] = None) -> ToolResult:
        """Get or set teammate status."""
        if _teammate_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TeammateManager not initialized",
            )

        if status is not None:
            # Set status
            try:
                teammate_status = TeammateStatus(status)
                _teammate_manager.set_teammate_status(name, teammate_status)
                return ToolResult(
                    tool_call_id="",
                    output=f"Set {name} status to {teammate_status.value}",
                )
            except ValueError:
                return ToolResult(
                    tool_call_id="",
                    output="",
                    error=f"Invalid status: {status}. Valid values: idle, busy, offline",
                )
        else:
            # Get status
            current_status = _teammate_manager.get_teammate_status(name)
            return ToolResult(
                tool_call_id="",
                output=f"{name} is {current_status.value}",
            )
