"""Protocol plan approval request tool."""

from agent.core.protocols import ProtocolManager
from agent.tools.base import Tool, ToolResult

_protocol_manager: ProtocolManager | None = None


def set_protocol_manager(pm: ProtocolManager) -> None:
    """Set the global protocol manager instance."""
    global _protocol_manager
    _protocol_manager = pm


class ProtocolPlanReqTool(Tool):
    """Request plan approval from a teammate."""

    name = "protocol_plan_req"
    description = "Request approval for a plan from a teammate. Returns a request_id to track the response."

    def execute(self, to: str, plan: str) -> ToolResult:
        """Send a plan approval request to a teammate."""
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

        if not plan:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Plan content is required",
            )

        request_id = _protocol_manager.create_plan_request(to, plan)
        return ToolResult(
            tool_call_id="",
            output=f"Plan approval request sent to {to}: {request_id}",
        )
