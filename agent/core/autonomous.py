"""s11: Autonomous Governance - Task board and self-governance for agents."""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agent.core.loop import Agent


class TimeoutAction(Enum):
    """Actions to take when a timeout occurs."""

    RETRY = "retry"
    SKIP = "skip"
    ABORT = "abort"
    ESCALATE = "escalate"


class GovernanceIssue(Enum):
    """Types of governance issues that can occur."""

    TASK_TIMEOUT = "task_timeout"
    IDLE_TIMEOUT = "idle_timeout"
    MAX_ITERATIONS = "max_iterations"
    ERROR_RATE = "error_rate"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class GovernorConfig:
    """Configuration for the autonomous governor."""

    max_iterations: int = 100
    max_time_seconds: float = 3600.0  # 1 hour
    idle_timeout_seconds: float = 300.0  # 5 minutes
    self_correct_enabled: bool = True
    retry_limit: int = 3
    escalation_threshold: int = 5


@dataclass
class BoardTask:
    """A task on the task board."""

    id: str
    title: str
    description: str = ""
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    claimed_by: str | None = None
    claimed_at: float | None = None
    completed_at: float | None = None
    result: dict[str, Any] | None = None
    status: str = "pending"  # pending, claimed, completed, failed
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BoardState:
    """Current state of the task board."""

    total_tasks: int = 0
    pending_tasks: int = 0
    claimed_tasks: int = 0
    completed_tasks: int = 0
    workers: list[str] = field(default_factory=list)


