"""s09: Agent Teams - Tests for TeammateManager and mailbox-based communication."""

import pytest
import time
import json
from agent.core.teams import TeammateManager, TeammateStatus, AgentConfig, TeammateInfo
from agent.state.mailbox import Mailbox, Message, MessageRole, ProtocolType


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_agent_config_defaults(self):
        """Test default AgentConfig."""
        config = AgentConfig()
        assert config.model == "claude-opus-4-6"
        assert config.system_prompt == "You are a helpful assistant."
        assert config.max_iterations == 100
        assert config.tools == []

    def test_agent_config_custom(self):
        """Test custom AgentConfig."""
        config = AgentConfig(
            model="custom-model",
            system_prompt="Custom prompt",
            max_iterations=50,
            tools=["bash", "read"]
        )
        assert config.model == "custom-model"
        assert config.max_iterations == 50
        assert len(config.tools) == 2

    def test_agent_config_serialization(self):
        """Test AgentConfig to/from dict."""
        config = AgentConfig(model="test", tools=["bash"])
        d = config.to_dict()
        restored = AgentConfig.from_dict(d)
        assert restored.model == "test"
        assert restored.tools == ["bash"]


class TestTeammateInfo:
    """Tests for TeammateInfo dataclass."""

    def test_teammate_info_creation(self):
        """Test creating TeammateInfo."""
        config = AgentConfig()
        info = TeammateInfo(
            name="alice",
            role="coder",
            status=TeammateStatus.IDLE,
            agent_config=config
        )
        assert info.name == "alice"
        assert info.role == "coder"
        assert info.status == TeammateStatus.IDLE


class TestMailbox:
    """Tests for Mailbox class."""

    def test_mailbox_initialization(self, tmp_path):
        """Test Mailbox initialization."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))
        assert mailbox is not None

    def test_send_message(self, tmp_path):
        """Test sending a message writes to outbox."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))
        msg = Message(
            id="1",
            from_="alice",
            to="bob",
            content="Hello Bob",
            role=MessageRole.TEAMMATE,
            protocol=ProtocolType.DIRECT
        )
        mailbox.send(msg)

        # Verify message is in outbox
        outbox = mailbox.get_outbox()
        assert len(outbox) == 1
        assert outbox[0].content == "Hello Bob"

    def test_receive_messages_empty_inbox(self, tmp_path):
        """Test receiving messages from empty inbox."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))
        messages = mailbox.receive_all()
        assert len(messages) == 0

    def test_receive_messages_from_inbox(self, tmp_path):
        """Test receiving messages that were written to inbox."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))

        # Write a message directly to inbox (simulating another agent's send)
        msg = Message(
            id="1",
            from_="alice",
            to="bob",
            content="Hello",
            role=MessageRole.TEAMMATE,
            protocol=ProtocolType.DIRECT
        )
        with open(mailbox._inbox_path, "w") as f:
            f.write(json.dumps(msg.to_dict()) + "\n")

        messages = mailbox.receive_all()
        assert len(messages) == 1
        assert messages[0].content == "Hello"

    def test_mark_messages_read(self, tmp_path):
        """Test marking messages as read."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))

        # Write a message to inbox
        msg = Message(
            id="1",
            from_="alice",
            to="bob",
            content="Hello",
            role=MessageRole.TEAMMATE,
            protocol=ProtocolType.DIRECT
        )
        with open(mailbox._inbox_path, "w") as f:
            f.write(json.dumps(msg.to_dict()) + "\n")

        mailbox.mark_read(["1"])

        messages = mailbox.receive_all()
        assert len(messages) == 0  # All marked as read

    def test_get_outbox(self, tmp_path):
        """Test getting outbox messages."""
        mailbox = Mailbox(str(tmp_path / "mailbox"))
        msg = Message(
            id="1",
            from_="alice",
            to="bob",
            content="Hello",
            role=MessageRole.TEAMMATE,
            protocol=ProtocolType.DIRECT
        )
        mailbox.send(msg)

        outbox = mailbox.get_outbox()
        assert len(outbox) == 1


class TestTeammateManager:
    """Tests for TeammateManager class."""

    def test_initialization(self, tmp_path):
        """Test TeammateManager initialization."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        assert manager._team_id == "test-team"

    def test_create_teammate(self, tmp_path):
        """Test creating a teammate."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        config = AgentConfig(system_prompt="You are Alice")
        name = manager.create_teammate("alice", "coder", config)
        assert name == "alice"

    def test_get_teammate_status(self, tmp_path):
        """Test getting teammate status."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        config = AgentConfig()
        manager.create_teammate("alice", "coder", config)

        status = manager.get_teammate_status("alice")
        assert status == TeammateStatus.IDLE

    def test_set_teammate_status(self, tmp_path):
        """Test setting teammate status."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        config = AgentConfig()
        manager.create_teammate("alice", "coder", config)

        manager.set_teammate_status("alice", TeammateStatus.BUSY)
        assert manager.get_teammate_status("alice") == TeammateStatus.BUSY

    def test_list_teammates(self, tmp_path):
        """Test listing teammates."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        config = AgentConfig()

        manager.create_teammate("alice", "coder", config)
        manager.create_teammate("bob", "tester", config)

        teammates = manager.list_teammates()
        assert len(teammates) == 2
        names = [t.name for t in teammates]
        assert "alice" in names
        assert "bob" in names

    def test_send_message_returns_id(self, tmp_path):
        """Test send_message returns a message ID."""
        manager = TeammateManager(team_id="test-team", mailbox_dir=str(tmp_path))
        config = AgentConfig()
        manager.create_teammate("bob", "tester", config)

        msg_id = manager.send_message(to="bob", message="Hello Bob", from_="leader")
        assert msg_id is not None
        assert isinstance(msg_id, str)


class TestTeammateManagerIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Spawn alice (coder) and bob (tester). Have alice send bob a message.
    - Broadcast "status update: phase 1 complete" to all teammates
    - Check the lead inbox for any messages
    """

    def test_spawn_alice_and_bob(self, tmp_path):
        """Test spawning alice (coder) and bob (tester)."""
        manager = TeammateManager(team_id="main", mailbox_dir=str(tmp_path))

        alice_config = AgentConfig(
            system_prompt="You are Alice, a coder.",
            tools=["bash", "write"]
        )
        bob_config = AgentConfig(
            system_prompt="You are Bob, a tester.",
            tools=["bash", "read"]
        )

        manager.create_teammate("alice", "coder", alice_config)
        manager.create_teammate("bob", "tester", bob_config)

        teammates = manager.list_teammates()
        assert len(teammates) == 2

    def test_alice_sends_message_to_bob(self, tmp_path):
        """Test alice sends bob a message via team_send."""
        manager = TeammateManager(team_id="main", mailbox_dir=str(tmp_path))

        config = AgentConfig()
        manager.create_teammate("alice", "coder", config)
        manager.create_teammate("bob", "tester", config)

        # Alice sends message to Bob using team_send tool logic
        msg_id = manager.send_message(
            to="bob",
            message="Hey Bob, I finished the feature. Please review.",
            from_="alice"
        )

        assert msg_id is not None
        # Message should be in bob's mailbox (inbox file)
        bob_mailbox = manager._get_or_create_mailbox("bob")
        # The implementation writes to outbox of recipient
        outbox = bob_mailbox.get_outbox()
        assert len(outbox) == 1

    def test_broadcast_to_all_teammates(self, tmp_path):
        """Test broadcasting to all teammates."""
        manager = TeammateManager(team_id="main", mailbox_dir=str(tmp_path))

        config = AgentConfig()
        manager.create_teammate("alice", "coder", config)
        manager.create_teammate("bob", "tester", config)

        # Leader broadcasts
        msg_ids = manager.broadcast("status update: phase 1 complete", from_="leader")
        assert len(msg_ids) == 2

    def test_get_agent_config(self, tmp_path):
        """Test getting agent configuration for a teammate."""
        manager = TeammateManager(team_id="main", mailbox_dir=str(tmp_path))

        config = AgentConfig(model="custom-model", tools=["bash"])
        manager.create_teammate("alice", "coder", config)

        retrieved_config = manager.get_agent_config("alice")
        assert retrieved_config is not None
        assert retrieved_config.model == "custom-model"
