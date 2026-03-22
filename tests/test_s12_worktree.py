"""s12: Worktree + Task Isolation - Tests for WorktreeManager and GitWorktreeManager."""

import pytest
import os
import time
from agent.core.worktree import (
    WorktreeManager,
    GitWorktreeManager,
    Worktree,
    WorktreeConfig,
    WorktreeState
)
from agent.core.loop import Agent
from agent.tools.base import Tool, ToolResult


class DummyTool(Tool):
    """Dummy tool for testing."""

    name = "dummy"
    description = "Dummy tool"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(tool_call_id="test", output="done")


class TestWorktreeState:
    """Tests for WorktreeState enum."""

    def test_worktree_state_values(self):
        """Test WorktreeState enum values."""
        assert WorktreeState.CREATING.value == "creating"
        assert WorktreeState.ACTIVE.value == "active"
        assert WorktreeState.SUSPENDED.value == "suspended"
        assert WorktreeState.DESTROYING.value == "destroying"
        assert WorktreeState.DESTROYED.value == "destroyed"


class TestWorktreeConfig:
    """Tests for WorktreeConfig dataclass."""

    def test_worktree_config_defaults(self):
        """Test default WorktreeConfig."""
        config = WorktreeConfig()
        assert config.branch == "main"
        assert config.tools == []
        assert config.memory_limit_mb == 512
        assert config.cpu_limit_percent == 100

    def test_worktree_config_custom(self):
        """Test custom WorktreeConfig."""
        config = WorktreeConfig(
            branch="feature-x",
            tools=["bash", "read"],
            memory_limit_mb=1024
        )
        assert config.branch == "feature-x"
        assert len(config.tools) == 2
        assert config.memory_limit_mb == 1024


class TestWorktree:
    """Tests for Worktree dataclass."""

    def test_worktree_creation(self):
        """Test creating a worktree."""
        config = WorktreeConfig()
        wt = Worktree(
            id="123",
            name="test-worktree",
            path="/path/to/worktree",
            config=config
        )
        assert wt.id == "123"
        assert wt.name == "test-worktree"
        assert wt.state == WorktreeState.CREATING

    def test_worktree_to_dict(self):
        """Test worktree serialization."""
        config = WorktreeConfig(branch="main")
        wt = Worktree(
            id="123",
            name="test",
            path="/path",
            config=config,
            state=WorktreeState.ACTIVE
        )
        d = wt.to_dict()
        assert d["id"] == "123"
        assert d["state"] == "active"
        assert d["config"]["branch"] == "main"


class TestWorktreeManager:
    """Tests for WorktreeManager class."""

    def test_initialization(self, tmp_path):
        """Test WorktreeManager initialization."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        assert manager is not None
        assert manager._base_dir == str(tmp_path)

    def test_create_worktree(self, tmp_path):
        """Test creating a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        wt = manager.create_worktree(name="test-worktree")
        assert wt is not None
        assert wt.name == "test-worktree"
        assert wt.state == WorktreeState.ACTIVE
        assert os.path.exists(wt.path)

    def test_create_worktree_with_config(self, tmp_path):
        """Test creating a worktree with config."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        config = WorktreeConfig(branch="feature-x", tools=["bash"])
        wt = manager.create_worktree(name="feature-worktree", config=config)
        assert wt.config.branch == "feature-x"
        assert "bash" in wt.config.tools

    def test_create_duplicate_worktree_fails(self, tmp_path):
        """Test creating a worktree with duplicate name fails."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="test")
        with pytest.raises(ValueError, match="already exists"):
            manager.create_worktree(name="test")

    def test_get_worktree(self, tmp_path):
        """Test getting a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="test")
        wt = manager.get_worktree("test")
        assert wt is not None
        assert wt.name == "test"

    def test_get_nonexistent_worktree(self, tmp_path):
        """Test getting a worktree that doesn't exist."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        wt = manager.get_worktree("nonexistent")
        assert wt is None

    def test_list_worktrees(self, tmp_path):
        """Test listing all worktrees."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.create_worktree(name="wt2")
        worktrees = manager.list_worktrees()
        assert len(worktrees) == 2

    def test_list_active_worktrees(self, tmp_path):
        """Test listing active worktrees."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="active1")
        manager.create_worktree(name="active2")
        manager.create_worktree(name="suspended1")

        # Suspend one
        manager.suspend_worktree("suspended1")

        active = manager.list_active_worktrees()
        assert len(active) == 2
        assert all(wt.state == WorktreeState.ACTIVE for wt in active)

    def test_destroy_worktree(self, tmp_path):
        """Test destroying a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="to-destroy")
        wt_path = manager.get_worktree("to-destroy").path

        manager.destroy_worktree("to-destroy")

        assert manager.get_worktree("to-destroy") is None
        assert not os.path.exists(wt_path)

    def test_destroy_nonexistent_worktree_fails(self, tmp_path):
        """Test destroying a nonexistent worktree fails."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        with pytest.raises(ValueError, match="does not exist"):
            manager.destroy_worktree("nonexistent")

    def test_switch_worktree(self, tmp_path):
        """Test switching to a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.create_worktree(name="wt2")

        manager.switch_worktree("wt1")
        assert manager._active_worktree == "wt1"

        manager.switch_worktree("wt2")
        assert manager._active_worktree == "wt2"

    def test_switch_to_inactive_worktree_fails(self, tmp_path):
        """Test switching to suspended worktree fails."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.suspend_worktree("wt1")

        with pytest.raises(ValueError, match="not active"):
            manager.switch_worktree("wt1")

    def test_suspend_worktree(self, tmp_path):
        """Test suspending a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.switch_worktree("wt1")

        manager.suspend_worktree("wt1")
        wt = manager.get_worktree("wt1")
        assert wt.state == WorktreeState.SUSPENDED
        assert manager._active_worktree is None

    def test_resume_worktree(self, tmp_path):
        """Test resuming a worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.suspend_worktree("wt1")

        manager.resume_worktree("wt1")
        wt = manager.get_worktree("wt1")
        assert wt.state == WorktreeState.ACTIVE

    def test_get_active_worktree(self, tmp_path):
        """Test getting active worktree."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="wt1")
        manager.switch_worktree("wt1")

        active = manager.get_active_worktree()
        assert active is not None
        assert active.name == "wt1"

    def test_worktree_stats(self, tmp_path):
        """Test getting worktree statistics."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        manager.create_worktree(name="active1")
        manager.create_worktree(name="active2")
        manager.create_worktree(name="suspended1")
        manager.suspend_worktree("suspended1")

        stats = manager.get_worktree_stats()
        assert stats["total"] == 3
        assert stats["active"] == 2
        assert stats["suspended"] == 1


