"""s12: Event List tool - List recent events."""

import json

from agent.event.emitter import EventEmitter
from agent.event.stream import EventStream
from agent.tools.base import Tool, ToolResult


# Shared instances
_event_emitter: EventEmitter | None = None
_event_stream: EventStream | None = None


def set_event_emitter(ee: EventEmitter) -> None:
    """Set the global event emitter instance."""
    global _event_emitter
    _event_emitter = ee


def set_event_stream(es: EventStream) -> None:
    """Set the global event stream instance."""
    global _event_stream
    _event_stream = es


class EventListTool(Tool):
    """List recent events from the event stream."""

    name = "event_list"
    description = "List recent events, optionally filtered by type or time."

    def execute(
        self,
        event_type: str | None = None,
        since: float | None = None,
        limit: int = 100,
        source: str | None = None,
    ) -> ToolResult:
        """
        List events.

        Args:
            event_type: Optional event type filter
            since: Optional timestamp (seconds since epoch)
            limit: Maximum number of events to return
            source: Optional source filter

        Returns:
            ToolResult with list of events
        """
        if _event_stream is None:
            return ToolResult(
                tool_call_id="",
                output="",
                error="EventStream not initialized",
            )

        events = _event_stream.get_events(since=since, limit=limit)

        if event_type:
            events = [e for e in events if e.type == event_type]
        if source:
            events = [e for e in events if e.source == source]

        # Convert to serializable format
        event_data = [e.to_dict() for e in events]

        return ToolResult(
            tool_call_id="",
            output=json.dumps(event_data, indent=2),
        )
