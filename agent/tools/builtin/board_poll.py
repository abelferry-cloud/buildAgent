"""s11: Board Poll tool - Poll for available tasks from the board."""

from agent.core.autonomous import TaskBoard
from agent.tools.base import Tool, ToolResult


# Shared instance
_board: TaskBoard | None = None


def set_board(board: TaskBoard) -> None:
    """Set the global task board instance."""
    global _board
    _board = board


class BoardPollTool(Tool):
    """Poll the task board for an available task."""

    name = "board_poll"
    description = "Poll for an available task from the task board. Claims the task atomically."

    def execute(
        self,
        worker: str,
        timeout: float = 30.0,
    ) -> ToolResult:
        """
        Poll for a task.

        Args:
            worker: The worker name/ID polling for work
            timeout: Maximum time to wait for a task

        Returns:
            ToolResult with task details if available
        """
        if _board is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskBoard not initialized",
            )

        if not worker:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Worker ID is required",
            )

        task = _board.poll(worker, timeout)

        if task is None:
            return ToolResult(
                tool_call_id="",
                output="No tasks available",
            )

        import json

        task_info = {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "claimed_by": task.claimed_by,
        }

        return ToolResult(
            tool_call_id="",
            output=json.dumps(task_info),
        )
