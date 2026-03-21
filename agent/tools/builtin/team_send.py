"""TeamSend tool - Send a message to a teammate."""

from agent.tools.base import Tool, ToolResult
from agent.core.teams import TeammateManager
from agent.state.mailbox import ProtocolType

_teammate_manager: TeammateManager | None = None


def set_teammate_manager(tm: TeammateManager) -> None:
    """Set the global teammate manager instance."""
    global _teammate_manager
    _teammate_manager = tm


class TeamSendTool(Tool):
    """Send a message to a teammate."""

    name = "team_send"
    description = "Send a message to a specific teammate."

    def execute(self, to: str, message: str, protocol: str = "direct") -> ToolResult:
        """Send a message to a teammate."""
        if _teammate_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="TeammateManager not initialized",
            )

        try:
            protocol_type = ProtocolType(protocol)
        except ValueError:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Invalid protocol: {protocol}. Valid values: direct, broadcast, request, response",
            )

        try:
            message_id = _teammate_manager.send_message(to, message, protocol_type)
            return ToolResult(
                tool_call_id="",
                output=f"Sent message to {to}: {message_id}",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                output="",
                error=str(e),
            )
