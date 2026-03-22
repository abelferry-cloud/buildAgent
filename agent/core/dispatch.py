"""s02: Tool Dispatch Map - Dynamic tool registration and routing."""

from typing import Any

from agent.tools.base import Tool, ToolResult


class DispatchMap:
    """
    A map from tool names to tool instances for dispatch.

    The loop stays the same; new tools register into the dispatch map.
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by name."""
        self._tools[tool.name] = tool

    def dispatch(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        """Dispatch a tool call by name with parameters."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                tool_call_id=params.get("_tool_call_id", ""),
                output="",
                error=f"Tool '{tool_name}' not found. Available tools: {', '.join(self._tools.keys())}",
            )

        try:
            return tool.execute(**params)
        except Exception as e:
            return ToolResult(
                tool_call_id=params.get("_tool_call_id", ""),
                output="",
                error=str(e),
            )

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_tool_names(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    @classmethod
    def from_directory(cls, tool_dir: str, subagent_manager=None, skill_loader=None) -> "DispatchMap":
        """Create a DispatchMap by loading tools from a directory."""
        dispatch = cls()

        # Import and register built-in tools
        from agent.tools.builtin.bash import BashTool
        from agent.tools.builtin.read import ReadTool
        from agent.tools.builtin.write import WriteTool
        from agent.tools.builtin.glob import GlobTool

        dispatch.register(BashTool())
        dispatch.register(ReadTool())
        dispatch.register(WriteTool())
        dispatch.register(GlobTool())

        # Import and register todo tools (s03)
        from agent.tools.builtin.todo_add import TodoAddTool
        from agent.tools.builtin.todo_list import TodoListTool
        from agent.tools.builtin.todo_done import TodoDoneTool
        from agent.tools.builtin.todo_start import TodoStartTool

        dispatch.register(TodoAddTool())
        dispatch.register(TodoListTool())
        dispatch.register(TodoDoneTool())
        dispatch.register(TodoStartTool())

        # Import and register task tools (s07: Tasks)
        from agent.tools.builtin.task_create import TaskCreateTool
        from agent.tools.builtin.task_update import TaskUpdateTool
        from agent.tools.builtin.task_list import TaskListTool
        from agent.tools.builtin.task_depends import TaskDependsTool

        dispatch.register(TaskCreateTool())
        dispatch.register(TaskUpdateTool())
        dispatch.register(TaskListTool())
        dispatch.register(TaskDependsTool())

        # Import and register background tools (s08: Background Tasks)
        from agent.tools.builtin.background_run import BackgroundRunTool
        from agent.tools.builtin.background_wait import BackgroundWaitTool
        from agent.tools.builtin.background_cancel import BackgroundCancelTool

        dispatch.register(BackgroundRunTool())
        dispatch.register(BackgroundWaitTool())
        dispatch.register(BackgroundCancelTool())

        # Import and register team tools (s09: Agent Teams)
        from agent.tools.builtin.team_send import TeamSendTool
        from agent.tools.builtin.team_broadcast import TeamBroadcastTool
        from agent.tools.builtin.team_list import TeamListTool
        from agent.tools.builtin.team_status import TeamStatusTool

        dispatch.register(TeamSendTool())
        dispatch.register(TeamBroadcastTool())
        dispatch.register(TeamListTool())
        dispatch.register(TeamStatusTool())

        # Import and register protocol tools (s10: Team Protocols)
        from agent.tools.builtin.protocol_shutdown_req import ProtocolShutdownReqTool
        from agent.tools.builtin.protocol_shutdown_resp import ProtocolShutdownRespTool
        from agent.tools.builtin.protocol_plan_req import ProtocolPlanReqTool
        from agent.tools.builtin.protocol_plan_resp import ProtocolPlanRespTool

        dispatch.register(ProtocolShutdownReqTool())
        dispatch.register(ProtocolShutdownRespTool())
        dispatch.register(ProtocolPlanReqTool())
        dispatch.register(ProtocolPlanRespTool())

        # Import and register board tools (s11: Autonomous Agents)
        from agent.tools.builtin.board_post import BoardPostTool
        from agent.tools.builtin.board_poll import BoardPollTool
        from agent.tools.builtin.board_claim import BoardClaimTool
        from agent.tools.builtin.board_complete import BoardCompleteTool

        dispatch.register(BoardPostTool())
        dispatch.register(BoardPollTool())
        dispatch.register(BoardClaimTool())
        dispatch.register(BoardCompleteTool())

        # Import and register worktree tools (s12: Worktree + Isolation)
        from agent.tools.builtin.worktree_create import WorktreeCreateTool
        from agent.tools.builtin.worktree_list import WorktreeListTool
        from agent.tools.builtin.worktree_switch import WorktreeSwitchTool
        from agent.tools.builtin.worktree_destroy import WorktreeDestroyTool

        dispatch.register(WorktreeCreateTool())
        dispatch.register(WorktreeListTool())
        dispatch.register(WorktreeSwitchTool())
        dispatch.register(WorktreeDestroyTool())

        # Register spawn tool (s04: Subagents)
        if subagent_manager:
            from agent.tools.builtin.spawn import SpawnTool
            dispatch.register(SpawnTool(subagent_manager))

        # Register load_skill tool (s05: Skills)
        if skill_loader:
            from agent.tools.builtin.load_skill import LoadSkillTool
            dispatch.register(LoadSkillTool(skill_loader))

        return dispatch
