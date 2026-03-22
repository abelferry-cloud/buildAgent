"""Protocol plan approval response tool."""

from agent.core.protocols import ProtocolManager
from agent.tools.base import Tool, ToolResult

_protocol_manager: ProtocolManager | None = None


def set_protocol_manager(pm: ProtocolManager) -> None:
    """Set the global protocol manager instance."""
    global _protocol_manager
    _protocol_manager = pm


class ProtocolPlanRespTool(Tool):
    """Respond to a plan approval request (approve or reject)."""

    name = "protocol_plan_resp"
    description = "Respond to a plan approval request. Use approve=true to approve, approve=false to reject. Optional feedback can be provided."

    def execute(
        self, request_id: str, approve: bool = True, feedback: str = ""
    ) -> ToolResult:
        """Respond to a plan approval request."""
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
        request = _protocol_manager.get_plan_request(request_id)
        if request is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Plan approval request '{request_id}' not found",
            )

        _protocol_manager.respond_plan(request_id, approve, feedback)
        status = "approved" if approve else "rejected"
        msg = f"Plan approval request {request_id} {status}"
        if feedback:
            msg += f". Feedback: {feedback}"
        return ToolResult(
            tool_call_id="",
            output=msg,
        )
