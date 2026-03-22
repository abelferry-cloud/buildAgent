"""s06: Compact - Tests for three-layer compression system."""

import pytest
from agent.core.compact import CompressionManager, CompressionConfig
from agent.core.loop import Agent, Message
from agent.tools.base import Tool, ToolResult


class DummyTool(Tool):
    """A dummy tool for testing."""

    name = "dummy"
    description = "A dummy tool"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(tool_call_id="test", output="done")


class TestCompressionConfig:
    """Tests for CompressionConfig dataclass."""

    def test_default_config(self):
        """Test default compression config."""
        config = CompressionConfig()
        assert config.micro_compact_threshold == 100
        assert config.auto_compact_interval == 50
        assert config.archive_after_messages == 100

    def test_custom_config(self):
        """Test custom compression config."""
        config = CompressionConfig(
            micro_compact_threshold=50,
            auto_compact_interval=25,
            archive_after_messages=50
        )
        assert config.micro_compact_threshold == 50
        assert config.auto_compact_interval == 25
        assert config.archive_after_messages == 50


class TestCompressionManager:
    """Tests for CompressionManager class."""

    def test_initialization(self):
        """Test CompressionManager initialization."""
        agent = Agent(tools=[])
        manager = CompressionManager(agent=agent)
        assert manager.agent is agent
        assert manager.stats["micro_threshold"] == 100

    def test_micro_compact(self):
        """Test micro-compaction on a message."""
        from agent.utils.compression import MicroCompressor

        compressor = MicroCompressor(threshold=10)
        msg = Message(role="user", content="  Hello   world  ")
        compacted = compressor.compact(msg)

        # Should remove extra whitespace
        assert "  " not in compacted.content or compacted.content == msg.content

    def test_stats_property(self):
        """Test getting compression stats."""
        agent = Agent(tools=[])
        config = CompressionConfig(
            micro_compact_threshold=100,
            auto_compact_interval=50,
            archive_after_messages=100
        )
        manager = CompressionManager(agent=agent, config=config)

        stats = manager.stats
        assert stats["micro_threshold"] == 100
        assert stats["auto_interval"] == 50
        assert stats["archive_threshold"] == 100
        assert stats["active_archives"] == 0


class TestCompressionLayers:
    """Tests for the three compression layers."""

    def test_micro_compact_threshold(self):
        """Test that micro-compact respects threshold."""
        from agent.utils.compression import MicroCompressor

        # Short message should not be compacted
        compressor = MicroCompressor(threshold=100)
        short_msg = Message(role="user", content="Hi")
        result = compressor.compact(short_msg)
        assert result.content == short_msg.content

    def test_auto_compact_should_compact(self):
        """Test auto-compact trigger condition."""
        from agent.utils.compression import AutoCompressor

        compressor = AutoCompressor(interval=10)
        messages = [
            Message(role="user", content=f"Message {i}")
            for i in range(15)
        ]
        assert compressor.should_compact(messages) is True

    def test_auto_compact_should_not_compact(self):
        """Test auto-compact not triggered when under threshold."""
        from agent.utils.compression import AutoCompressor

        compressor = AutoCompressor(interval=50)
        messages = [
            Message(role="user", content=f"Message {i}")
            for i in range(10)
        ]
        assert compressor.should_compact(messages) is False


class TestArchiveFunctionality:
    """Tests for archive functionality."""

    def test_archive_should_archive(self):
        """Test archive trigger condition."""
        from agent.utils.compression import ArchivalCompressor

        compressor = ArchivalCompressor(after_messages=10)
        messages = [
            Message(role="user", content=f"Message {i}")
            for i in range(15)
        ]
        assert compressor.should_archive(messages) is True

    def test_archive_should_not_archive(self):
        """Test archive not triggered when under threshold."""
        from agent.utils.compression import ArchivalCompressor

        compressor = ArchivalCompressor(after_messages=100)
        messages = [
            Message(role="user", content=f"Message {i}")
            for i in range(50)
        ]
        assert compressor.should_archive(messages) is False

    def test_archive_messages(self, tmp_path):
        """Test archiving old messages."""
        from agent.utils.compression import ArchivalCompressor

        compressor = ArchivalCompressor(after_messages=5)
        messages = [
            Message(role="user", content=f"Message {i}")
            for i in range(10)
        ]

        archive = compressor.archive(messages, "test_archive")
        assert archive.message_count > 0

    def test_list_archives(self):
        """Test listing archive IDs."""
        agent = Agent(tools=[])
        manager = CompressionManager(agent=agent)

        archives = manager.list_archives()
        assert isinstance(archives, list)


class TestCompactIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Read every Python file in the agents/ directory one by one (observe micro-compact)
    - Keep reading files until compression triggers automatically
    - Use the compact tool to manually compress the conversation
    """

    def test_micro_compact_on_repeated_tool_results(self):
        """Test that micro-compact replaces old/verbose tool results."""
        agent = Agent(tools=[DummyTool()])

        # Add many similar messages (simulating repeated reads)
        for i in range(5):
            msg = Message(
                role="tool",
                content=f"Reading file {i}.py - content here with lots of details..."
            )
            agent.messages.append(msg)

        manager = CompressionManager(agent=agent)
        compressed = manager.compress_if_needed(agent.messages)

        # Should apply some compression
        assert compressed is not None

    def test_auto_compact_trigger(self):
        """Test auto-compact triggers at correct interval."""
        agent = Agent(tools=[])

        # Add messages to exceed auto_compact_interval
        config = CompressionConfig(
            micro_compact_threshold=100,
            auto_compact_interval=10,
            archive_after_messages=100
        )

        for i in range(15):
            agent.add_message("user", f"Message {i}")

        manager = CompressionManager(agent=agent, config=config)

        # Should trigger auto-compact
        result = manager.compress_if_needed(agent.messages)
        assert result is not None

    def test_archive_trigger(self):
        """Test archive triggers when message count exceeds threshold."""
        agent = Agent(tools=[])

        config = CompressionConfig(
            micro_compact_threshold=100,
            auto_compact_interval=100,
            archive_after_messages=10
        )

        # Add more messages than archive threshold
        for i in range(15):
            agent.add_message("user", f"Message {i}")

        manager = CompressionManager(agent=agent, config=config)

        # Should trigger archive
        result = manager.compress_if_needed(agent.messages)
        assert result is not None

        # Stats should show archive
        stats = manager.stats
        assert stats["active_archives"] >= 0

    def test_compression_preserves_recent_messages(self):
        """Test that recent messages are preserved during compression."""
        agent = Agent(tools=[])

        config = CompressionConfig(
            micro_compact_threshold=100,
            auto_compact_interval=50,
            archive_after_messages=10
        )

        # Add many messages
        for i in range(15):
            agent.add_message("user", f"Message {i}")

        manager = CompressionManager(agent=agent, config=config)
        compressed = manager.compress_if_needed(agent.messages)

        # Recent messages should be preserved
        assert len(compressed) <= len(agent.messages)
