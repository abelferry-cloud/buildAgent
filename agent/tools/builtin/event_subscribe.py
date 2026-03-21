"""s12: Event Subscribe tool - Subscribe to event types."""

import json

from agent.event.emitter import EventEmitter
from agent.tools.base import Tool, ToolResult


# Shared instance
_event_emitter: EventEmitter | None = None


def set_event_emitter(ee: EventEmitter) -> None:
    """Set the global event emitter instance."""
    global _event_emitter
    _event_emitter = ee


class EventSubscribeTool(Tool):
    """Subscribe to event types."""

    name = "event_subscribe"
    description = "Subscribe to an event type to receive notifications."

    def execute(
        self,
        event_type: str,
        subscriber_id: str | None = None,
    ) -> ToolResult:
        """
        Subscribe to an event type.

        Args:
            event_type: The event type to subscribe to
            subscriber_id: Optional subscriber identifier

        Returns:
            ToolResult with subscription info
        """
        if _event_emitter is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="EventEmitter not initialized",
            )

        if not event_type:
            return ToolResult(
                tool_call_id="",
                output="",
                error="Event type is required",
            )

        handler = _event_emitter.on(event_type, lambda e: None, subscriber_id)

        return ToolResult(
            tool_call_id="",
            output=json.dumps({
                "subscribed": True,
                "event_type": event_type,
                "subscriber_id": handler.subscriber_id,
            }),
        )
