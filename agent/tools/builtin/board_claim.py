"""s11: Board Claim tool - Claim a specific task from the board."""

from agent.core.autonomous import TaskBoard
from agent.tools.base import Tool, ToolResult


# Shared instance
_board: TaskBoard | None = None


def set_board(board: TaskBoard) -> None:
    """Set the global task board instance."""
    global _board
    _board = board


class BoardClaimTool(Tool):
    """Claim a specific task from the board."""

    name = "board_claim"
    description = "Claim a specific task by ID from the task board."

    def execute(
        self,
        task_id: str,
        worker: str,
    ) -> ToolResult:
        """
        Claim a task.

        Args:
            task_id: The task ID to claim
            worker: The worker claiming the task

        Returns:
            ToolResult indicating success or failure
        """
        if _board is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskBoard not initialized",
            )

        if not task_id:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Task ID is required",
            )

        if not worker:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Worker ID is required",
            )

        success = _board.claim_task(task_id, worker)

        if success:
            return ToolResult(
                tool_call_id="",
                output=f"Claimed task: {task_id}",
            )
        else:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Failed to claim task {task_id} - task may not exist or already claimed",
            )
