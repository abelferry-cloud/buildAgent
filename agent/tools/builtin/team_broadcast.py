"""TeamBroadcast tool - Broadcast a message to all teammates."""

from agent.tools.base import Tool, ToolResult
from agent.core.teams import TeammateManager

_teammate_manager: TeammateManager | None = None


def set_teammate_manager(tm: TeammateManager) -> None:
    """Set the global teammate manager instance."""
    global _teammate_manager
    _teammate_manager = tm


class TeamBroadcastTool(Tool):
    """Broadcast a message to all teammates."""

    name = "team_broadcast"
    description = "Broadcast a message to all teammates in the team."

    def execute(self, message: str) -> ToolResult:
        """Broadcast a message to all teammates."""
        if _teammate_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TeammateManager not initialized",
            )

        message_ids = _teammate_manager.broadcast(message)
        if not message_ids:
            return ToolResult(
                tool_call_id="",
                output="No teammates to broadcast to.",
            )

        return ToolResult(
            tool_call_id="",
            output=f"Broadcast sent to {len(message_ids)} teammate(s)",
        )
