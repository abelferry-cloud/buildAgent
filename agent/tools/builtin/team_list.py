"""TeamList tool - List all teammates in the team."""

from agent.tools.base import Tool, ToolResult
from agent.core.teams import TeammateManager

_teammate_manager: TeammateManager | None = None


def set_teammate_manager(tm: TeammateManager) -> None:
    """Set the global teammate manager instance."""
    global _teammate_manager
    _teammate_manager = tm


class TeamListTool(Tool):
    """List all teammates in the team."""

    name = "team_list"
    description = "List all teammates in the team with their roles and status."

    def execute(self) -> ToolResult:
        """List all teammates."""
        if _teammate_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TeammateManager not initialized",
            )

        teammates = _teammate_manager.list_teammates()
        if not teammates:
            return ToolResult(
                tool_call_id="",
                output="No teammates in the team.",
            )

        lines = []
        for tm in teammates:
            lines.append(f"[{tm.name}] {tm.role} - {tm.status.value}")

        return ToolResult(
            tool_call_id="",
            output="\n".join(lines),
        )
