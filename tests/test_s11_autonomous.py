"""s11: Autonomous Agents - Tests for TaskBoard and AutonomousGovernor."""

import pytest
import time
from agent.core.autonomous import (
    TaskBoard,
    BoardTask,
    BoardState,
    AutonomousGovernor,
    GovernorConfig,
    GovernanceIssue,
    TimeoutAction
)
from agent.core.loop import Agent
from agent.tools.base import Tool, ToolResult


class DummyTool(Tool):
    """Dummy tool for testing."""

    name = "dummy"
    description = "Dummy tool"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(tool_call_id="test", output="done")


class TestBoardTask:
    """Tests for BoardTask dataclass."""

    def test_board_task_creation(self):
        """Test creating a board task."""
        task = BoardTask(
            id="123",
            title="Test task",
            description="A test",
            priority=5
        )
        assert task.id == "123"
        assert task.title == "Test task"
        assert task.status == "pending"
        assert task.claimed_by is None


class TestBoardState:
    """Tests for BoardState dataclass."""

    def test_board_state_defaults(self):
        """Test default board state."""
        state = BoardState()
        assert state.total_tasks == 0
        assert state.pending_tasks == 0
        assert state.claimed_tasks == 0
        assert state.completed_tasks == 0
        assert state.workers == []


class TestTaskBoard:
    """Tests for TaskBoard class."""

    def test_initialization(self, tmp_path):
        """Test TaskBoard initialization."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        assert board is not None

    def test_post_task(self, tmp_path):
        """Test posting a task to the board."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task", description="Description")
        assert task_id is not None
        assert len(task_id) == 8

    def test_post_task_with_priority(self, tmp_path):
        """Test posting a task with priority."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        board.post_task(title="Low priority", priority=1)
        board.post_task(title="High priority", priority=10)

        tasks = board.list_tasks()
        assert len(tasks) == 2

    def test_claim_task(self, tmp_path):
        """Test claiming a task."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task")

        result = board.claim_task(task_id, "worker1")
        assert result is True

        task = board.get_task(task_id)
        assert task.status == "claimed"
        assert task.claimed_by == "worker1"

    def test_claim_task_already_claimed(self, tmp_path):
        """Test claiming an already claimed task fails."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task")

        board.claim_task(task_id, "worker1")
        result = board.claim_task(task_id, "worker2")
        assert result is False

    def test_complete_task(self, tmp_path):
        """Test completing a task."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task")
        board.claim_task(task_id, "worker1")

        result = board.complete_task(task_id, {"result": "success"})
        assert result is True

        task = board.get_task(task_id)
        assert task.status == "completed"

    def test_fail_task(self, tmp_path):
        """Test marking a task as failed."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task")
        board.claim_task(task_id, "worker1")

        result = board.fail_task(task_id, "Connection error")
        assert result is True

        task = board.get_task(task_id)
        assert task.status == "failed"
        assert task.result == {"error": "Connection error"}

    def test_poll_for_task(self, tmp_path):
        """Test polling for available tasks."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        board.post_task(title="Task 1", priority=1)
        board.post_task(title="Task 2", priority=10)

        # Worker polls
        task = board.poll("worker1")
        assert task is not None
        # Should get highest priority task
        assert task.title == "Task 2"
        assert task.status == "claimed"

    def test_poll_when_no_tasks(self, tmp_path):
        """Test polling when no tasks available."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task = board.poll("worker1")
        assert task is None

    def test_get_board_state(self, tmp_path):
        """Test getting board state."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        board.post_task(title="Task 1")
        board.post_task(title="Task 2")
        t1 = board.post_task(title="Task 3")
        board.claim_task(t1, "worker1")

        state = board.get_board_state()
        assert state.total_tasks == 3
        assert state.pending_tasks == 2
        assert state.claimed_tasks == 1

    def test_list_tasks_by_status(self, tmp_path):
        """Test listing tasks by status."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        t1 = board.post_task(title="Pending")
        t2 = board.post_task(title="Claimed")
        board.claim_task(t2, "worker1")

        pending = board.list_tasks(status="pending")
        claimed = board.list_tasks(status="claimed")

        assert len(pending) == 1
        assert len(claimed) == 1

    def test_release_task(self, tmp_path):
        """Test releasing a claimed task."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))
        task_id = board.post_task(title="Test task")
        board.claim_task(task_id, "worker1")

        result = board.release_task(task_id)
        assert result is True

        task = board.get_task(task_id)
        assert task.status == "pending"
        assert task.claimed_by is None


