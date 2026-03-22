"""s07: Tasks - Tests for TaskManager with dependency graph and topological sorting."""

import pytest
from agent.core.tasks import TaskManager, Task, TaskStatus, TaskCreate, TaskUpdate


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_task_status_values(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.BLOCKED.value == "blocked"


class TestTask:
    """Tests for Task dataclass."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(id="123", title="Test task")
        assert task.id == "123"
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.description == ""
        assert task.priority == 0
        assert task.depends_on == []

    def test_task_to_dict(self):
        """Test task serialization to dict."""
        task = Task(id="123", title="Test task", priority=5)
        d = task.to_dict()
        assert d["id"] == "123"
        assert d["title"] == "Test task"
        assert d["priority"] == 5
        assert d["status"] == "pending"

    def test_task_from_dict(self):
        """Test task deserialization from dict."""
        data = {
            "id": "123",
            "title": "Test task",
            "description": "A test",
            "status": "completed",
            "priority": 3,
            "created_at": 1234567890.0,
            "updated_at": 1234567890.0,
            "depends_on": [],
            "assigned_to": None
        }
        task = Task.from_dict(data)
        assert task.id == "123"
        assert task.title == "Test task"
        assert task.status == TaskStatus.COMPLETED


class TestTaskManager:
    """Tests for TaskManager class."""

    def test_task_manager_initialization(self, tmp_path):
        """Test TaskManager initialization."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        assert manager is not None

    def test_create_task(self, tmp_path):
        """Test creating a task."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="Test task"))
        assert task_id is not None
        assert len(task_id) == 8  # UUID shortened to 8 chars

    def test_create_task_with_priority(self, tmp_path):
        """Test creating a task with priority."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="High priority", priority=10))
        task = manager.get_task(task_id)
        assert task.priority == 10

    def test_create_task_with_dependency(self, tmp_path):
        """Test creating a task with dependency on another task."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        task2_id = manager.create_task(
            TaskCreate(title="Task 2", depends_on=[task1_id])
        )

        task2 = manager.get_task(task2_id)
        assert task1_id in task2.depends_on

    def test_create_task_invalid_dependency(self, tmp_path):
        """Test creating task with non-existent dependency."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        with pytest.raises(ValueError, match="does not exist"):
            manager.create_task(TaskCreate(title="Task", depends_on=["invalid"]))

    def test_get_task(self, tmp_path):
        """Test getting a task by ID."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="Test task"))
        task = manager.get_task(task_id)
        assert task.title == "Test task"

    def test_get_nonexistent_task(self, tmp_path):
        """Test getting a task that doesn't exist."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        with pytest.raises(KeyError, match="not found"):
            manager.get_task("nonexistent")

    def test_update_task(self, tmp_path):
        """Test updating a task."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="Original"))
        manager.update_task(task_id, TaskUpdate(title="Updated"))
        task = manager.get_task(task_id)
        assert task.title == "Updated"

    def test_update_task_status(self, tmp_path):
        """Test updating task status."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="Test"))
        manager.update_task(task_id, TaskUpdate(status=TaskStatus.IN_PROGRESS))
        task = manager.get_task(task_id)
        assert task.status == TaskStatus.IN_PROGRESS

    def test_list_tasks(self, tmp_path):
        """Test listing all tasks."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        manager.create_task(TaskCreate(title="Task 1"))
        manager.create_task(TaskCreate(title="Task 2"))
        tasks = manager.list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_by_status(self, tmp_path):
        """Test listing tasks filtered by status."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        manager.create_task(TaskCreate(title="Task 2"))
        manager.update_task(task1_id, TaskUpdate(status=TaskStatus.COMPLETED))

        pending = manager.list_tasks(status=TaskStatus.PENDING)
        completed = manager.list_tasks(status=TaskStatus.COMPLETED)
        assert len(pending) == 1
        assert len(completed) == 1

    def test_add_dependency(self, tmp_path):
        """Test adding a dependency between tasks."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        task2_id = manager.create_task(TaskCreate(title="Task 2"))

        manager.add_dependency(task2_id, task1_id)
        task2 = manager.get_task(task2_id)
        assert task1_id in task2.depends_on

    def test_add_dependency_circular_detection(self, tmp_path):
        """Test that circular dependencies are detected."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        task2_id = manager.create_task(TaskCreate(title="Task 2", depends_on=[task1_id]))

        # Try to make task1 depend on task2 (would create cycle)
        with pytest.raises(ValueError, match="cycle"):
            manager.add_dependency(task1_id, task2_id)

    def test_get_ready_tasks(self, tmp_path):
        """Test getting tasks that are ready to execute."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        task2_id = manager.create_task(TaskCreate(title="Task 2", depends_on=[task1_id]))

        # Task 1 should be ready
        ready = manager.get_ready_tasks()
        assert any(t.id == task1_id for t in ready)

        # Task 2 should not be ready (depends on incomplete task)
        assert not any(t.id == task2_id for t in ready)

    def test_get_ready_tasks_after_completion(self, tmp_path):
        """Test that blocked tasks become ready after dependencies complete."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task1_id = manager.create_task(TaskCreate(title="Task 1"))
        task2_id = manager.create_task(TaskCreate(title="Task 2", depends_on=[task1_id]))

        # Complete task 1
        manager.update_task(task1_id, TaskUpdate(status=TaskStatus.COMPLETED))

        # Now task 2 should be ready
        ready = manager.get_ready_tasks()
        assert any(t.id == task2_id for t in ready)

    def test_delete_task(self, tmp_path):
        """Test deleting a task."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))
        task_id = manager.create_task(TaskCreate(title="To delete"))
        result = manager.delete_task(task_id)
        assert result is True

        with pytest.raises(KeyError):
            manager.get_task(task_id)


class TestTaskManagerIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Create 3 tasks: "Setup project", "Write code", "Write tests". Make them depend on each other in order.
    - List all tasks and show the dependency graph
    - Complete task 1 and then list tasks to see task 2 unblocked
    - Create a task board for refactoring: parse -> transform -> emit -> test, where transform and emit can run in parallel after parse
    """

    def test_sequential_task_chain(self, tmp_path):
        """Test creating sequential dependent tasks."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))

        # Create chain: Setup -> Write code -> Write tests
        setup_id = manager.create_task(TaskCreate(title="Setup project"))
        code_id = manager.create_task(
            TaskCreate(title="Write code", depends_on=[setup_id])
        )
        test_id = manager.create_task(
            TaskCreate(title="Write tests", depends_on=[code_id])
        )

        # Verify dependencies
        assert manager.get_task(code_id).depends_on == [setup_id]
        assert manager.get_task(test_id).depends_on == [code_id]

    def test_task_execution_flow(self, tmp_path):
        """Test task execution flow: complete one, next becomes ready."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))

        task1_id = manager.create_task(TaskCreate(title="Setup project"))
        task2_id = manager.create_task(
            TaskCreate(title="Write code", depends_on=[task1_id])
        )
        task3_id = manager.create_task(
            TaskCreate(title="Write tests", depends_on=[task2_id])
        )

        # Initially only task1 is ready
        ready = manager.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == task1_id

        # Complete task 1
        manager.update_task(task1_id, TaskUpdate(status=TaskStatus.COMPLETED))

        # Now task2 should be ready
        ready = manager.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == task2_id

    def test_parallel_tasks_after_dependency(self, tmp_path):
        """Test parallel tasks that depend on the same predecessor."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))

        # Parse must complete first
        parse_id = manager.create_task(TaskCreate(title="Parse"))

        # Transform and Emit can run in parallel after parse
        transform_id = manager.create_task(
            TaskCreate(title="Transform", depends_on=[parse_id])
        )
        emit_id = manager.create_task(
            TaskCreate(title="Emit", depends_on=[parse_id])
        )

        # Test can run after both transform and emit
        test_id = manager.create_task(
            TaskCreate(title="Test", depends_on=[transform_id, emit_id])
        )

        # Complete parse
        manager.update_task(parse_id, TaskUpdate(status=TaskStatus.COMPLETED))

        # Transform and emit should now be ready
        ready = manager.get_ready_tasks()
        ready_ids = [t.id for t in ready]
        assert transform_id in ready_ids
        assert emit_id in ready_ids
        assert test_id not in ready_ids  # Still blocked

    def test_dependency_graph_listing(self, tmp_path):
        """Test listing tasks shows dependency relationships."""
        manager = TaskManager(state_dir=str(tmp_path / "tasks"))

        task1_id = manager.create_task(TaskCreate(title="Setup"))
        task2_id = manager.create_task(
            TaskCreate(title="Code", depends_on=[task1_id])
        )

        tasks = manager.list_tasks()
        code_task = next(t for t in tasks if t.title == "Code")
        assert code_task.depends_on == [task1_id]
