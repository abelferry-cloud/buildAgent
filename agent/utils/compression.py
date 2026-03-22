"""s06: Compression Utilities - Micro, Auto, and Archive compression strategies."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agent.core.loop import Message


# Tool name abbreviations for micro-compact
TOOL_ABBREVIATIONS = {
    "bash": "bsh",
    "read": "rd",
    "write": "wr",
    "glob": "gl",
    "spawn": "spn",
    "todo_add": "t_add",
    "todo_list": "t_lst",
    "todo_done": "t_dn",
}


@dataclass
class ArchivedMessages:
    """Archived conversation segment stored in a file."""

    archive_id: str
    messages: list[Message]
    file_path: str
    message_count: int
    archived_at: float


class MicroCompressor:
    """
    Micro-compaction: Remove whitespace, shorten tool names.

    Applied to individual messages to reduce size while preserving meaning.
    """

    def __init__(self, threshold: int = 100):
        """
        Initialize MicroCompressor.

        Args:
            threshold: Minimum message length to trigger compaction
        """
        self.threshold = threshold

    def compact(self, message: Message) -> Message:
        """
        Apply micro-compaction to a message.

        - Removes leading/trailing whitespace
        - Collapses multiple spaces to single space
        - Shortens tool names using abbreviations

        Args:
            message: Original message

        Returns:
            Compacted message (may be same object if no changes needed)
        """
        # Lazy import to avoid circular dependency
        from agent.core.loop import Message

        if len(message.content) < self.threshold:
            return message

        content = message.content

        # Remove leading/trailing whitespace
        content = content.strip()

        # Collapse multiple spaces
        content = re.sub(r"\s+", " ", content)

        # Shorten tool names in tool_calls
        if message.tool_calls:
            compacted_calls = []
            for call in message.tool_calls:
                short_name = TOOL_ABBREVIATIONS.get(call.name, call.name)
                compacted_calls.append(
                    type(call)(
                        id=call.id,
                        name=short_name,
                        arguments=call.arguments,
                    )
                )
            return Message(
                role=message.role,
                content=content,
                tool_calls=compacted_calls,
                tool_call_id=message.tool_call_id,
                name=message.name,
                created_at=message.created_at,
            )

        return Message(
            role=message.role,
            content=content,
            tool_calls=message.tool_calls,
            tool_call_id=message.tool_call_id,
            name=message.name,
            created_at=message.created_at,
        )


class AutoCompressor:
    """
    Auto-compaction: Summarize old messages when threshold exceeded.

    Keeps recent messages intact, summarizes older ones to preserve context.
    """

    def __init__(self, interval: int = 50):
        """
        Initialize AutoCompressor.

        Args:
            interval: Number of messages before triggering summarization
        """
        self.interval = interval

    def should_compact(self, messages: list[Message]) -> bool:
        """Check if messages should be auto-compacted."""
        return len(messages) > self.interval

    def compact(self, messages: list[Message]) -> list[Message]:
        """
        Compact messages by summarizing older ones.

        Keeps the most recent messages intact, summarizes the rest.

        Args:
            messages: Full message list

        Returns:
            Compacted message list with summarized older messages
        """
        # Lazy import to avoid circular dependency
        from agent.core.loop import Message

        if not self.should_compact(messages):
            return messages

        # Keep recent messages intact (last interval messages)
        recent_count = self.interval // 2
        recent = messages[-recent_count:] if recent_count > 0 else []

        # Summarize older messages
        older = messages[:-recent_count] if recent_count > 0 else messages[:-1]

        if not older:
            return messages

        # Create a summary of older messages
        summary = self._summarize_messages(older)

        # Build result: summary + recent
        result = []

        # Add system message if present
        if messages and messages[0].role == "system":
            result.append(messages[0])

        # Add summary of older messages
        result.append(
            Message(
                role="system",
                content=f"[Previous {len(older)} messages summarized]: {summary}",
            )
        )

        # Add recent messages
        result.extend(recent)

        return result

    def _summarize_messages(self, messages: list[Message]) -> str:
        """
        Create a summary of multiple messages.

        Args:
            messages: Messages to summarize

        Returns:
            Summary string
        """
        if not messages:
            return "No previous context."

        # Simple summarization: count by role and topics
        roles = {}
        for msg in messages:
            roles[msg.role] = roles.get(msg.role, 0) + 1

        role_summary = ", ".join(f"{v} {k}" for k, v in roles.items())

        # Extract tool names if present
        tools_used = set()
        for msg in messages:
            if msg.tool_calls:
                for call in msg.tool_calls:
                    tools_used.add(call.name)

        tool_summary = ""
        if tools_used:
            tool_summary = f" Tools used: {', '.join(sorted(tools_used))}."

        return f"Conversation had {len(messages)} messages ({role_summary}).{tool_summary}"


class ArchivalCompressor:
    """
    Archival: Move old conversation to file-based storage.

    When messages exceed archive threshold, older messages are written to
    a file and replaced with a reference message.
    """

    def __init__(self, archive_dir: str = ".agent_archive", after_messages: int = 100):
        """
        Initialize ArchivalCompressor.

        Args:
            archive_dir: Directory to store archived files
            after_messages: Threshold for archiving
        """
        self.archive_dir = archive_dir
        self.after_messages = after_messages
        self._ensure_archive_dir()

    def _ensure_archive_dir(self) -> None:
        """Create archive directory if it doesn't exist."""
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def should_archive(self, messages: list[Message]) -> bool:
        """Check if messages should be archived."""
        return len(messages) > self.after_messages

    def archive(self, messages: list[Message], archive_id: str) -> ArchivedMessages:
        """
        Archive older messages to a file.

        Keeps the most recent messages in memory, stores older ones in a file.

        Args:
            messages: Full message list
            archive_id: Unique identifier for this archive

        Returns:
            ArchivedMessages object with file reference and metadata
        """
        if not self.should_archive(messages):
            return ArchivedMessages(
                archive_id=archive_id,
                messages=[],
                file_path="",
                message_count=0,
                archived_at=0.0,
            )

        # Keep recent messages (after_messages count)
        keep_count = self.after_messages
        to_archive = messages[:-keep_count] if keep_count > 0 else messages
        recent = messages[-keep_count:] if keep_count > 0 else []

        if not to_archive:
            return ArchivedMessages(
                archive_id=archive_id,
                messages=[],
                file_path="",
                message_count=0,
                archived_at=0.0,
            )

        # Write to file
        import time
        archive_path = os.path.join(self.archive_dir, f"{archive_id}.json")

        # Convert messages to dicts for JSON serialization
        archive_data = {
            "archive_id": archive_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": [
                        {"id": c.id, "name": c.name, "arguments": c.arguments}
                        for c in (msg.tool_calls or [])
                    ],
                    "tool_call_id": msg.tool_call_id,
                    "name": msg.name,
                    "created_at": msg.created_at,
                }
                for msg in to_archive
            ],
            "archived_at": time.time(),
        }

        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2)

        return ArchivedMessages(
            archive_id=archive_id,
            messages=to_archive,
            file_path=archive_path,
            message_count=len(to_archive),
            archived_at=time.time(),
        )

    def load_archive(self, archive_id: str) -> Optional[list[Message]]:
        """
        Load an archived conversation from file.

        Args:
            archive_id: Archive identifier

        Returns:
            List of archived messages, or None if not found
        """
        archive_path = os.path.join(self.archive_dir, f"{archive_id}.json")
        if not os.path.exists(archive_path):
            return None

        with open(archive_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        messages = []
        for msg_data in data.get("messages", []):
            tool_calls = None
            if msg_data.get("tool_calls"):
                tool_calls = [
                    type("ToolCall", (), tc)() for tc in msg_data["tool_calls"]
                ]
            messages.append(
                Message(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    tool_calls=tool_calls,
                    tool_call_id=msg_data.get("tool_call_id"),
                    name=msg_data.get("name"),
                    created_at=msg_data.get("created_at", 0.0),
                )
            )

        return messages