class TestAutonomousGovernor:
    """Tests for AutonomousGovernor class."""

    def test_initialization(self):
        """Test AutonomousGovernor initialization."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        assert governor._agent is agent

    def test_start(self):
        """Test starting governance."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        governor.start()
        assert governor._start_time > 0

    def test_record_activity(self):
        """Test recording activity."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        governor.start()
        time.sleep(0.01)
        governor.record_activity()
        assert governor._last_activity_time >= governor._start_time

    def test_record_iteration(self):
        """Test recording iteration."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        governor.start()
        governor.record_iteration()
        assert governor._iteration_count == 1

    def test_should_continue_within_limits(self):
        """Test should_continue when within limits."""
        agent = Agent(tools=[DummyTool()])
        config = GovernorConfig(max_iterations=100, max_time_seconds=3600)
        governor = AutonomousGovernor(agent, config)
        governor.start()

        assert governor.should_continue() is True

    def test_should_continue_max_iterations(self):
        """Test should_continue when max iterations reached."""
        agent = Agent(tools=[DummyTool()])
        config = GovernorConfig(max_iterations=10)
        governor = AutonomousGovernor(agent, config)
        governor.start()
        governor._iteration_count = 10

        assert governor.should_continue() is False

    def test_apply_timeout_action_retry(self):
        """Test applying retry timeout action."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        result = governor.apply_timeout_action("task1", TimeoutAction.RETRY)
        assert result["action"] == "retry"

    def test_apply_timeout_action_abort(self):
        """Test applying abort timeout action."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        result = governor.apply_timeout_action("task1", TimeoutAction.ABORT)
        assert result["action"] == "aborted"

    def test_get_stats(self):
        """Test getting governance stats."""
        agent = Agent(tools=[DummyTool()])
        governor = AutonomousGovernor(agent)
        governor.start()
        governor.record_iteration()

        stats = governor.get_stats()
        assert "iteration_count" in stats
        assert "elapsed_seconds" in stats
        assert stats["iteration_count"] == 1


class TestAutonomousIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Create 3 tasks on the board, then spawn alice and bob. Watch them auto-claim.
    - Spawn a coder teammate and let it find work from the task board itself
    - Create tasks with dependencies. Watch teammates respect the blocked order.
    """

    def test_multiple_workers_auto_claim(self, tmp_path):
        """Test multiple workers auto-claiming tasks."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))

        # Post 3 tasks
        board.post_task(title="Task 1")
        board.post_task(title="Task 2")
        board.post_task(title="Task 3")

        # Alice polls
        task_alice = board.poll("alice")
        assert task_alice is not None
        assert task_alice.claimed_by == "alice"

        # Bob polls
        task_bob = board.poll("bob")
        assert task_bob is not None
        assert task_bob.claimed_by == "bob"

        # Third task should be available
        tasks = board.list_tasks(status="pending")
        assert len(tasks) == 1

    def test_worker_finds_work_from_board(self, tmp_path):
        """Test worker polling for work."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))

        # Post some tasks
        board.post_task(title="Code review")
        board.post_task(title="Write tests")

        # Worker polls
        task = board.poll("worker1")
        assert task is not None
        assert task.title in ["Code review", "Write tests"]

    def test_priority_based_claiming(self, tmp_path):
        """Test that higher priority tasks are claimed first."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))

        board.post_task(title="Low priority task", priority=1)
        board.post_task(title="High priority task", priority=10)
        board.post_task(title="Medium priority task", priority=5)

        # Worker polls - should get highest priority
        task = board.poll("worker1")
        assert task.title == "High priority task"

    def test_task_completion_flow(self, tmp_path):
        """Test full task completion flow."""
        board = TaskBoard(board_file=str(tmp_path / "board.json"))

        task_id = board.post_task(title="Feature work")
        assert board.get_board_state().pending_tasks == 1

        # Claim
        board.claim_task(task_id, "alice")
        assert board.get_board_state().claimed_tasks == 1

        # Complete
        board.complete_task(task_id, {"completed": True})
        state = board.get_board_state()
        assert state.completed_tasks == 1
        assert state.claimed_tasks == 0
