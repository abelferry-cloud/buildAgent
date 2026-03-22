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
    def from_directory(cls, tool_dir: str, subagent_manager=None) -> "DispatchMap":
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

        # Register spawn tool (s04: Subagents)
        if subagent_manager:
            from agent.tools.builtin.spawn import SpawnTool
            dispatch.register(SpawnTool(subagent_manager))

        return dispatch
