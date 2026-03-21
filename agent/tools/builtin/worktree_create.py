"""s12: Worktree Create tool - Create a new worktree."""

from agent.core.worktree import WorktreeConfig, WorktreeManager
from agent.tools.base import Tool, ToolResult


# Shared instance
_worktree_manager: WorktreeManager | None = None


def set_worktree_manager(wm: WorktreeManager) -> None:
    """Set the global worktree manager instance."""
    global _worktree_manager
    _worktree_manager = wm


class WorktreeCreateTool(Tool):
    """Create a new worktree."""

    name = "worktree_create"
    description = "Create a new isolated worktree with its own directory."

    def execute(
        self,
        name: str,
        branch: str = "main",
        tools: str | None = None,
        memory_limit_mb: int = 512,
        cpu_limit_percent: int = 100,
    ) -> ToolResult:
        """
        Create a new worktree.

        Args:
            name: Unique name for the worktree
            branch: Git branch to use
            tools: Comma-separated list of tools to enable
            memory_limit_mb: Memory limit in MB
            cpu_limit_percent: CPU limit percentage

        Returns:
            ToolResult with worktree info on success
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

        # Parse tools list
        tools_list = []
        if tools:
            tools_list = [t.strip() for t in tools.split(",") if t.strip()]

        config = WorktreeConfig(
            branch=branch,
            tools=tools_list,
            memory_limit_mb=memory_limit_mb,
            cpu_limit_percent=cpu_limit_percent,
        )

        try:
            worktree = _worktree_manager.create_worktree(name, config)
            return ToolResult(
                tool_call_id="",
                output=f"Created worktree: {name} at {worktree.path}",
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
                error=f"Failed to create worktree: {str(e)}",
            )
