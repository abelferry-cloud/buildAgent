"""Core agent components."""

from agent.core.loop import Agent, Message, AgentResponse
from agent.core.dispatch import DispatchMap
from agent.core.todo import TodoManager, Todo
from agent.core.subagent import SubagentManager, Subagent
from agent.core.skills import Skill, SkillLoader
from agent.core.compact import CompressionManager, CompressionConfig
from agent.core.autonomous import (
    AutonomousGovernor,
    TaskBoard,
    BoardTask,
    BoardState,
    GovernorConfig,
    TimeoutAction,
    GovernanceIssue,
    TimeoutRecord,
)
from agent.core.worktree import (
    WorktreeManager,
    Worktree,
    WorktreeConfig,
    WorktreeState,
    GitWorktreeManager,
)

__all__ = [
    "Agent",
    "Message",
    "AgentResponse",
    "DispatchMap",
    "TodoManager",
    "Todo",
    "SubagentManager",
    "Subagent",
    "Skill",
    "SkillLoader",
    "CompressionManager",
    "CompressionConfig",
    # Autonomous governance
    "AutonomousGovernor",
    "TaskBoard",
    "BoardTask",
    "BoardState",
    "GovernorConfig",
    "TimeoutAction",
    "GovernanceIssue",
    "TimeoutRecord",
    # Worktree
    "WorktreeManager",
    "Worktree",
    "WorktreeConfig",
    "WorktreeState",
    "GitWorktreeManager",
]
