"""TodoAdd tool - Add a todo item."""

from agent.tools.base import Tool, ToolResult
from agent.core.todo import TodoManager

# Shared instance (in real impl, would be injected)
_todo_manager: TodoManager | None = None


def set_todo_manager(tm: TodoManager) -> None:
    """Set the global todo manager instance."""
    global _todo_manager
    _todo_manager = tm


class TodoAddTool(Tool):
    """Add a todo item."""

    name = "todo_add"
    description = "Add a new todo item."

    def execute(self, task: str, priority: int = 0) -> ToolResult:
        """Add a todo item."""
        if _todo_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TodoManager not initialized",
            )
        todo_id = _todo_manager.add(task, priority)
        return ToolResult(
            tool_call_id="",
            output=f"Added todo: {todo_id}",
        )
