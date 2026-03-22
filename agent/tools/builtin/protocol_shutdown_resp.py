"""Protocol shutdown response tool."""

from agent.core.protocols import ProtocolManager
from agent.tools.base import Tool, ToolResult

_protocol_manager: ProtocolManager | None = None


def set_protocol_manager(pm: ProtocolManager) -> None:
    """Set the global protocol manager instance."""
    global _protocol_manager
    _protocol_manager = pm


class ProtocolShutdownRespTool(Tool):
    """Respond to a shutdown request (approve or reject)."""

    name = "protocol_shutdown_resp"
    description = "Respond to a shutdown request. Use approve=true to allow shutdown, approve=false to reject."

    def execute(self, request_id: str, approve: bool = True) -> ToolResult:
        """Respond to a shutdown request."""
        if _protocol_manager is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="ProtocolManager not initialized",
            )

        if not request_id:
            return ToolResult(
                tool_call_id="",
                output="",
                error="request_id is required",
            )

        # Check if request exists
        request = _protocol_manager.get_shutdown_request(request_id)
        if request is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Shutdown request '{request_id}' not found",
            )

        _protocol_manager.respond_shutdown(request_id, approve)
        status = "approved" if approve else "rejected"
        return ToolResult(
            tool_call_id="",
            output=f"Shutdown request {request_id} {status}",
        )
