"""TodoList tool - List all todo items."""

from agent.tools.base import Tool, ToolResult
from agent.core.todo import TodoManager

# Shared instance
_todo_manager: TodoManager | None = None


def set_todo_manager(tm: TodoManager) -> None:
    """Set the global todo manager instance."""
    global _todo_manager
    _todo_manager = tm


class TodoListTool(Tool):
    """List all pending todo items."""

    name = "todo_list"
    description = "List all pending todo items."

    def execute(self) -> ToolResult:
        """List all pending todos."""
        if _todo_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TodoManager not initialized",
            )

        todos = _todo_manager.list()
        if not todos:
            return ToolResult(
                tool_call_id="",
                output="No pending todos.",
            )

        lines = []
        for i, todo in enumerate(todos, 1):
            lines.append(f"{i}. [{todo.id}] (priority={todo.priority}) {todo.task}")

        return ToolResult(
            tool_call_id="",
            output="\n".join(lines),
        )
