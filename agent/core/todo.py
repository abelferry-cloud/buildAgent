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
    in_progress: bool = False


class TodoManager:
    """
    Manages todo items with nag reminders.

    An agent without a plan drifts; list the steps first, then execute.
    """

    NAG_THRESHOLD = 3  # Nag after 3 rounds without todo tool usage

    def __init__(self):
        self._todos: dict[str, Todo] = {}
        self._rounds_since_todo: int = 0

    def add(self, task: str, priority: int = 0) -> str:
        """Add a new todo item. Returns the todo_id."""
        todo_id = str(uuid.uuid4())[:8]
        todo = Todo(id=todo_id, task=task, priority=priority)
        self._todos[todo_id] = todo
        self._rounds_since_todo = 0  # Reset nag counter on todo action
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
        todo.in_progress = False  # Clear in_progress when done
        self._rounds_since_todo = 0  # Reset nag counter on todo action
        return True

    def start(self, todo_id: str) -> bool:
        """Mark a todo as in_progress. Only one todo can be in_progress at a time."""
        todo = self._todos.get(todo_id)
        if not todo:
            return False

        # Clear any existing in_progress todo
        for t in self._todos.values():
            if t.in_progress and t.id != todo_id:
                t.in_progress = False

        todo.in_progress = True
        self._rounds_since_todo = 0  # Reset nag counter on todo action
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

    def increment_round(self) -> None:
        """Increment the round counter (called when no todo tool was used)."""
        self._rounds_since_todo += 1

    def should_nag(self) -> bool:
        """Check if nag reminder should be injected."""
        return self._rounds_since_todo >= self.NAG_THRESHOLD

    def get_nag_message(self) -> str:
        """Get the nag reminder message."""
        return "<reminder>Update your todos.</reminder>"