class TestGitWorktreeManager:
    """Tests for GitWorktreeManager class."""

    def test_initialization(self, tmp_path):
        """Test GitWorktreeManager initialization."""
        manager = GitWorktreeManager(base_dir=str(tmp_path))
        assert manager is not None


class TestWorktreeIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Create tasks for backend auth and frontend login page, then list tasks.
    - Create worktree "auth-refactor" for task 1, then bind task 2 to a new worktree "ui-login".
    - Run "git status --short" in worktree "auth-refactor".
    - Keep worktree "ui-login", then list worktrees and inspect events.
    - Remove worktree "auth-refactor" with complete_task=true, then list tasks/worktrees/events.
    """

    def test_create_worktrees_for_tasks(self, tmp_path):
        """Test creating worktrees for different tasks."""
        manager = WorktreeManager(base_dir=str(tmp_path))

        # Create worktree for auth refactor
        auth_wt = manager.create_worktree(name="auth-refactor")
        assert auth_wt.name == "auth-refactor"

        # Create worktree for UI login
        ui_wt = manager.create_worktree(name="ui-login")
        assert ui_wt.name == "ui-login"

        # List all worktrees
        worktrees = manager.list_worktrees()
        assert len(worktrees) == 2

    def test_switch_between_worktrees(self, tmp_path):
        """Test switching between worktrees."""
        manager = WorktreeManager(base_dir=str(tmp_path))

        manager.create_worktree(name="auth-refactor")
        manager.create_worktree(name="ui-login")

        # Switch to auth-refactor
        manager.switch_worktree("auth-refactor")
        assert manager.get_active_worktree().name == "auth-refactor"

        # Switch to ui-login
        manager.switch_worktree("ui-login")
        assert manager.get_active_worktree().name == "ui-login"

    def test_worktree_with_agent(self, tmp_path):
        """Test worktree with bound agent."""
        manager = WorktreeManager(base_dir=str(tmp_path))
        agent = Agent(tools=[DummyTool()])

        wt = manager.create_worktree(name="test-worktree", agent=agent)
        assert wt.agent is agent

    def test_destroy_and_verify_cleanup(self, tmp_path):
        """Test that destroying worktree cleans up properly."""
        manager = WorktreeManager(base_dir=str(tmp_path))

        # Create worktrees
        manager.create_worktree(name="auth-refactor")
        manager.create_worktree(name="ui-login")

        # Verify both exist
        assert manager.worktree_exists("auth-refactor")
        assert manager.worktree_exists("ui-login")

        # Destroy one
        manager.destroy_worktree("auth-refactor")

        # Verify only one remains
        assert not manager.worktree_exists("auth-refactor")
        assert manager.worktree_exists("ui-login")

    def test_worktree_persistence(self, tmp_path):
        """Test worktree state persists across manager instances."""
        # Create and switch
        manager1 = WorktreeManager(base_dir=str(tmp_path))
        manager1.create_worktree(name="persistent-wt")
        manager1.switch_worktree("persistent-wt")

        # Create new manager instance
        manager2 = WorktreeManager(base_dir=str(tmp_path))

        # Should still have the worktree
        assert manager2.worktree_exists("persistent-wt")
        assert manager2.get_active_worktree().name == "persistent-wt"
