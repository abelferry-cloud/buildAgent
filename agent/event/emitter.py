"""s12: Event Emitter - Event handling and dispatch system."""

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Event:
    """
    Represents an event in the system.

    Events are the core data structure for the event-driven architecture.
    """

    id: str
    type: str
    timestamp: float
    source: str
    data: dict[str, Any]
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: str,
        source: str,
        data: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Event":
        """
        Create a new event.

        Args:
            event_type: The type of event
            source: The source identifier
            data: Event data payload
            correlation_id: Optional ID for correlating related events
            metadata: Optional metadata

        Returns:
            A new Event instance
        """
        return cls(
            id=str(uuid.uuid4())[:8],
            type=event_type,
            timestamp=time.time(),
            source=source,
            data=data or {},
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


class EventHandler:
    """
    Wrapper for an event handler function with metadata.
    """

    def __init__(
        self,
        handler: Callable[[Event], None],
        event_type: str,
        subscriber_id: str | None = None,
    ):
        self.handler = handler
        self.event_type = event_type
        self.subscriber_id = subscriber_id or str(uuid.uuid4())[:8]
        self.call_count: int = 0
        self.last_called: float | None = None

    def __call__(self, event: Event) -> None:
        """Execute the handler."""
        self.call_count += 1
        self.last_called = time.time()
        self.handler(event)

    def __repr__(self) -> str:
        return f"EventHandler({self.event_type}, calls={self.call_count})"


class EventEmitter:
    """
    Event emitter for publish-subscribe messaging.

    Provides a way to register handlers for specific event types
    and emit events to all registered subscribers.
    """

    def __init__(self):
        """Initialize the event emitter."""
        self._handlers: dict[str, list[EventHandler]] = {}
        self._lock = threading.Lock()
        self._global_handlers: list[EventHandler] = []
        self._event_history: list[Event] = []
        self._max_history: int = 1000

    def emit(self, event: Event) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event: The event to emit
        """
        with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]

            # Get handlers for this event type
            handlers = self._handlers.get(event.type, []).copy()
            global_handlers = self._global_handlers.copy()

        # Call type-specific handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # Don't let handler errors break event emission
                pass

        # Call global handlers
        for handler in global_handlers:
            try:
                handler(event)
            except Exception:
                pass

    def on(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        subscriber_id: str | None = None,
    ) -> EventHandler:
        """
        Register a handler for an event type.

        Args:
            event_type: The event type to subscribe to
            handler: The handler function
            subscriber_id: Optional subscriber identifier

        Returns:
            The EventHandler wrapper
        """
        with self._lock:
            event_handler = EventHandler(handler, event_type, subscriber_id)
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(event_handler)
            return event_handler

    def off(
        self,
        event_type: str | None = None,
        handler: Callable[[Event], None] | None = None,
        subscriber_id: str | None = None,
    ) -> int:
        """
        Unregister handlers.

        Can remove handlers by:
        - event_type only (removes all handlers for that type)
        - event_type + handler
        - subscriber_id only (removes all handlers for that subscriber)

        Args:
            event_type: The event type
            handler: The specific handler function
            subscriber_id: The subscriber identifier

        Returns:
            Number of handlers removed
        """
        with self._lock:
            if event_type is None and subscriber_id is None:
                # Can't remove without some criteria
                return 0

            if event_type is not None and subscriber_id is None and handler is None:
                # Remove all handlers for this event type
                count = len(self._handlers.get(event_type, []))
                if event_type in self._handlers:
                    del self._handlers[event_type]
                return count

            # More specific removal
            removed = 0
            if event_type:
                handlers = self._handlers.get(event_type, [])
                new_handlers = []
                for h in handlers:
                    if subscriber_id and h.subscriber_id == subscriber_id:
                        removed += 1
                    elif handler and h.handler == handler:
                        removed += 1
                    else:
                        new_handlers.append(h)
                self._handlers[event_type] = new_handlers

            # Also check global handlers
            if subscriber_id:
                new_global = []
                for h in self._global_handlers:
                    if h.subscriber_id != subscriber_id:
                        new_global.append(h)
                    else:
                        removed += 1
                self._global_handlers = new_global

            return removed

    def on_any(self, handler: Callable[[Event], None]) -> EventHandler:
        """
        Register a handler for all events.

        Args:
            handler: The handler function

        Returns:
            The EventHandler wrapper
        """
        with self._lock:
            event_handler = EventHandler(handler, "*")
            self._global_handlers.append(event_handler)
            return event_handler

    def off_any(self, subscriber_id: str) -> int:
        """
        Remove all global handlers for a subscriber.

        Args:
            subscriber_id: The subscriber identifier

        Returns:
            Number of handlers removed
        """
        with self._lock:
            original = len(self._global_handlers)
            self._global_handlers = [
                h for h in self._global_handlers if h.subscriber_id != subscriber_id
            ]
            return original - len(self._global_handlers)

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """
        Get all handlers for an event type.

        Args:
            event_type: The event type

        Returns:
            List of EventHandlers
        """
        with self._lock:
            return list(self._handlers.get(event_type, []))

    def get_all_event_types(self) -> list[str]:
        """
        Get all event types with registered handlers.

        Returns:
            List of event type names
        """
        with self._lock:
            return list(self._handlers.keys())

    def get_subscriber_ids(self, event_type: str | None = None) -> list[str]:
        """
        Get subscriber IDs for an event type or all subscribers.

        Args:
            event_type: Optional event type to filter by

        Returns:
            List of subscriber IDs
        """
        with self._lock:
            if event_type:
                return [h.subscriber_id for h in self._handlers.get(event_type, [])]
            else:
                ids = set()
                for handlers in self._handlers.values():
                    for h in handlers:
                        ids.add(h.subscriber_id)
                for h in self._global_handlers:
                    ids.add(h.subscriber_id)
                return list(ids)

    def get_history(
        self,
        event_type: str | None = None,
        since: float | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """
        Get recent event history.

        Args:
            event_type: Optional event type filter
            since: Optional timestamp to filter from
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        with self._lock:
            history = self._event_history.copy()

        if event_type:
            history = [e for e in history if e.type == event_type]
        if since is not None:
            history = [e for e in history if e.timestamp >= since]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear the event history."""
        with self._lock:
            self._event_history.clear()

    def handler_stats(self) -> dict[str, Any]:
        """Get statistics about registered handlers."""
        with self._lock:
            stats = {
                "event_types": len(self._handlers),
                "total_handlers": sum(len(h) for h in self._handlers.values()),
                "global_handlers": len(self._global_handlers),
                "history_size": len(self._event_history),
                "by_type": {},
            }
            for event_type, handlers in self._handlers.items():
                stats["by_type"][event_type] = {
                    "count": len(handlers),
                    "subscribers": list(set(h.subscriber_id for h in handlers)),
                }
            return stats
