"""s03: TodoWrite - Tests for TodoManager with nag reminder."""

import pytest
from agent.core.todo import TodoManager, Todo


class TestTodo:
    """Tests for Todo dataclass."""

    def test_todo_creation(self):
        """Test creating a todo item."""
        todo = Todo(id="123", task="Write tests")
        assert todo.id == "123"
        assert todo.task == "Write tests"
        assert todo.done is False
        assert todo.in_progress is False
        assert todo.priority == 0

    def test_todo_with_priority(self):
        """Test creating a todo with priority."""
        todo = Todo(id="123", task="Important task", priority=5)
        assert todo.priority == 5


class TestTodoManager:
    """Tests for TodoManager class."""

    def test_todo_manager_initialization(self):
        """Test TodoManager initialization."""
        manager = TodoManager()
        assert manager.pending_count() == 0
        assert manager.should_nag() is False

    def test_add_todo(self):
        """Test adding a todo."""
        manager = TodoManager()
        todo_id = manager.add("Write unit tests")
        assert todo_id is not None
        assert manager.pending_count() == 1

    def test_add_todo_with_priority(self):
        """Test adding a todo with priority."""
        manager = TodoManager()
        manager.add("Low priority task", priority=1)
        manager.add("High priority task", priority=10)
        manager.add("Medium priority task", priority=5)

        todos = manager.list()
        # Should be sorted by priority (highest first)
        assert todos[0].task == "High priority task"
        assert todos[1].task == "Medium priority task"
        assert todos[2].task == "Low priority task"

    def test_list_todos(self):
        """Test listing todos."""
        manager = TodoManager()
        manager.add("Task 1")
        manager.add("Task 2")
        manager.add("Task 3")

        todos = manager.list()
        assert len(todos) == 3

    def test_list_todos_excludes_done(self):
        """Test that list() excludes completed todos."""
        manager = TodoManager()
        todo_id = manager.add("Task to complete")
        manager.add("Another task")
        manager.done(todo_id)

        todos = manager.list()
        assert len(todos) == 1
        assert todos[0].task == "Another task"

    def test_get_todo(self):
        """Test getting a specific todo."""
        manager = TodoManager()
        todo_id = manager.add("Test task")
        todo = manager.get(todo_id)
        assert todo is not None
        assert todo.task == "Test task"

    def test_get_nonexistent_todo(self):
        """Test getting a todo that doesn't exist."""
        manager = TodoManager()
        todo = manager.get("nonexistent")
        assert todo is None

    def test_done_todo(self):
        """Test marking a todo as done."""
        manager = TodoManager()
        todo_id = manager.add("Task to complete")
        result = manager.done(todo_id)
        assert result is True
        assert manager.get(todo_id).done is True
        assert manager.get(todo_id).done_at is not None

    def test_done_nonexistent_todo(self):
        """Test marking a nonexistent todo as done."""
        manager = TodoManager()
        result = manager.done("nonexistent")
        assert result is False

    def test_start_todo(self):
        """Test starting a todo (marking in_progress)."""
        manager = TodoManager()
        todo_id = manager.add("Task to start")
        result = manager.start(todo_id)
        assert result is True
        assert manager.get(todo_id).in_progress is True

    def test_start_todo_clears_other_in_progress(self):
        """Test that starting a todo clears other in_progress todos."""
        manager = TodoManager()
        todo_id1 = manager.add("Task 1")
        todo_id2 = manager.add("Task 2")
        manager.start(todo_id1)
        manager.start(todo_id2)

        assert manager.get(todo_id1).in_progress is False
        assert manager.get(todo_id2).in_progress is True

    def test_start_nonexistent_todo(self):
        """Test starting a nonexistent todo."""
        manager = TodoManager()
        result = manager.start("nonexistent")
        assert result is False

    def test_clear_done(self):
        """Test clearing completed todos."""
        manager = TodoManager()
        todo_id1 = manager.add("Task 1")
        todo_id2 = manager.add("Task 2")
        manager.done(todo_id1)

        count = manager.clear_done()
        assert count == 1
        assert manager.pending_count() == 1


