"""s12: Worktree List tool - List all worktrees."""

import json

from agent.core.worktree import WorktreeManager
from agent.tools.base import Tool, ToolResult


# Shared instance
_worktree_manager: WorktreeManager | None = None


def set_worktree_manager(wm: WorktreeManager) -> None:
    """Set the global worktree manager instance."""
    global _worktree_manager
    _worktree_manager = wm


class WorktreeListTool(Tool):
    """List all worktrees."""

    name = "worktree_list"
    description = "List all worktrees with their status and configuration."

    def execute(
        self,
        active_only: bool = False,
    ) -> ToolResult:
        """
        List worktrees.

        Args:
            active_only: If true, only show active (non-suspended) worktrees

        Returns:
            ToolResult with list of worktrees
        """
        if _worktree_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="WorktreeManager not initialized",
            )

        if active_only:
            worktrees = _worktree_manager.list_active_worktrees()
        else:
            worktrees = _worktree_manager.list_worktrees()

        if not worktrees:
            return ToolResult(
                tool_call_id="",
                output="No worktrees found",
            )

        worktree_info = []
        active = _worktree_manager.get_active_worktree()

        for wt in worktrees:
            info = {
                "name": wt.name,
                "id": wt.id,
                "path": wt.path,
                "state": wt.state.value,
                "is_active": active.name == wt.name if active else False,
                "branch": wt.config.branch,
                "tools": wt.config.tools,
                "created_at": wt.created_at,
                "last_active_at": wt.last_active_at,
            }
            worktree_info.append(info)

        return ToolResult(
            tool_call_id="",
            output=json.dumps(worktree_info, indent=2),
        )
