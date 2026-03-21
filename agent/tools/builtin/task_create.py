"""TaskCreate tool - Create a new task."""

from typing import Optional

from agent.tools.base import Tool, ToolResult
from agent.core.tasks import TaskCreate, TaskManager, TaskStatus

_task_manager: TaskManager | None = None


def set_task_manager(tm: TaskManager) -> None:
    """Set the global task manager instance."""
    global _task_manager
    _task_manager = tm


class TaskCreateTool(Tool):
    """Create a new task."""

    name = "task_create"
    description = "Create a new task with optional dependencies."

    def execute(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        depends_on: Optional[list[str]] = None,
        assigned_to: Optional[str] = None,
    ) -> ToolResult:
        """Create a new task."""
        if _task_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskManager not initialized",
            )

        try:
            task_create = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                depends_on=depends_on or [],
                assigned_to=assigned_to,
            )
            task_id = _task_manager.create_task(task_create)
            return ToolResult(
                tool_call_id="",
                output=f"Created task: {task_id}",
            )
        except ValueError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
