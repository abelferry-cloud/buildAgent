"""s12: Worktree Switch tool - Switch to a different worktree."""

from agent.core.worktree import WorktreeManager
from agent.tools.base import Tool, ToolResult


# Shared instance
_worktree_manager: WorktreeManager | None = None


def set_worktree_manager(wm: WorktreeManager) -> None:
    """Set the global worktree manager instance."""
    global _worktree_manager
    _worktree_manager = wm


class WorktreeSwitchTool(Tool):
    """Switch to a different worktree."""

    name = "worktree_switch"
    description = "Switch the active context to a different worktree."

    def execute(
        self,
        name: str,
    ) -> ToolResult:
        """
        Switch to a worktree.

        Args:
            name: The worktree name to switch to

        Returns:
            ToolResult indicating success or failure
        """
        if _worktree_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="WorktreeManager not initialized",
            )

        if not name:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Worktree name is required",
            )

        try:
            _worktree_manager.switch_worktree(name)
            return ToolResult(
                tool_call_id="",
                output=f"Switched to worktree: {name}",
            )
        except ValueError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
