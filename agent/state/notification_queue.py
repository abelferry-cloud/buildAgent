"""s08: NotificationQueue - Event notification system for background jobs."""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class NotificationType(Enum):
    """Types of notifications."""

    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    JOB_CANCELLED = "job_cancelled"


@dataclass
class Notification:
    """A notification event."""

    id: str
    type: NotificationType
    job_id: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "job_id": self.job_id,
            "data": self.data,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            job_id=data["job_id"],
            data=data.get("data", {}),
            created_at=data.get("created_at", time.time()),
        )


class NotificationQueue:
    """
    Queue for notification events.

    Notifications are stored in a JSONL file and can be read and marked as processed.
    """

    def __init__(self, queue_path: str):
        """Initialize the notification queue with a file path."""
        self._path = Path(queue_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._read_ids: set[str] = set()

    def enqueue(self, notification: Notification) -> None:
        """Add a notification to the queue."""
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(notification.to_dict()) + "\n")

    def dequeue_all(self) -> list[Notification]:
        """
        Read all unread notifications.

        Notifications are not automatically marked as read; call mark_read() after processing.
        """
        if not self._path.exists():
            return []

        notifications = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    notification = Notification.from_dict(data)
                    if notification.id not in self._read_ids:
                        notifications.append(notification)
                except json.JSONDecodeError:
                    continue

        return notifications

    def mark_read(self, notification_ids: list[str]) -> None:
        """Mark notifications as read."""
        self._read_ids.update(notification_ids)

    def clear(self) -> None:
        """Remove all notifications from the queue."""
        if self._path.exists():
            self._path.unlink()
        self._read_ids.clear()

    def count_unread(self) -> int:
        """Count unread notifications."""
        return len(self.dequeue_all())
