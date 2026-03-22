"""Protocol shutdown request tool."""

from agent.core.protocols import ProtocolManager
from agent.tools.base import Tool, ToolResult

_protocol_manager: ProtocolManager | None = None


def set_protocol_manager(pm: ProtocolManager) -> None:
    """Set the global protocol manager instance."""
    global _protocol_manager
    _protocol_manager = pm


class ProtocolShutdownReqTool(Tool):
    """Request a teammate to shut down."""

    name = "protocol_shutdown_req"
    description = "Request a teammate to shut down. Returns a request_id to track the response."

    def execute(self, to: str, reason: str = "") -> ToolResult:
        """Send a shutdown request to a teammate."""
        if _protocol_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="ProtocolManager not initialized",
            )

        if not to:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Target 'to' is required",
            )

        request_id = _protocol_manager.create_shutdown_request(to, reason or "Shutdown requested")
        return ToolResult(
            tool_call_id="",
            output=f"Shutdown request sent to {to}: {request_id}",
        )
