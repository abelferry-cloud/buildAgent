"""s11: Board Post tool - Post a task to the task board."""

import uuid

from agent.core.autonomous import BoardTask, TaskBoard
from agent.tools.base import Tool, ToolResult


# Shared instance
_board: TaskBoard | None = None


def set_board(board: TaskBoard) -> None:
    """Set the global task board instance."""
    global _board
    _board = board


class BoardPostTool(Tool):
    """Post a new task to the task board."""

    name = "board_post"
    description = "Post a new task to the task board for workers to claim."

    def execute(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        task_id: str | None = None,
    ) -> ToolResult:
        """
        Post a task to the board.

        Args:
            title: The task title
            description: Detailed task description
            priority: Task priority (higher = more important)
            task_id: Optional specific ID for the task

        Returns:
            ToolResult with the task_id on success
        """
        if _board is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskBoard not initialized",
            )

        if not title:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Title is required",
            )

        if task_id:
            task = BoardTask(id=task_id, title=title, description=description, priority=priority)
        else:
            task = BoardTask(
                id=str(uuid.uuid4())[:8],
                title=title,
                description=description,
                priority=priority,
            )

        posted_id = _board.post_task(task=task)
        return ToolResult(
            tool_call_id="",
            output=f"Posted task: {posted_id}",
        )
