"""s12: Worktree Destroy tool - Destroy a worktree."""

from agent.core.worktree import WorktreeManager
from agent.tools.base import Tool, ToolResult


# Shared instance
_worktree_manager: WorktreeManager | None = None


def set_worktree_manager(wm: WorktreeManager) -> None:
    """Set the global worktree manager instance."""
    global _worktree_manager
    _worktree_manager = wm


class WorktreeDestroyTool(Tool):
    """Destroy a worktree."""

    name = "worktree_destroy"
    description = "Destroy a worktree and reclaim resources."

    def execute(
        self,
        name: str,
    ) -> ToolResult:
        """
        Destroy a worktree.

        Args:
            name: The worktree name to destroy

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
            _worktree_manager.destroy_worktree(name)
            return ToolResult(
                tool_call_id="",
                output=f"Destroyed worktree: {name}",
            )
        except ValueError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Failed to destroy worktree: {str(e)}",
            )
