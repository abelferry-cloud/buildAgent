"""TodoDone tool - Mark a todo item as done."""

from agent.tools.base import Tool, ToolResult
from agent.core.todo import TodoManager

# Shared instance
_todo_manager: TodoManager | None = None


def set_todo_manager(tm: TodoManager) -> None:
    """Set the global todo manager instance."""
    global _todo_manager
    _todo_manager = tm


class TodoDoneTool(Tool):
    """Mark a todo item as done."""

    name = "todo_done"
    description = "Mark a todo item as completed."

    def execute(self, todo_id: str) -> ToolResult:
        """Mark a todo as done."""
        if _todo_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TodoManager not initialized",
            )

        if _todo_manager.done(todo_id):
            return ToolResult(
                tool_call_id="",
                output=f"Marked todo {todo_id} as done.",
            )
        else:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Todo {todo_id} not found.",
            )
