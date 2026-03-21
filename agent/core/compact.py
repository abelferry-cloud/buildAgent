"""s06: Three-Layer Compression Manager - Micro, Auto, and Archive compression."""

import uuid
from dataclasses import dataclass, field

from agent.core.loop import Agent, Message
from agent.utils.compression import (
    ArchivedMessages,
    AutoCompressor,
    ArchivalCompressor,
    MicroCompressor,
)


@dataclass
class CompressionConfig:
    """Configuration thresholds for the CompressionManager."""

    micro_compact_threshold: int = 100
    auto_compact_interval: int = 50
    archive_after_messages: int = 100


class CompressionManager:
    """
    Three-layer compression system for managing conversation history.

    Layer 1 - Micro-compact:
        Applied to individual messages. Removes whitespace, shortens tool names.
        Threshold-based: only compacts messages over micro_compact_threshold chars.

    Layer 2 - Auto-compact:
        Summarizes old messages when conversation gets long.
        Triggered when messages exceed auto_compact_interval.

    Layer 3 - Archive:
        Moves old conversation to file-based storage.
        Triggered when messages exceed archive_after_messages.

    The compression manager operates on an Agent's message history to keep
    it manageable while preserving important context.
    """

    def __init__(
        self,
        agent: Agent,
        config: CompressionConfig | None = None,
    ):
        """
        Initialize the CompressionManager.

        Args:
            agent: The Agent whose messages will be compressed
            config: Optional configuration thresholds
        """
        self.agent = agent
        self.config = config or CompressionConfig()

        # Initialize compressors
        self._micro = MicroCompressor(
            threshold=self.config.micro_compact_threshold
        )
        self._auto = AutoCompressor(interval=self.config.auto_compact_interval)
        self._archive = ArchivalCompressor(
            after_messages=self.config.archive_after_messages
        )

        # Track archives
        self._archives: dict[str, ArchivedMessages] = {}
        self._archive_counter = 0

    def micro_compact(self, message: Message) -> Message:
        """
        Apply micro-compaction to a single message.

        Args:
            message: The message to compact

        Returns:
            Compacted message
        """
        return self._micro.compact(message)

    def auto_compact(self, messages: list[Message]) -> list[Message]:
        """
        Apply auto-compaction to message list.

        Summarizes older messages when threshold is exceeded.

        Args:
            messages: Full message list

        Returns:
            Compacted message list
        """
        return self._auto.compact(messages)

    def archive(self, messages: list[Message]) -> ArchivedMessages:
        """
        Archive old messages to file storage.

        Args:
            messages: Full message list

        Returns:
            ArchivedMessages object with file reference
        """
        self._archive_counter += 1
        archive_id = f"archive_{self._archive_counter}_{uuid.uuid4().hex[:8]}"

        archived = self._archive.archive(messages, archive_id)

        if archived.message_count > 0:
            self._archives[archive_id] = archived

        return archived

    def compress_if_needed(self, messages: list[Message]) -> list[Message]:
        """
        Apply appropriate compression based on message count.

        Checks thresholds and applies compression layers as needed.

        Args:
            messages: Current message list

        Returns:
            Potentially compressed message list
        """
        # Layer 3: Archive check (largest threshold)
        if self._archive.should_archive(messages):
            archived = self.archive(messages)
            # Return only the reference message + recent messages
            if archived.message_count > 0:
                ref_msg = Message(
                    role="system",
                    content=f"[Archived {archived.message_count} messages to {archived.file_path}]",
                )
                # Keep last portion of messages
                keep_count = self.config.archive_after_messages
                recent = messages[-keep_count:]
                return [ref_msg] + recent

        # Layer 2: Auto-compact check
        if self._auto.should_compact(messages):
            return self.auto_compact(messages)

        # Layer 1: Micro-compact individual messages
        return [self.micro_compact(msg) for msg in messages]

    def get_archive(self, archive_id: str) -> ArchivedMessages | None:
        """Get an archive by ID."""
        return self._archives.get(archive_id)

    def list_archives(self) -> list[str]:
        """List all archive IDs."""
        return list(self._archives.keys())

    def restore_archive(self, archive_id: str) -> list[Message] | None:
        """
        Restore messages from an archive file.

        Args:
            archive_id: ID of the archive to restore

        Returns:
            List of archived messages, or None if not found
        """
        return self._archive.load_archive(archive_id)

    @property
    def stats(self) -> dict:
        """Get compression statistics."""
        return {
            "micro_threshold": self.config.micro_compact_threshold,
            "auto_interval": self.config.auto_compact_interval,
            "archive_threshold": self.config.archive_after_messages,
            "active_archives": len(self._archives),
            "total_archived_messages": sum(
                a.message_count for a in self._archives.values()
            ),
        }
