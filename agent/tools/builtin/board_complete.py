"""s11: Board Complete tool - Mark a task as complete on the board."""

import json

from agent.core.autonomous import TaskBoard
from agent.tools.base import Tool, ToolResult


# Shared instance
_board: TaskBoard | None = None


def set_board(board: TaskBoard) -> None:
    """Set the global task board instance."""
    global _board
    _board = board


class BoardCompleteTool(Tool):
    """Mark a task as complete on the board."""

    name = "board_complete"
    description = "Mark a task as complete with optional result data."

    def execute(
        self,
        task_id: str,
        result: str | None = None,
    ) -> ToolResult:
        """
        Complete a task.

        Args:
            task_id: The task ID to mark complete
            result: Optional JSON result data

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

        result_data = None
        if result:
            try:
                result_data = json.loads(result)
            except json.JSONDecodeError:
                result_data = {"raw": result}

        success = _board.complete_task(task_id, result_data)

        if success:
            return ToolResult(
                tool_call_id="",
                output=f"Completed task: {task_id}",
            )
        else:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Failed to complete task {task_id} - task may not exist or not claimed",
            )
