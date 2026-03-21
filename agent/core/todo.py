"""s03: TodoManager - Plan before you act with TodoWrite + nag reminder."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Todo:
    """A todo item."""

    id: str
    task: str
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    done: bool = False
    done_at: Optional[float] = None


class TodoManager:
    """
    Manages todo items with nag reminders.

    An agent without a plan drifts; list the steps first, then execute.
    """

    def __init__(self):
        self._todos: dict[str, Todo] = {}

    def add(self, task: str, priority: int = 0) -> str:
        """Add a new todo item. Returns the todo_id."""
        todo_id = str(uuid.uuid4())[:8]
        todo = Todo(id=todo_id, task=task, priority=priority)
        self._todos[todo_id] = todo
        return todo_id

    def list(self) -> List[Todo]:
        """List all todos, sorted by priority (highest first) then by created_at."""
        todos = [t for t in self._todos.values() if not t.done]
        todos.sort(key=lambda t: (-t.priority, t.created_at))
        return todos

    def done(self, todo_id: str) -> bool:
        """Mark a todo as done."""
        todo = self._todos.get(todo_id)
        if not todo:
            return False
        todo.done = True
        todo.done_at = time.time()
        return True

    def get(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return self._todos.get(todo_id)

    def nag(self) -> List[Todo]:
        """
        Return pending todos that need attention.

        In a full implementation, this could filter by age, priority, etc.
        For now, returns all pending todos.
        """
        return self.list()

    def pending_count(self) -> int:
        """Return count of pending todos."""
        return sum(1 for t in self._todos.values() if not t.done)

    def clear_done(self) -> int:
        """Remove all done todos. Returns count of removed todos."""
        done_ids = [tid for tid, t in self._todos.items() if t.done]
        for tid in done_ids:
            del self._todos[tid]
        return len(done_ids)
