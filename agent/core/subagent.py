"""s04: Subagent Spawning - Isolated subagent execution with message passing."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from agent.core.loop import Agent, Message
from agent.tools.base import Tool


@dataclass
class Subagent:
    """An isolated subagent with its own message history."""

    id: str
    name: str
    role: str
    tools: list[str]
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    terminated: bool = False


class SubagentManager:
    """
    Manages subagent lifecycle and message passing.

    Each subagent runs in isolation with its own message history.
    Communication happens via send/receive rather than shared state.
    """

    def __init__(self):
        self._subagents: dict[str, Subagent] = {}

    def spawn(self, name: str, role: str, tools: list[str]) -> str:
        """
        Spawn a new subagent.

        Args:
            name: Human-readable name for the subagent
            role: Role description (e.g., "code reviewer", "researcher")
            tools: List of tool names available to this subagent

        Returns:
            subagent_id: Unique identifier for the spawned subagent
        """
        subagent_id = str(uuid.uuid4())[:12]
        subagent = Subagent(
            id=subagent_id,
            name=name,
            role=role,
            tools=tools,
        )
        self._subagents[subagent_id] = subagent
        return subagent_id

    def send(self, subagent_id: str, message: str) -> None:
        """
        Send a message to a subagent's inbox.

        Args:
            subagent_id: Target subagent identifier
            message: Message content to send

        Raises:
            ValueError: If subagent does not exist or is terminated
        """
        subagent = self._get_subagent(subagent_id)
        subagent.messages.append(
            Message(role="user", content=message, name="parent")
        )

    def receive(self, subagent_id: str) -> list[Message]:
        """
        Receive all pending messages from a subagent.

        Args:
            subagent_id: Subagent identifier

        Returns:
            List of messages from the subagent since last receive

        Raises:
            ValueError: If subagent does not exist or is terminated
        """
        subagent = self._get_subagent(subagent_id)
        # Return all messages that are not from "parent" (i.e., subagent's responses)
        responses = [
            msg for msg in subagent.messages
            if msg.name != "parent"
        ]
        return responses

    def terminate(self, subagent_id: str) -> None:
        """
        Terminate a subagent.

        Args:
            subagent_id: Subagent identifier to terminate

        Raises:
            ValueError: If subagent does not exist
        """
        subagent = self._subagents.get(subagent_id)
        if not subagent:
            raise ValueError(f"Subagent '{subagent_id}' not found")
        subagent.terminated = True
        del self._subagents[subagent_id]

    def get_subagent(self, subagent_id: str) -> Optional[Subagent]:
        """Get subagent info by ID."""
        return self._subagents.get(subagent_id)

    def list_subagents(self) -> list[Subagent]:
        """List all active (non-terminated) subagents."""
        return list(self._subagents.values())

    def _get_subagent(self, subagent_id: str) -> Subagent:
        """Get a subagent or raise ValueError if not found/terminated."""
        subagent = self._subagents.get(subagent_id)
        if not subagent:
            raise ValueError(f"Subagent '{subagent_id}' not found")
        if subagent.terminated:
            raise ValueError(f"Subagent '{subagent_id}' has been terminated")
        return subagent

    def inject_agent(self, subagent_id: str, agent: Agent) -> None:
        """
        Inject an Agent instance into a subagent for actual execution.

        This bridges the SubagentManager with the Agent loop.

        Args:
            subagent_id: Target subagent identifier
            agent: Agent instance to inject
        """
        subagent = self._get_subagent(subagent_id)
        # Store reference to agent for this subagent
        subagent._agent = agent

    def get_agent(self, subagent_id: str) -> Optional[Agent]:
        """Get the Agent instance for a subagent."""
        subagent = self._subagents.get(subagent_id)
        if subagent:
            return getattr(subagent, "_agent", None)
        return None

    def subagent_count(self) -> int:
        """Return count of active subagents."""
        return len(self._subagents)
