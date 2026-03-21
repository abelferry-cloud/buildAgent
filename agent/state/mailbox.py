"""s09: Mailbox - File-based inbox/outbox for inter-agent messaging."""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class MessageRole(Enum):
    """Role of a message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    TEAMMATE = "teammate"


class ProtocolType(Enum):
    """Communication protocol type."""

    DIRECT = "direct"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class Message:
    """A message between agents."""

    id: str
    from_: str  # Use from_ to avoid Python keyword
    to: str
    content: str
    role: MessageRole = MessageRole.TEAMMATE
    protocol: ProtocolType = ProtocolType.DIRECT
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    read: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "from": self.from_,
            "to": self.to,
            "content": self.content,
            "role": self.role.value,
            "protocol": self.protocol.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "read": self.read,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            from_=data["from"],
            to=data["to"],
            content=data["content"],
            role=MessageRole(data.get("role", "teammate")),
            protocol=ProtocolType(data.get("protocol", "direct")),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            read=data.get("read", False),
        )


class Mailbox:
    """
    File-based mailbox for inter-agent messages.

    Uses inbox.jsonl and outbox.jsonl files for message storage.
    """

    def __init__(self, mailbox_path: str):
        """Initialize the mailbox with a directory path."""
        self._path = Path(mailbox_path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._inbox_path = self._path / "inbox.jsonl"
        self._outbox_path = self._path / "outbox.jsonl"

        # Ensure files exist
        self._inbox_path.touch(exist_ok=True)
        self._outbox_path.touch(exist_ok=True)

    def send(self, message: Message) -> None:
        """
        Send a message (write to outbox).

        The message is appended to the outbox file.
        """
        with open(self._outbox_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(message.to_dict()) + "\n")

    def receive_all(self) -> list[Message]:
        """
        Receive all unread messages from inbox.

        Messages are parsed but not automatically marked as read.
        """
        if not self._inbox_path.exists():
            return []

        messages = []
        with open(self._inbox_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = Message.from_dict(data)
                    if not message.read:
                        messages.append(message)
                except json.JSONDecodeError:
                    continue

        messages.sort(key=lambda m: m.created_at)
        return messages

    def mark_read(self, message_ids: list[str]) -> None:
        """
        Mark messages as read.

        Rewrites the inbox file with updated read status.
        """
        if not self._inbox_path.exists():
            return

        messages = []
        with open(self._inbox_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = Message.from_dict(data)
                    if message.id in message_ids:
                        message.read = True
                    messages.append(message)
                except json.JSONDecodeError:
                    continue

        # Rewrite the inbox file
        with open(self._inbox_path, "w", encoding="utf-8") as f:
            for message in messages:
                f.write(json.dumps(message.to_dict()) + "\n")

    def get_outbox(self) -> list[Message]:
        """Get all messages in the outbox (sent messages)."""
        if not self._outbox_path.exists():
            return []

        messages = []
        with open(self._outbox_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    messages.append(Message.from_dict(data))
                except json.JSONDecodeError:
                    continue

        messages.sort(key=lambda m: m.created_at)
        return messages

    def clear_inbox(self) -> None:
        """Clear all messages from inbox."""
        if self._inbox_path.exists():
            self._inbox_path.unlink()
        self._inbox_path.touch()

    def clear_outbox(self) -> None:
        """Clear all messages from outbox."""
        if self._outbox_path.exists():
            self._outbox_path.unlink()
        self._outbox_path.touch()
