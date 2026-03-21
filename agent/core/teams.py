"""s09: TeammateManager - Multi-agent team coordination."""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from agent.core.loop import Agent, Message
from agent.state.mailbox import Mailbox, Message as TeamMessage, MessageRole, ProtocolType


class TeammateStatus(Enum):
    """Status of a teammate."""

    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class AgentConfig:
    """Configuration for a teammate agent."""

    model: str = "claude-opus-4-6"
    system_prompt: str = "You are a helpful assistant."
    max_iterations: int = 100
    tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "model": self.model,
            "system_prompt": self.system_prompt,
            "max_iterations": self.max_iterations,
            "tools": self.tools,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentConfig":
        """Create from dictionary."""
        return cls(
            model=data.get("model", "claude-opus-4-6"),
            system_prompt=data.get("system_prompt", "You are a helpful assistant."),
            max_iterations=data.get("max_iterations", 100),
            tools=data.get("tools", []),
        )


@dataclass
class TeammateInfo:
    """Information about a teammate."""

    name: str
    role: str
    status: TeammateStatus
    agent_config: AgentConfig
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "agent_config": self.agent_config.to_dict(),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeammateInfo":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            role=data["role"],
            status=TeammateStatus(data.get("status", "offline")),
            agent_config=AgentConfig.from_dict(data.get("agent_config", {})),
            created_at=data.get("created_at", time.time()),
        )


class TeammateManager:
    """
    Manages a team of agents with mailbox-based communication.

    Each teammate has their own inbox and outbox for inter-agent messaging.
    """

    def __init__(self, team_id: str, mailbox_dir: str):
        """
        Initialize the teammate manager.

        Args:
            team_id: Unique identifier for the team.
            mailbox_dir: Directory for mailbox files.
        """
        self._team_id = team_id
        self._mailbox_dir = Path(mailbox_dir)
        self._mailbox_dir.mkdir(parents=True, exist_ok=True)
        self._team_dir = self._mailbox_dir / team_id
        self._team_dir.mkdir(parents=True, exist_ok=True)
        self._teammates: dict[str, TeammateInfo] = {}
        self._statuses: dict[str, TeammateStatus] = {}
        self._mailboxes: dict[str, Mailbox] = {}
        self._agents: dict[str, Agent] = {}

    def _get_teammate_dir(self, name: str) -> Path:
        """Get the directory for a teammate's mailbox."""
        return self._team_dir / name

    def _get_or_create_mailbox(self, name: str) -> Mailbox:
        """Get or create a mailbox for a teammate."""
        if name not in self._mailboxes:
            teammate_dir = self._get_teammate_dir(name)
            self._mailboxes[name] = Mailbox(str(teammate_dir))
        return self._mailboxes[name]

    def create_teammate(self, name: str, role: str, agent_config: AgentConfig) -> str:
        """
        Create a new teammate.

        Returns the teammate name (used as ID).
        """
        # Create teammate directory and mailbox
        teammate_dir = self._get_teammate_dir(name)
        Mailbox(str(teammate_dir))

        # Create teammate info
        info = TeammateInfo(
            name=name,
            role=role,
            status=TeammateStatus.IDLE,
            agent_config=agent_config,
        )
        self._teammates[name] = info
        self._statuses[name] = TeammateStatus.IDLE

        # Create the agent for this teammate
        agent = Agent(
            tools=[],  # Tools would be injected separately
            model=agent_config.model,
            system_prompt=agent_config.system_prompt,
            max_iterations=agent_config.max_iterations,
        )
        self._agents[name] = agent

        # Save teammate info
        self._save_teammate_info(name)

        return name

    def _save_teammate_info(self, name: str) -> None:
        """Save teammate info to file."""
        if name not in self._teammates:
            return
        path = self._get_teammate_dir(name) / "info.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._teammates[name].to_dict(), f, indent=2)

    def _load_teammate_info(self, name: str) -> Optional[TeammateInfo]:
        """Load teammate info from file."""
        path = self._get_teammate_dir(name) / "info.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return TeammateInfo.from_dict(json.load(f))

    def send_message(
        self,
        to: str,
        message: str,
        protocol: ProtocolType = ProtocolType.DIRECT,
        from_: Optional[str] = None,
    ) -> str:
        """
        Send a message to a teammate.

        Args:
            to: The recipient teammate name.
            message: The message content.
            protocol: The communication protocol.
            from_: The sender name (if None, uses the team_id as sender).

        Returns:
            The message ID.
        """
        sender = from_ or self._team_id
        msg = TeamMessage(
            id=str(uuid.uuid4())[:8],
            from_=sender,
            to=to,
            content=message,
            role=MessageRole.TEAMMATE,
            protocol=protocol,
        )

        # Write to recipient's inbox
        mailbox = self._get_or_create_mailbox(to)
        mailbox.send(msg)

        return msg.id

    def read_mailbox(self, teammate_name: str) -> list[TeamMessage]:
        """
        Read all unread messages from a teammate's inbox.

        Messages are not automatically marked as read.
        """
        mailbox = self._get_or_create_mailbox(teammate_name)
        return mailbox.receive_all()

    def mark_messages_read(self, teammate_name: str, message_ids: list[str]) -> None:
        """Mark messages as read."""
        mailbox = self._get_or_create_mailbox(teammate_name)
        mailbox.mark_read(message_ids)

    def get_teammate_status(self, name: str) -> TeammateStatus:
        """Get the status of a teammate."""
        # Try to load from file if not in memory
        if name not in self._statuses:
            info = self._load_teammate_info(name)
            if info is not None:
                self._statuses[name] = info.status
                self._teammates[name] = info

        return self._statuses.get(name, TeammateStatus.OFFLINE)

    def set_teammate_status(self, name: str, status: TeammateStatus) -> None:
        """Set the status of a teammate."""
        self._statuses[name] = status
        if name in self._teammates:
            self._teammates[name].status = status
            self._save_teammate_info(name)

    def list_teammates(self) -> list[TeammateInfo]:
        """List all teammates in the team."""
        # Load any teammates not in memory from disk
        if self._team_dir.exists():
            for item in self._team_dir.iterdir():
                if item.is_dir() and (item / "info.json").exists():
                    name = item.name
                    if name not in self._teammates:
                        info = self._load_teammate_info(name)
                        if info is not None:
                            self._teammates[name] = info

        return list(self._teammates.values())

    def get_teammate_agent(self, name: str) -> Optional[Agent]:
        """Get the agent instance for a teammate."""
        return self._agents.get(name)

    def broadcast(self, message: str, from_: Optional[str] = None) -> list[str]:
        """
        Broadcast a message to all teammates.

        Returns a list of message IDs sent.
        """
        message_ids = []
        for name in self._teammates:
            msg_id = self.send_message(
                to=name,
                message=message,
                protocol=ProtocolType.BROADCAST,
                from_=from_,
            )
            message_ids.append(msg_id)
        return message_ids

    def get_agent_config(self, name: str) -> Optional[AgentConfig]:
        """Get the agent configuration for a teammate."""
        if name in self._teammates:
            return self._teammates[name].agent_config
        info = self._load_teammate_info(name)
        return info.agent_config if info else None