class TaskBoard:
    """
    Polling-based task coordination board.

    Provides a file-based task board where agents can post tasks,
    claim them, and mark them complete. Uses polling for coordination.
    """

    def __init__(self, board_file: str):
        """
        Initialize the task board.

        Args:
            board_file: Path to the JSON file for persistence
        """
        self._board_file = board_file
        self._lock_file = f"{board_file}.lock"
        self._tasks: dict[str, BoardTask] = {}
        self._workers: set[str] = set()
        self._load_board()

    def _load_board(self) -> None:
        """Load the board state from file."""
        import os

        if os.path.exists(self._board_file):
            try:
                with open(self._board_file, "r") as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = BoardTask(**task_data)
                        self._tasks[task.id] = task
                    self._workers = set(data.get("workers", []))
            except (json.JSONDecodeError, TypeError):
                # Start with empty board if file is corrupt
                pass

    def _save_board(self) -> None:
        """Save the board state to file."""
        data = {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "created_at": t.created_at,
                    "claimed_by": t.claimed_by,
                    "claimed_at": t.claimed_at,
                    "completed_at": t.completed_at,
                    "result": t.result,
                    "status": t.status,
                    "metadata": t.metadata,
                }
                for t in self._tasks.values()
            ],
            "workers": list(self._workers),
        }
        with open(self._board_file, "w") as f:
            json.dump(data, f, indent=2)

    def post_task(
        self,
        task: BoardTask | None = None,
        title: str = "",
        description: str = "",
        priority: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Post a new task to the board.

        Args:
            task: A pre-created BoardTask (id will be generated if not provided)
            title: Task title (used if task is None)
            description: Task description
            priority: Task priority (higher = more important)
            metadata: Additional metadata

        Returns:
            The task_id of the posted task
        """
        if task is None:
            task = BoardTask(
                id=str(uuid.uuid4())[:8],
                title=title,
                description=description,
                priority=priority,
                metadata=metadata or {},
            )

        self._tasks[task.id] = task
        self._save_board()
        return task.id

    def claim_task(self, task_id: str, worker: str) -> bool:
        """
        Claim a task for a worker.

        Args:
            task_id: The task to claim
            worker: The worker claiming the task

        Returns:
            True if successfully claimed, False otherwise
        """
        task = self._tasks.get(task_id)
        if task is None or task.status != "pending":
            return False

        task.claimed_by = worker
        task.claimed_at = time.time()
        task.status = "claimed"
        self._workers.add(worker)
        self._save_board()
        return True

    def complete_task(self, task_id: str, result: dict[str, Any] | None = None) -> bool:
        """
        Mark a task as complete.

        Args:
            task_id: The task to complete
            result: The result data from task execution

        Returns:
            True if successfully completed, False otherwise
        """
        task = self._tasks.get(task_id)
        if task is None or task.status != "claimed":
            return False

        task.completed_at = time.time()
        task.status = "completed"
        task.result = result
        self._save_board()
        return True

    def fail_task(self, task_id: str, error: str | None = None) -> bool:
        """
        Mark a task as failed.

        Args:
            task_id: The task that failed
            error: Error message if available

        Returns:
            True if successfully marked, False otherwise
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        task.status = "failed"
        task.result = {"error": error} if error else None
        self._save_board()
        return True

    def poll(self, worker: str, timeout: float = 30.0) -> BoardTask | None:
        """
        Poll for an available task.

        Returns the highest priority pending task that isn't claimed.

        Args:
            worker: The worker polling for work
            timeout: How long to wait for a task (not currently implemented)

        Returns:
            A BoardTask if one is available, None otherwise
        """
        pending = [t for t in self._tasks.values() if t.status == "pending"]
        if not pending:
            return None

        # Sort by priority (highest first), then by created_at (oldest first)
        pending.sort(key=lambda t: (-t.priority, t.created_at))

        task = pending[0]
        if self.claim_task(task.id, worker):
            return task
        return None

    def get_board_state(self) -> BoardState:
        """
        Get the current state of the board.

        Returns:
            A BoardState with counts of various task states
        """
        tasks = list(self._tasks.values())
        return BoardState(
            total_tasks=len(tasks),
            pending_tasks=sum(1 for t in tasks if t.status == "pending"),
            claimed_tasks=sum(1 for t in tasks if t.status == "claimed"),
            completed_tasks=sum(1 for t in tasks if t.status == "completed"),
            workers=list(self._workers),
        )

    def get_task(self, task_id: str) -> BoardTask | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: str | None = None,
        worker: str | None = None,
    ) -> list[BoardTask]:
        """
        List tasks, optionally filtered.

        Args:
            status: Filter by status
            worker: Filter by assigned worker

        Returns:
            List of matching tasks
        """
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if worker is not None:
            tasks = [t for t in tasks if t.claimed_by == worker]
        return tasks

    def release_task(self, task_id: str) -> bool:
        """
        Release a claimed task back to pending.

        Args:
            task_id: The task to release

        Returns:
            True if successfully released
        """
        task = self._tasks.get(task_id)
        if task is None or task.status != "claimed":
            return False

        task.claimed_by = None
        task.claimed_at = None
        task.status = "pending"
        self._save_board()
        return True


@dataclass
class TimeoutRecord:
    """Record of a timeout event."""

    task_id: str
    timeout_type: str
    occurred_at: float
    action_taken: TimeoutAction


