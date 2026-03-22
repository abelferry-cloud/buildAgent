"""TodoStart tool - Mark a todo item as in_progress."""

from agent.tools.base import Tool, ToolResult
from agent.core.todo import TodoManager

# Shared instance
_todo_manager: TodoManager | None = None


def set_todo_manager(tm: TodoManager) -> None:
    """Set the global todo manager instance."""
    global _todo_manager
    _todo_manager = tm


class TodoStartTool(Tool):
    """Mark a todo item as in_progress (only one can be in_progress at a time)."""

    name = "todo_start"
    description = "Mark a todo item as in_progress. Only one todo can be in_progress at a time."

    def execute(self, todo_id: str) -> ToolResult:
        """Mark a todo as in_progress."""
        if _todo_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TodoManager not initialized",
            )

        if _todo_manager.start(todo_id):
            return ToolResult(
                tool_call_id="",
                output=f"Started todo {todo_id}.",
            )
        else:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Todo {todo_id} not found.",
            )