"""s12: Worktree Management - Composable worktree lifecycle management."""

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agent.core.loop import Agent


class WorktreeState(Enum):
    """States of a worktree."""

    CREATING = "creating"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


@dataclass
class WorktreeConfig:
    """Configuration for a worktree."""

    branch: str = "main"
    tools: list[str] = field(default_factory=list)
    memory_limit_mb: int = 512
    cpu_limit_percent: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Worktree:
    """
    Represents a worktree with its own isolated working directory.

    A worktree provides an isolated environment for agent execution,
    with its own directory, agent instance, and configuration.
    """

    id: str
    name: str
    path: str
    config: WorktreeConfig
    state: WorktreeState = WorktreeState.CREATING
    created_at: float = field(default_factory=time.time)
    last_active_at: float = field(default_factory=time.time)
    agent: Agent | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert worktree to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "config": {
                "branch": self.config.branch,
                "tools": self.config.tools,
                "memory_limit_mb": self.config.memory_limit_mb,
                "cpu_limit_percent": self.config.cpu_limit_percent,
                "metadata": self.config.metadata,
            },
            "state": self.state.value,
            "created_at": self.created_at,
            "last_active_at": self.last_active_at,
            "metadata": self.metadata,
        }


class WorktreeManager:
    """
    Manages worktree lifecycle and coordination.

    Provides creation, switching, listing, and destruction of worktrees.
    Each worktree is isolated with its own directory and optionally
    its own git worktree for version control isolation.
    """

    def __init__(self, base_dir: str):
        """
        Initialize the worktree manager.

        Args:
            base_dir: Base directory for worktrees
        """
        self._base_dir = base_dir
        self._worktrees: dict[str, Worktree] = {}
        self._state_file = os.path.join(base_dir, ".worktree_state.json")
        self._active_worktree: str | None = None
        self._ensure_base_dir()
        self._load_state()

    def _ensure_base_dir(self) -> None:
        """Ensure the base directory exists."""
        os.makedirs(self._base_dir, exist_ok=True)

    def _load_state(self) -> None:
        """Load worktree state from file."""
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, "r") as f:
                    data = json.load(f)
                    for wt_data in data.get("worktrees", []):
                        config = WorktreeConfig(**wt_data["config"])
                        wt = Worktree(
                            id=wt_data["id"],
                            name=wt_data["name"],
                            path=wt_data["path"],
                            config=config,
                            state=WorktreeState(wt_data["state"]),
                            created_at=wt_data["created_at"],
                            last_active_at=wt_data["last_active_at"],
                            metadata=wt_data.get("metadata", {}),
                        )
                        self._worktrees[wt.name] = wt
                    self._active_worktree = data.get("active_worktree")
            except (json.JSONDecodeError, TypeError, KeyError):
                pass

    def _save_state(self) -> None:
        """Save worktree state to file."""
        data = {
            "worktrees": [wt.to_dict() for wt in self._worktrees.values()],
            "active_worktree": self._active_worktree,
        }
        with open(self._state_file, "w") as f:
            json.dump(data, f, indent=2)

    def create_worktree(
        self,
        name: str,
        config: WorktreeConfig | None = None,
        agent: Agent | None = None,
    ) -> Worktree:
        """
        Create a new worktree.

        Args:
            name: Unique name for the worktree
            config: Worktree configuration
            agent: Optional agent instance for this worktree

        Returns:
            The created Worktree

        Raises:
            ValueError: If a worktree with the given name already exists
        """
        if name in self._worktrees:
            raise ValueError(f"Worktree '{name}' already exists")

        config = config or WorktreeConfig()
        worktree_path = os.path.join(self._base_dir, name)

        # Create the worktree directory
        os.makedirs(worktree_path, exist_ok=True)

        # Create a worktree info file
        info_file = os.path.join(worktree_path, ".worktree_info.json")
        with open(info_file, "w") as f:
            json.dump(
                {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "created_at": time.time(),
                },
                f,
            )

        worktree = Worktree(
            id=str(uuid.uuid4())[:8],
            name=name,
            path=worktree_path,
            config=config,
            state=WorktreeState.ACTIVE,
            agent=agent,
        )

        self._worktrees[name] = worktree
        self._save_state()

        return worktree

    def get_worktree(self, name: str) -> Worktree | None:
        """
        Get a worktree by name.

        Args:
            name: The worktree name

        Returns:
            The Worktree if found, None otherwise
        """
        return self._worktrees.get(name)

    def list_worktrees(self) -> list[Worktree]:
        """
        List all worktrees.

        Returns:
            List of all worktrees
        """
        return list(self._worktrees.values())

    def list_active_worktrees(self) -> list[Worktree]:
        """
        List all active (non-suspended) worktrees.

        Returns:
            List of active worktrees
        """
        return [wt for wt in self._worktrees.values() if wt.state == WorktreeState.ACTIVE]

    def destroy_worktree(self, name: str) -> None:
        """
        Destroy a worktree.

        Args:
            name: The worktree name to destroy

        Raises:
            ValueError: If the worktree doesn't exist
        """
        worktree = self._worktrees.get(name)
        if worktree is None:
            raise ValueError(f"Worktree '{name}' does not exist")

        if self._active_worktree == name:
            self._active_worktree = None

        worktree.state = WorktreeState.DESTROYING
        self._save_state()

        # Remove the worktree directory
        if os.path.exists(worktree.path):
            shutil.rmtree(worktree.path)

        worktree.state = WorktreeState.DESTROYED
        del self._worktrees[name]
        self._save_state()

    def switch_worktree(self, name: str) -> None:
        """
        Switch to a different worktree.

        Args:
            name: The worktree name to switch to

        Raises:
            ValueError: If the worktree doesn't exist or isn't active
        """
        worktree = self._worktrees.get(name)
        if worktree is None:
            raise ValueError(f"Worktree '{name}' does not exist")

        if worktree.state != WorktreeState.ACTIVE:
            raise ValueError(f"Worktree '{name}' is not active")

        # Update last active time of current worktree
        if self._active_worktree and self._active_worktree in self._worktrees:
            current = self._worktrees[self._active_worktree]
            current.last_active_at = time.time()

        self._active_worktree = name
        worktree.last_active_at = time.time()
        self._save_state()

    def suspend_worktree(self, name: str) -> None:
        """
        Suspend a worktree.

        Args:
            name: The worktree name to suspend

        Raises:
            ValueError: If the worktree doesn't exist
        """
        worktree = self._worktrees.get(name)
        if worktree is None:
            raise ValueError(f"Worktree '{name}' does not exist")

        if self._active_worktree == name:
            self._active_worktree = None

        worktree.state = WorktreeState.SUSPENDED
        worktree.last_active_at = time.time()
        self._save_state()

    def resume_worktree(self, name: str) -> None:
        """
        Resume a suspended worktree.

        Args:
            name: The worktree name to resume

        Raises:
            ValueError: If the worktree doesn't exist or isn't suspended
        """
        worktree = self._worktrees.get(name)
        if worktree is None:
            raise ValueError(f"Worktree '{name}' does not exist")

        if worktree.state != WorktreeState.SUSPENDED:
            raise ValueError(f"Worktree '{name}' is not suspended")

        worktree.state = WorktreeState.ACTIVE
        worktree.last_active_at = time.time()
        self._save_state()

    def get_active_worktree(self) -> Worktree | None:
        """
        Get the currently active worktree.

        Returns:
            The active worktree if any
        """
        if self._active_worktree:
            return self._worktrees.get(self._active_worktree)
        return None

    def worktree_exists(self, name: str) -> bool:
        """Check if a worktree exists."""
        return name in self._worktrees

    def get_worktree_stats(self) -> dict[str, Any]:
        """Get statistics about all worktrees."""
        worktrees = list(self._worktrees.values())
        return {
            "total": len(worktrees),
            "active": sum(1 for wt in worktrees if wt.state == WorktreeState.ACTIVE),
            "suspended": sum(1 for wt in worktrees if wt.state == WorktreeState.SUSPENDED),
            "active_worktree": self._active_worktree,
        }


