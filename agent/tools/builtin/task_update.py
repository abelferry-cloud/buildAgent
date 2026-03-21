"""TaskUpdate tool - Update an existing task."""

from agent.tools.base import Tool, ToolResult
from agent.core.tasks import TaskManager, TaskStatus, TaskUpdate

_task_manager: TaskManager | None = None


def set_task_manager(tm: TaskManager) -> None:
    """Set the global task manager instance."""
    global _task_manager
    _task_manager = tm


class TaskUpdateTool(Tool):
    """Update an existing task."""

    name = "task_update"
    description = "Update an existing task's properties."

    def execute(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: int | None = None,
        assigned_to: str | None = None,
    ) -> ToolResult:
        """Update an existing task."""
        if _task_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskManager not initialized",
            )

        try:
            # Convert status string to TaskStatus enum
            task_status = None
            if status is not None:
                task_status = TaskStatus(status)

            update = TaskUpdate(
                title=title,
                description=description,
                status=task_status,
                priority=priority,
                assigned_to=assigned_to,
            )
            _task_manager.update_task(task_id, update)
            return ToolResult(
                tool_call_id="",
                output=f"Updated task: {task_id}",
            )
        except KeyError as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
