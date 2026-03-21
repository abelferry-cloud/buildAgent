"""TaskList tool - List tasks with optional filtering."""

from typing import Optional

from agent.tools.base import Tool, ToolResult
from agent.core.tasks import TaskManager, TaskStatus

_task_manager: TaskManager | None = None


def set_task_manager(tm: TaskManager) -> None:
    """Set the global task manager instance."""
    global _task_manager
    _task_manager = tm


class TaskListTool(Tool):
    """List tasks with optional status filtering."""

    name = "task_list"
    description = "List all tasks, optionally filtered by status."

    def execute(self, status: Optional[str] = None) -> ToolResult:
        """List tasks, optionally filtered by status."""
        if _task_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskManager not initialized",
            )

        # Convert status string to TaskStatus enum
        task_status = None
        if status is not None:
            try:
                task_status = TaskStatus(status)
            except ValueError:
                return ToolResult(
                    tool_call_id="",
                    output="",
                    error=f"Invalid status: {status}. Valid values: pending, in_progress, completed, blocked",
                )

        tasks = _task_manager.list_tasks(status=task_status)
        if not tasks:
            return ToolResult(
                tool_call_id="",
                output="No tasks found.",
            )

        lines = []
        for task in tasks:
            deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
            assigned = f" [assigned: {task.assigned_to}]" if task.assigned_to else ""
            lines.append(
                f"[{task.id}] {task.status.value} (priority={task.priority}){assigned} {task.title}{deps}"
            )

        return ToolResult(
            tool_call_id="",
            output="\n".join(lines),
        )
