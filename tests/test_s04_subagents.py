"""s04: Subagents - Tests for SubagentManager and spawn tool."""

import pytest
from agent.core.subagent import SubagentManager, Subagent
from agent.tools.base import Tool, ToolResult


class TestSubagent:
    """Tests for Subagent dataclass."""

    def test_subagent_creation(self):
        """Test creating a subagent."""
        subagent = Subagent(
            id="123",
            name="test-agent",
            role="coder",
            tools=["bash", "read"]
        )
        assert subagent.id == "123"
        assert subagent.name == "test-agent"
        assert subagent.role == "coder"
        assert subagent.tools == ["bash", "read"]
        assert subagent.terminated is False


class TestSubagentManager:
    """Tests for SubagentManager class."""

    def test_subagent_manager_initialization(self):
        """Test SubagentManager initialization."""
        manager = SubagentManager()
        assert manager is not None
        assert manager.subagent_count() == 0

    def test_spawn_subagent(self):
        """Test spawning a new subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(
            name="test-agent",
            role="coder",
            tools=["bash", "read"]
        )
        assert subagent_id is not None
        assert len(subagent_id) == 12  # UUID shortened to 12 chars

    def test_get_subagent(self):
        """Test getting a spawned subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(name="test-agent", role="coder", tools=[])
        subagent = manager.get_subagent(subagent_id)
        assert subagent is not None
        assert subagent.name == "test-agent"

    def test_get_nonexistent_subagent(self):
        """Test getting a subagent that doesn't exist."""
        manager = SubagentManager()
        subagent = manager.get_subagent("nonexistent")
        assert subagent is None

    def test_list_subagents(self):
        """Test listing all subagents."""
        manager = SubagentManager()
        manager.spawn(name="agent1", role="coder", tools=[])
        manager.spawn(name="agent2", role="tester", tools=[])

        subagents = manager.list_subagents()
        assert len(subagents) == 2
        assert manager.subagent_count() == 2

    def test_send_to_subagent(self):
        """Test sending a message to a subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(name="test-agent", role="coder", tools=[])
        manager.send(subagent_id, "Hello, agent!")
        subagent = manager.get_subagent(subagent_id)
        assert len(subagent.messages) == 1
        assert subagent.messages[0].content == "Hello, agent!"

    def test_receive_from_subagent(self):
        """Test receiving messages from a subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(name="test-agent", role="coder", tools=[])

        # Send a message first
        manager.send(subagent_id, "Task: test")

        # Receive messages (returns messages not from parent)
        messages = manager.receive(subagent_id)
        assert isinstance(messages, list)

    def test_terminate_subagent(self):
        """Test terminating a subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(name="test-agent", role="coder", tools=[])
        assert manager.subagent_count() == 1

        manager.terminate(subagent_id)
        assert manager.subagent_count() == 0
        assert manager.get_subagent(subagent_id) is None

    def test_terminate_nonexistent_subagent_fails(self):
        """Test terminating a subagent that doesn't exist."""
        manager = SubagentManager()
        with pytest.raises(ValueError, match="not found"):
            manager.terminate("nonexistent")

    def test_inject_and_get_agent(self):
        """Test injecting and retrieving an agent instance."""
        from agent.core.loop import Agent

        manager = SubagentManager()
        subagent_id = manager.spawn(name="test-agent", role="coder", tools=[])

        agent = Agent(tools=[])
        manager.inject_agent(subagent_id, agent)

        retrieved_agent = manager.get_agent(subagent_id)
        assert retrieved_agent is agent


class TestSubagentIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Use a subtask to find what testing framework this project uses
    - Delegate: read all .py files and summarize what each one does
    - Use a task to create a new module, then verify it from here
    """

    def test_find_testing_framework_subtask(self):
        """Test delegating task to find testing framework."""
        manager = SubagentManager()
        subagent_id = manager.spawn(
            name="researcher",
            role="researcher",
            tools=[]
        )

        manager.send(subagent_id, "What testing framework does this project use? Look at pyproject.toml.")
        messages = manager.receive(subagent_id)

        assert subagent_id is not None
        subagent = manager.get_subagent(subagent_id)
        assert subagent.name == "researcher"

    def test_delegate_file_reading_task(self):
        """Test delegating file reading to subagent."""
        manager = SubagentManager()
        subagent_id = manager.spawn(
            name="reader",
            role="reader",
            tools=["read", "glob"]
        )

        manager.send(
            subagent_id,
            "Task: Read all .py files in the agent/ directory and summarize what each module does."
        )

        subagent = manager.get_subagent(subagent_id)
        assert subagent is not None
        assert subagent.tools == ["read", "glob"]

    def test_delegate_module_creation_task(self):
        """Test delegating module creation task."""
        manager = SubagentManager()
        subagent_id = manager.spawn(
            name="creator",
            role="creator",
            tools=["write", "bash"]
        )

        manager.send(
            subagent_id,
            "Task: Create a new module called 'helper.py' with a helper function."
        )

        subagent = manager.get_subagent(subagent_id)
        assert subagent is not None
        assert "write" in subagent.tools

    def test_multiple_subagents_working_in_parallel(self):
        """Test multiple subagents can work on different tasks."""
        manager = SubagentManager()

        manager.spawn(name="worker1", role="worker", tools=[])
        manager.spawn(name="worker2", role="worker", tools=[])

        manager.send(manager.list_subagents()[0].id, "Task A")
        manager.send(manager.list_subagents()[1].id, "Task B")

        # Both should be active
        assert manager.subagent_count() == 2


class TestSpawnTool:
    """Tests for the spawn tool."""

    def test_spawn_tool_class_exists(self):
        """Test that SpawnTool class exists."""
        from agent.tools.builtin.spawn import SpawnTool
        assert SpawnTool is not None
