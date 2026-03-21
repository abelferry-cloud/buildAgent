"""s12: Event Stream - Persistent event stream with replay support."""

import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from agent.event.emitter import Event


@dataclass
class StreamConfig:
    """Configuration for an event stream."""

    max_file_size_mb: int = 100
    max_events_per_file: int = 10000
    rotation_enabled: bool = True
    compression_enabled: bool = False


class EventStream:
    """
    Persistent event stream with file-based storage.

    Provides append-only event storage with support for
    event replay and filtering.
    """

    def __init__(self, stream_file: str, config: StreamConfig | None = None):
        """
        Initialize the event stream.

        Args:
            stream_file: Path to the stream file
            config: Optional stream configuration
        """
        self._stream_file = stream_file
        self._config = config or StreamConfig()
        self._lock = threading.Lock()
        self._ensure_stream_file()

    def _ensure_stream_file(self) -> None:
        """Ensure the stream file exists."""
        if not os.path.exists(self._stream_file):
            os.makedirs(os.path.dirname(self._stream_file) or ".", exist_ok=True)
            with open(self._stream_file, "w") as f:
                json.dump({"events": [], "metadata": {"created_at": time.time()}}, f)

    def append(self, event: Event) -> None:
        """
        Append an event to the stream.

        Args:
            event: The event to append
        """
        with self._lock:
            self._append_event_unlocked(event)

    def _append_event_unlocked(self, event: Event) -> None:
        """Append event without locking (caller must hold lock)."""
        try:
            with open(self._stream_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {"events": [], "metadata": {"created_at": time.time()}}

        event_dict = event.to_dict()
        data["events"].append(event_dict)
        data["metadata"]["last_updated"] = time.time()
        data["metadata"]["event_count"] = len(data["events"])

        # Check rotation
        if self._config.rotation_enabled:
            self._maybe_rotate(data)

        with open(self._stream_file, "w") as f:
            json.dump(data, f)

    def _maybe_rotate(self, data: dict[str, Any]) -> None:
        """Rotate the stream file if it exceeds the configured size."""
        file_size = os.path.getsize(self._stream_file)
        max_size = self._config.max_file_size_mb * 1024 * 1024

        if file_size > max_size or len(data["events"]) > self._config.max_events_per_file:
            # Create backup and start new file
            backup_file = f"{self._stream_file}.{int(time.time())}"
            with open(backup_file, "w") as f:
                json.dump(data, f)

            # Keep only recent events in main file
            recent_count = self._config.max_events_per_file // 2
            data["events"] = data["events"][-recent_count:]
            data["metadata"]["rotated_at"] = time.time()

    def get_events(
        self,
        since: float | None = None,
        until: float | None = None,
        limit: int | None = None,
    ) -> list[Event]:
        """
        Get events from the stream.

        Args:
            since: Optional start timestamp
            until: Optional end timestamp
            limit: Optional maximum number of events

        Returns:
            List of events matching the criteria
        """
        with self._lock:
            events = self._load_events()

        filtered = events
        if since is not None:
            filtered = [e for e in filtered if e.timestamp >= since]
        if until is not None:
            filtered = [e for e in filtered if e.timestamp <= until]

        # Sort by timestamp
        filtered.sort(key=lambda e: e.timestamp)

        if limit is not None:
            filtered = filtered[-limit:]

        return filtered

    def get_events_by_type(self, event_type: str) -> list[Event]:
        """
        Get all events of a specific type.

        Args:
            event_type: The event type to filter by

        Returns:
            List of events of the specified type
        """
        with self._lock:
            events = self._load_events()

        return [e for e in events if e.type == event_type]

    def get_events_by_source(self, source: str) -> list[Event]:
        """
        Get all events from a specific source.

        Args:
            source: The source identifier

        Returns:
            List of events from the source
        """
        with self._lock:
            events = self._load_events()

        return [e for e in events if e.source == source]

    def replay(
        self,
        handler: Callable[[Event], None],
        since: float | None = None,
        event_type: str | None = None,
    ) -> int:
        """
        Replay events through a handler.

        Args:
            handler: Function to call for each event
            since: Optional start timestamp
            event_type: Optional event type filter

        Returns:
            Number of events replayed
        """
        events = self.get_events(since=since)

        if event_type:
            events = [e for e in events if e.type == event_type]

        count = 0
        for event in events:
            try:
                handler(event)
                count += 1
            except Exception:
                # Don't let handler errors break replay
                pass

        return count

    def _load_events(self) -> list[Event]:
        """Load events from the stream file."""
        try:
            with open(self._stream_file, "r") as f:
                data = json.load(f)
                return [self._dict_to_event(e) for e in data.get("events", [])]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _dict_to_event(self, d: dict[str, Any]) -> Event:
        """Convert a dictionary to an Event."""
        return Event(
            id=d["id"],
            type=d["type"],
            timestamp=d["timestamp"],
            source=d["source"],
            data=d.get("data", {}),
            correlation_id=d.get("correlation_id"),
            metadata=d.get("metadata", {}),
        )

    def get_stream_info(self) -> dict[str, Any]:
        """
        Get information about the stream.

        Returns:
            Dict with stream metadata
        """
        with self._lock:
            try:
                with open(self._stream_file, "r") as f:
                    data = json.load(f)
                    return {
                        "file": self._stream_file,
                        "event_count": len(data.get("events", [])),
                        "metadata": data.get("metadata", {}),
                        "file_size_bytes": os.path.getsize(self._stream_file)
                        if os.path.exists(self._stream_file)
                        else 0,
                    }
            except (json.JSONDecodeError, FileNotFoundError):
                return {
                    "file": self._stream_file,
                    "event_count": 0,
                    "metadata": {},
                    "file_size_bytes": 0,
                }

    def search(
        self,
        query: str,
        field: str = "data",
        limit: int = 100,
    ) -> list[Event]:
        """
        Search events by content.

        Args:
            query: Search query string
            field: Field to search in ('data', 'source', 'type', 'all')
            limit: Maximum results

        Returns:
            List of matching events
        """
        events = self.get_events(limit=1000)
        results = []
        query_lower = query.lower()

        for event in events:
            match = False
            if field == "all":
                search_text = json.dumps(event.to_dict()).lower()
                match = query_lower in search_text
            elif field == "data":
                match = query_lower in json.dumps(event.data).lower()
            elif field == "source":
                match = query_lower in event.source.lower()
            elif field == "type":
                match = query_lower in event.type.lower()

            if match:
                results.append(event)

            if len(results) >= limit:
                break

        return results

    def get_event_count(self) -> int:
        """Get total event count in the stream."""
        with self._lock:
            try:
                with open(self._stream_file, "r") as f:
                    data = json.load(f)
                    return len(data.get("events", []))
            except (json.JSONDecodeError, FileNotFoundError):
                return 0

    def clear(self) -> None:
        """Clear all events from the stream."""
        with self._lock:
            with open(self._stream_file, "w") as f:
                json.dump(
                    {"events": [], "metadata": {"created_at": time.time(), "cleared_at": time.time()}},
                    f,
                )
