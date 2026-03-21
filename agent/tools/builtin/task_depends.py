"""TaskDepends tool - Add a dependency between tasks."""

from agent.tools.base import Tool, ToolResult
from agent.core.tasks import TaskManager

_task_manager: TaskManager | None = None


def set_task_manager(tm: TaskManager) -> None:
    """Set the global task manager instance."""
    global _task_manager
    _task_manager = tm


class TaskDependsTool(Tool):
    """Add a dependency between two tasks."""

    name = "task_depends"
    description = "Add a dependency so that task_id waits for depends_on to complete first."

    def execute(self, task_id: str, depends_on: str) -> ToolResult:
        """Add a dependency between tasks."""
        if _task_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TaskManager not initialized",
            )

        try:
            _task_manager.add_dependency(task_id, depends_on)
            return ToolResult(
                tool_call_id="",
                output=f"Added dependency: {task_id} depends on {depends_on}",
            )
        except (KeyError, ValueError) as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
