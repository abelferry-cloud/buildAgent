"""s07: TaskManager - Task dependency graph with topological sorting."""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agent.state.file_store import FileStore


class TaskStatus(Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """A task with optional dependencies on other tasks."""

    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    depends_on: list[str] = field(default_factory=list)
    assigned_to: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "depends_on": self.depends_on,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a task from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data["status"]),
            priority=data.get("priority", 0),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            depends_on=data.get("depends_on", []),
            assigned_to=data.get("assigned_to"),
        )


@dataclass
class TaskCreate:
    """Input for creating a new task."""

    title: str
    description: str = ""
    priority: int = 0
    depends_on: list[str] = field(default_factory=list)
    assigned_to: Optional[str] = None


@dataclass
class TaskUpdate:
    """Input for updating an existing task."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    assigned_to: Optional[str] = None


class TaskManager:
    """
    Manages tasks with dependency tracking and topological sorting.

    Uses file-based persistence via FileStore. Tasks can have
    dependencies on other tasks, and the dependency graph is sorted
    topologically to determine execution order.
    """

    def __init__(self, state_dir: str):
        """Initialize the task manager with a state directory."""
        self._store = FileStore(state_dir)
        self._index: dict[str, str] = {}  # task_id -> stored key

    def create_task(self, task_create: TaskCreate) -> str:
        """
        Create a new task.

        Returns the task ID.
        """
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            title=task_create.title,
            description=task_create.description,
            priority=task_create.priority,
            depends_on=list(task_create.depends_on),
            assigned_to=task_create.assigned_to,
        )

        # Validate dependencies exist
        for dep_id in task.depends_on:
            if not self._store.exists(f"task_{dep_id}"):
                raise ValueError(f"Dependency task '{dep_id}' does not exist")

        # Store the task
        self._store.set(f"task_{task_id}", task.to_dict())
        self._index[task_id] = f"task_{task_id}"

        return task_id

    def get_task(self, task_id: str) -> Task:
        """Get a task by ID."""
        data = self._store.get(f"task_{task_id}")
        if data is None:
            raise KeyError(f"Task '{task_id}' not found")
        return Task.from_dict(data)

    def update_task(self, task_id: str, update: TaskUpdate) -> None:
        """Update an existing task."""
        task = self.get_task(task_id)

        if update.title is not None:
            task.title = update.title
        if update.description is not None:
            task.description = update.description
        if update.status is not None:
            task.status = update.status
        if update.priority is not None:
            task.priority = update.priority
        if update.assigned_to is not None:
            task.assigned_to = update.assigned_to

        task.updated_at = time.time()
        self._store.set(f"task_{task_id}", task.to_dict())

    def list_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """
        List all tasks, optionally filtered by status.

        Returns tasks sorted by priority (highest first) then by created_at.
        """
        tasks = []
        for key in self._store.list_keys():
            if not key.startswith("task_"):
                continue
            data = self._store.get(key)
            if data is None:
                continue
            task = Task.from_dict(data)
            if status is None or task.status == status:
                tasks.append(task)

        tasks.sort(key=lambda t: (-t.priority, t.created_at))
        return tasks

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """
        Add a dependency relationship between tasks.

        task_id depends on depends_on (i.e., depends_on must complete before task_id).
        """
        # Validate both tasks exist
        if not self._store.exists(f"task_{task_id}"):
            raise KeyError(f"Task '{task_id}' not found")
        if not self._store.exists(f"task_{depends_on}"):
            raise KeyError(f"Dependency task '{depends_on}' not found")

        # Prevent circular dependencies
        if self._would_create_cycle(task_id, depends_on):
            raise ValueError(
                f"Adding dependency '{depends_on}' -> '{task_id}' would create a cycle"
            )

        task = self.get_task(task_id)
        if depends_on not in task.depends_on:
            task.depends_on.append(depends_on)
            task.updated_at = time.time()
            self._store.set(f"task_{task_id}", task.to_dict())

    def _would_create_cycle(self, task_id: str, new_dep: str) -> bool:
        """
        Check if adding a dependency would create a cycle.

        Returns True if task_id would eventually depend on itself through new_dep.
        """
        visited: set[str] = set()

        def has_path(current: str) -> bool:
            if current == task_id:
                return True
            if current in visited:
                return False
            visited.add(current)
            try:
                task = self.get_task(current)
                return any(has_path(dep) for dep in task.depends_on)
            except KeyError:
                return False

        return has_path(new_dep)

    def get_ready_tasks(self) -> list[Task]:
        """
        Get tasks that are ready to execute.

        A task is ready when:
        1. It is not completed
        2. All its dependencies are completed
        """
        ready = []
        for task in self.list_tasks():
            if task.status == TaskStatus.COMPLETED:
                continue

            # Check if all dependencies are completed
            deps_completed = True
            for dep_id in task.depends_on:
                try:
                    dep = self.get_task(dep_id)
                    if dep.status != TaskStatus.COMPLETED:
                        deps_completed = False
                        break
                except KeyError:
                    # Dependency task doesn't exist - treat as not completed
                    deps_completed = False
                    break

            if deps_completed:
                ready.append(task)

        return ready

    def get_dependent_tasks(self, task_id: str) -> list[Task]:
        """Get all tasks that depend on the given task."""
        dependent = []
        for task in self.list_tasks():
            if task_id in task.depends_on:
                dependent.append(task)
        return dependent

    def delete_task(self, task_id: str) -> bool:
        """Delete a task. Returns True if it existed."""
        # Remove from any tasks that depend on this one
        for task in self.list_tasks():
            if task_id in task.depends_on:
                task.depends_on.remove(task_id)
                self._store.set(f"task_{task.id}", task.to_dict())

        return self._store.delete(f"task_{task_id}")