class GitWorktreeManager(WorktreeManager):
    """
    Extended worktree manager with git worktree integration.

    Creates actual git worktrees for complete isolation when
    the project is a git repository.
    """

    def create_worktree(
        self,
        name: str,
        config: WorktreeConfig | None = None,
        agent: Agent | None = None,
    ) -> Worktree:
        """
        Create a new git worktree.

        Args:
            name: Unique name for the worktree
            config: Worktree configuration
            agent: Optional agent instance for this worktree

        Returns:
            The created Worktree
        """
        if name in self._worktrees:
            raise ValueError(f"Worktree '{name}' already exists")

        config = config or WorktreeConfig()
        worktree_path = os.path.join(self._base_dir, name)

        # Check if we're in a git repository
        git_dir = os.path.join(self._base_dir, ".git")
        if os.path.exists(git_dir) or os.path.exists(os.path.join(os.getcwd(), ".git")):
            try:
                # Try to create a real git worktree
                branch_name = f"worktree/{name}"
                subprocess.run(
                    ["git", "worktree", "add", "-b", branch_name, worktree_path, config.branch],
                    capture_output=True,
                    check=False,
                )
            except Exception:
                # Fall back to regular directory creation
                os.makedirs(worktree_path, exist_ok=True)
        else:
            # Not a git repo, just create directory
            os.makedirs(worktree_path, exist_ok=True)

        # Create worktree info file
        info_file = os.path.join(worktree_path, ".worktree_info.json")
        with open(info_file, "w") as f:
            json.dump(
                {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "branch": config.branch,
                    "created_at": time.time(),
                },
                f,
            )

        worktree = Worktree(
            id=str(uuid.uuid4())[:8],
            name=name,
            path=worktree_path,
            config=config,
            state=WorktreeState.ACTIVE,
            agent=agent,
        )

        self._worktrees[name] = worktree
        self._save_state()

        return worktree

    def destroy_worktree(self, name: str) -> None:
        """
        Destroy a git worktree.

        Args:
            name: The worktree name to destroy

        Raises:
            ValueError: If the worktree doesn't exist
        """
        worktree = self._worktrees.get(name)
        if worktree is None:
            raise ValueError(f"Worktree '{name}' does not exist")

        # Try to remove the git worktree
        try:
            subprocess.run(
                ["git", "worktree", "remove", name, "--force"],
                capture_output=True,
                check=False,
            )
        except Exception:
            pass

        super().destroy_worktree(name)