class TestNagReminder:
    """Tests for the nag reminder mechanism."""

    def test_nag_threshold(self):
        """Test that NAG_THRESHOLD is set correctly."""
        manager = TodoManager()
        assert manager.NAG_THRESHOLD == 3

    def test_should_nag_initially_false(self):
        """Test that should_nag is initially False."""
        manager = TodoManager()
        assert manager.should_nag() is False

    def test_should_nag_after_threshold(self):
        """Test should_nag after reaching threshold."""
        manager = TodoManager()
        # Add a todo so we have something to track
        manager.add("Test task")

        # Increment round without using todo tool
        manager.increment_round()
        assert manager.should_nag() is False
        manager.increment_round()
        assert manager.should_nag() is False
        manager.increment_round()
        assert manager.should_nag() is True

    def test_add_resets_nag_counter(self):
        """Test that adding a todo resets the nag counter."""
        manager = TodoManager()
        manager.increment_round()
        manager.increment_round()
        manager.increment_round()  # Now at threshold
        assert manager.should_nag() is True

        manager.add("New task")  # This should reset
        assert manager.should_nag() is False

    def test_done_resets_nag_counter(self):
        """Test that completing a todo resets the nag counter."""
        manager = TodoManager()
        todo_id = manager.add("Task")
        manager.increment_round()
        manager.increment_round()
        manager.increment_round()

        manager.done(todo_id)
        assert manager.should_nag() is False

    def test_start_resets_nag_counter(self):
        """Test that starting a todo resets the nag counter."""
        manager = TodoManager()
        todo_id = manager.add("Task")
        manager.increment_round()
        manager.increment_round()
        manager.increment_round()

        manager.start(todo_id)
        assert manager.should_nag() is False

    def test_get_nag_message(self):
        """Test getting the nag message."""
        manager = TodoManager()
        msg = manager.get_nag_message()
        assert "<reminder>" in msg
        assert "todos" in msg.lower()


class TestTodoWriteIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Refactor the file hello.py: add type hints, docstrings, and a main guard
    - Create a Python package with __init__.py, utils.py, and tests/test_utils.py
    - Review all Python files and fix any style issues
    """

    def test_todo_for_refactoring_task(self):
        """Test tracking a refactoring task."""
        manager = TodoManager()
        refactor_id = manager.add("Refactor hello.py: add type hints, docstrings, and main guard")
        assert manager.pending_count() == 1

        manager.start(refactor_id)
        assert manager.get(refactor_id).in_progress is True

    def test_todo_for_package_creation(self):
        """Test tracking package creation tasks."""
        manager = TodoManager()
        # Create tasks for package structure
        init_id = manager.add("Create package __init__.py", priority=2)
        utils_id = manager.add("Create utils.py with utility functions", priority=3)
        test_id = manager.add("Create tests/test_utils.py", priority=1)

        todos = manager.list()
        # utils.py has highest priority
        assert todos[0].task == "Create utils.py with utility functions"

    def test_todo_for_code_review(self):
        """Test tracking code review tasks."""
        manager = TodoManager()
        manager.add("Review all Python files")
        manager.add("Fix style issues")

        todos = manager.list()
        assert len(todos) == 2

        # Complete the review task
        review_todo = next(t for t in todos if "Review" in t.task)
        manager.done(review_todo.id)

        assert manager.pending_count() == 1

    def test_nag_after_no_todo_usage(self):
        """Test nag reminder after not using todo tools for multiple rounds."""
        manager = TodoManager()
        manager.add("Initial task")

        # Simulate multiple rounds without todo usage
        for _ in range(3):
            manager.increment_round()

        assert manager.should_nag() is True
        assert manager.get_nag_message() == "<reminder>Update your todos.</reminder>"
