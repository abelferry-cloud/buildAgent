"""s10: Protocol base classes for team communication."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProtocolMessage:
    """A message in a protocol exchange."""

    request_id: str
    action: str
    from_: str = ""
    to: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    is_response: bool = False


@dataclass
class RawMessage:
    """Raw serialized message format."""

    source: str
    destination: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Protocol(ABC):
    """
    Abstract base class for communication protocols.

    A protocol defines how agents exchange messages and coordinate actions.
    """

    @abstractmethod
    def create_request(self, to: str, action: str, params: dict) -> ProtocolMessage:
        """
        Create a request message.

        Args:
            to: The recipient identifier
            action: The action being requested
            params: Parameters for the action

        Returns:
            A ProtocolMessage representing the request
        """
        pass

    @abstractmethod
    def parse_response(self, raw: RawMessage) -> ProtocolMessage:
        """
        Parse a raw response message.

        Args:
            raw: The raw message to parse

        Returns:
            A parsed ProtocolMessage
        """
        pass

    def create_response(
        self, to: str, in_response_to: str, result: dict, from_: str = ""
    ) -> ProtocolMessage:
        """
        Create a response message.

        Args:
            to: The recipient identifier
            in_response_to: The request_id being responded to
            result: The result data
            from_: The sender identifier

        Returns:
            A ProtocolMessage representing the response
        """
        import time
        import uuid

        return ProtocolMessage(
            request_id=str(uuid.uuid4()),
            action="response",
            from_=from_,
            to=to,
            payload={"result": result, "in_response_to": in_response_to},
            timestamp=time.time(),
            is_response=True,
        )
