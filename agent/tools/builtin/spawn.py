"""Spawn tool - Create a new subagent instance."""

from agent.core.subagent import SubagentManager
from agent.tools.base import Tool, ToolResult


class SpawnTool(Tool):
    """Spawn a new subagent with specified role and tools."""

    name = "spawn"
    description = "Spawn a new subagent with a specific role and set of tools. Returns the subagent ID."

    def __init__(self, subagent_manager: SubagentManager):
        self.subagent_manager = subagent_manager

    def execute(
        self,
        name: str,
        role: str,
        tools: list[str],
    ) -> ToolResult:
        """
        Spawn a new subagent.

        Args:
            name: Human-readable name for the subagent
            role: Description of the subagent's role (e.g., "code reviewer")
            tools: List of tool names to make available to the subagent

        Returns:
            ToolResult with the new subagent_id
        """
        try:
            subagent_id = self.subagent_manager.spawn(
                name=name,
                role=role,
                tools=tools,
            )
            return ToolResult(
                tool_call_id="",
                output=f"Subagent spawned: {name} (ID: {subagent_id}, role: {role})",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
