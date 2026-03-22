"""Built-in tools."""

from agent.tools.builtin.bash import BashTool
from agent.tools.builtin.read import ReadTool
from agent.tools.builtin.write import WriteTool
from agent.tools.builtin.glob import GlobTool
from agent.tools.builtin.spawn import SpawnTool

# Todo tools (s03)
from agent.tools.builtin.todo_add import TodoAddTool
from agent.tools.builtin.todo_list import TodoListTool
from agent.tools.builtin.todo_done import TodoDoneTool
from agent.tools.builtin.todo_start import TodoStartTool

# Task tools (s07)
from agent.tools.builtin.task_create import TaskCreateTool
from agent.tools.builtin.task_update import TaskUpdateTool
from agent.tools.builtin.task_list import TaskListTool
from agent.tools.builtin.task_depends import TaskDependsTool

# Background tools (s08)
from agent.tools.builtin.background_run import BackgroundRunTool
from agent.tools.builtin.background_wait import BackgroundWaitTool
from agent.tools.builtin.background_cancel import BackgroundCancelTool

# Team tools (s09)
from agent.tools.builtin.team_send import TeamSendTool
from agent.tools.builtin.team_broadcast import TeamBroadcastTool
from agent.tools.builtin.team_list import TeamListTool
from agent.tools.builtin.team_status import TeamStatusTool

# Board tools (s11)
from agent.tools.builtin.board_post import BoardPostTool
from agent.tools.builtin.board_poll import BoardPollTool
from agent.tools.builtin.board_claim import BoardClaimTool
from agent.tools.builtin.board_complete import BoardCompleteTool

# Worktree tools (s12)
from agent.tools.builtin.worktree_create import WorktreeCreateTool
from agent.tools.builtin.worktree_list import WorktreeListTool
from agent.tools.builtin.worktree_switch import WorktreeSwitchTool
from agent.tools.builtin.worktree_destroy import WorktreeDestroyTool

# Event tools (s12)
from agent.tools.builtin.event_subscribe import EventSubscribeTool
from agent.tools.builtin.event_list import EventListTool

__all__ = [
    "BashTool",
    "ReadTool",
    "WriteTool",
    "GlobTool",
    "SpawnTool",
    # Todo tools
    "TodoAddTool",
    "TodoListTool",
    "TodoDoneTool",
    "TodoStartTool",
    # Task tools
    "TaskCreateTool",
    "TaskUpdateTool",
    "TaskListTool",
    "TaskDependsTool",
    # Background tools
    "BackgroundRunTool",
    "BackgroundWaitTool",
    "BackgroundCancelTool",
    # Team tools
    "TeamSendTool",
    "TeamBroadcastTool",
    "TeamListTool",
    "TeamStatusTool",
    # Board tools
    "BoardPostTool",
    "BoardPollTool",
    "BoardClaimTool",
    "BoardCompleteTool",
    # Worktree tools
    "WorktreeCreateTool",
    "WorktreeListTool",
    "WorktreeSwitchTool",
    "WorktreeDestroyTool",
    # Event tools
    "EventSubscribeTool",
    "EventListTool",
]