class AutonomousGovernor:
    """
    Timeout-based self-governance for agents.

    Monitors agent execution and applies governance rules when timeouts
    or other issues occur. Can retry, skip, abort, or escalate tasks.
    """

    def __init__(self, agent: Agent, config: GovernorConfig | None = None):
        """
        Initialize the autonomous governor.

        Args:
            agent: The agent to govern
            config: Governor configuration
        """
        self._agent = agent
        self._config = config or GovernorConfig()
        self._start_time: float = 0.0
        self._iteration_count: int = 0
        self._last_activity_time: float = 0.0
        self._timeout_records: list[TimeoutRecord] = []
        self._retry_counts: dict[str, int] = {}
        self._issue_counts: dict[GovernanceIssue, int] = {}

    def start(self) -> None:
        """Mark the start of governed execution."""
        self._start_time = time.time()
        self._last_activity_time = self._start_time
        self._iteration_count = 0

    def record_activity(self) -> None:
        """Record that activity occurred (resets idle timer)."""
        self._last_activity_time = time.time()

    def record_iteration(self) -> None:
        """Record an iteration completed."""
        self._iteration_count += 1
        self.record_activity()

    def should_continue(self) -> bool:
        """
        Check if execution should continue.

        Returns:
            False if max iterations, max time, or a governance rule stops execution
        """
        # Check iteration limit
        if self._iteration_count >= self._config.max_iterations:
            self._record_issue(GovernanceIssue.MAX_ITERATIONS)
            return False

        # Check time limit
        elapsed = time.time() - self._start_time
        if elapsed >= self._config.max_time_seconds:
            self._record_issue(GovernanceIssue.MAX_ITERATIONS)
            return False

        return True

    def check_timeouts(self) -> list[TimeoutAction]:
        """
        Check for any timeout conditions.

        Returns:
            List of TimeoutActions to take for any timed out tasks
        """
        actions: list[TimeoutAction] = []
        elapsed = time.time() - self._start_time
        idle_time = time.time() - self._last_activity_time

        # Check overall time timeout
        if elapsed >= self._config.max_time_seconds:
            actions.append(TimeoutAction.ABORT)

        # Check idle timeout
        if idle_time >= self._config.idle_timeout_seconds:
            actions.append(TimeoutAction.ESCALATE)
            self._record_issue(GovernanceIssue.IDLE_TIMEOUT)

        return actions

    def self_correct(self, issue: GovernanceIssue) -> None:
        """
        Attempt self-correction for a governance issue.

        Args:
            issue: The issue to correct
        """
        if not self._config.self_correct_enabled:
            return

        self._issue_counts[issue] = self._issue_counts.get(issue, 0) + 1

        # Simple self-correction logic based on issue type
        if issue == GovernanceIssue.ERROR_RATE:
            # Could implement backoff, circuit breaker, etc.
            pass
        elif issue == GovernanceIssue.RESOURCE_EXHAUSTION:
            # Could reduce parallelism, clear caches, etc.
            pass

    def apply_timeout_action(
        self, task_id: str, action: TimeoutAction
    ) -> dict[str, Any]:
        """
        Apply a timeout action to a task.

        Args:
            task_id: The task to apply the action to
            action: The action to take

        Returns:
            Dict with action details
        """
        record = TimeoutRecord(
            task_id=task_id,
            timeout_type="execution",
            occurred_at=time.time(),
            action_taken=action,
        )
        self._timeout_records.append(record)

        if action == TimeoutAction.RETRY:
            retry_count = self._retry_counts.get(task_id, 0)
            if retry_count < self._config.retry_limit:
                self._retry_counts[task_id] = retry_count + 1
                return {"action": "retry", "retry_count": retry_count + 1}
            else:
                return {"action": "aborted", "reason": "retry_limit_exceeded"}

        elif action == TimeoutAction.SKIP:
            return {"action": "skipped"}

        elif action == TimeoutAction.ABORT:
            return {"action": "aborted"}

        elif action == TimeoutAction.ESCALATE:
            return {"action": "escalated", "reason": "requires_attention"}

        return {"action": "unknown"}

    def get_stats(self) -> dict[str, Any]:
        """Get governance statistics."""
        return {
            "iteration_count": self._iteration_count,
            "elapsed_seconds": time.time() - self._start_time,
            "idle_seconds": time.time() - self._last_activity_time,
            "timeout_records": len(self._timeout_records),
            "issue_counts": {k.value: v for k, v in self._issue_counts.items()},
            "retry_counts": dict(self._retry_counts),
        }

    def _record_issue(self, issue: GovernanceIssue) -> None:
        """Record that an issue occurred."""
        self._issue_counts[issue] = self._issue_counts.get(issue, 0) + 1
        if self._config.self_correct_enabled:
            self.self_correct(issue)
