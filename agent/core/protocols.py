"""s10: Team Protocols - Request/response and notification protocols."""

import json
import threading
import time
import uuid
from abc import ABC
from concurrent.futures import Future, TimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable

from agent.protocols.base import Protocol, ProtocolMessage, RawMessage


@dataclass
class RequestFuture:
    """
    A future representing a pending request.

    Provides a way to wait for and retrieve the result of an asynchronous request.
    """

    request_id: str
    _result: Any = None
    _error: Exception | None = None
    _is_ready: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _event: threading.Event = field(default_factory=threading.Event)

    @property
    def result(self) -> Any:
        """Get the result of the request."""
        with self._lock:
            if self._error is not None:
                raise self._error
            return self._result

    @property
    def error(self) -> Exception | None:
        """Get the error if the request failed."""
        with self._lock:
            return self._error

    @property
    def is_ready(self) -> bool:
        """Check if the request is complete."""
        with self._lock:
            return self._is_ready

    def set_result(self, result: Any) -> None:
        """Set the result of the request."""
        with self._lock:
            self._result = result
            self._is_ready = True
            self._event.set()

    def set_error(self, error: Exception) -> None:
        """Set an error on the request."""
        with self._lock:
            self._error = error
            self._is_ready = True
            self._event.set()

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for the request to complete."""
        return self._event.wait(timeout)

    def get_result(self, timeout: float | None = None) -> Any:
        """
        Wait for and return the result.

        Raises:
            TimeoutError: If the request doesn't complete in time
            The original exception: If the request failed with an error
        """
        if not self.wait(timeout):
            raise TimeoutError(f"Request {self.request_id} timed out after {timeout}s")
        return self.result


class TeammateManager:
    """
    Manages teammate information and message routing.

    Keeps track of known teammates and their capabilities.
    """

    def __init__(self):
        self._teammates: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register_teammate(
        self, teammate_id: str, capabilities: list[str] | None = None
    ) -> None:
        """Register a teammate."""
        with self._lock:
            self._teammates[teammate_id] = {
                "id": teammate_id,
                "capabilities": capabilities or [],
                "registered_at": time.time(),
            }

    def get_teammate(self, teammate_id: str) -> dict[str, Any] | None:
        """Get teammate information."""
        with self._lock:
            return self._teammates.get(teammate_id)

    def list_teammates(self) -> list[dict[str, Any]]:
        """List all registered teammates."""
        with self._lock:
            return list(self._teammates.values())

    def has_teammate(self, teammate_id: str) -> bool:
        """Check if a teammate is registered."""
        with self._lock:
            return teammate_id in self._teammates


class RequestResponseProtocol(Protocol):
    """
    Two-way request/response protocol with request_id correlation.

    This protocol ensures every request gets a correlated response using
    request IDs. It supports both sending requests (with futures for async
    waiting) and receiving/handling responses.
    """

    def __init__(self, teammate_manager: TeammateManager | None = None):
        """
        Initialize the request/response protocol.

        Args:
            teammate_manager: Manager for tracking teammates
        """
        self._teammate_manager = teammate_manager or TeammateManager()
        self._pending_requests: dict[str, RequestFuture] = {}
        self._lock = threading.Lock()
        self._response_handlers: dict[str, Callable[[ProtocolMessage], None]] = {}

    def create_request(self, to: str, action: str, params: dict) -> ProtocolMessage:
        """Create a request message."""
        import time

        request_id = str(uuid.uuid4())
        return ProtocolMessage(
            request_id=request_id,
            action=action,
            from_="",
            to=to,
            payload=params,
            timestamp=time.time(),
            is_response=False,
        )

    def parse_response(self, raw: RawMessage) -> ProtocolMessage:
        """Parse a raw response message."""
        try:
            data = json.loads(raw.content)
            return ProtocolMessage(
                request_id=data.get("request_id", ""),
                action=data.get("action", "response"),
                from_=raw.source,
                to=raw.destination,
                payload=data.get("payload", {}),
                timestamp=data.get("timestamp", time.time()),
                is_response=True,
            )
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return ProtocolMessage(
                request_id="",
                action="response",
                from_=raw.source,
                to=raw.destination,
                payload={"raw": raw.content},
                timestamp=time.time(),
                is_response=True,
            )

    def parse_request(self, raw: RawMessage) -> ProtocolMessage:
        """Parse a raw request message."""
        try:
            data = json.loads(raw.content)
            return ProtocolMessage(
                request_id=data.get("request_id", str(uuid.uuid4())),
                action=data.get("action", ""),
                from_=raw.source,
                to=raw.destination,
                payload=data.get("payload", {}),
                timestamp=data.get("timestamp", time.time()),
                is_response=False,
            )
        except json.JSONDecodeError:
            return ProtocolMessage(
                request_id=str(uuid.uuid4()),
                action="unknown",
                from_=raw.source,
                to=raw.destination,
                payload={"raw": raw.content},
                timestamp=time.time(),
                is_response=False,
            )

    def send_request(
        self, to: str, action: str, params: dict, timeout: float = 30.0
    ) -> RequestFuture:
        """
        Send a request and return a future for the response.

        Args:
            to: The recipient identifier
            action: The action being requested
            params: Parameters for the action
            timeout: Maximum time to wait for response

        Returns:
            A RequestFuture that can be used to wait for the response
        """
        message = self.create_request(to, action, params)
        future = RequestFuture(request_id=message.request_id)

        with self._lock:
            self._pending_requests[message.request_id] = future

        # In a real implementation, this would send the message over a transport
        # For now, we store it for correlation when a response arrives
        return future

    def send_response(
        self, to: str, in_response_to: str, result: dict, from_: str = ""
    ) -> None:
        """
        Send a response to a request.

        Args:
            to: The recipient identifier
            in_response_to: The request_id being responded to
            result: The result data
            from_: The sender identifier
        """
        response = self.create_response(to, in_response_to, result, from_)

        # If there's a pending future for this request, resolve it
        with self._lock:
            future = self._pending_requests.get(in_response_to)
            if future is not None:
                future.set_result(result)
                del self._pending_requests[in_response_to]

        # In a real implementation, this would send the response over a transport

    def correlate_request(self, request_id: str) -> RequestFuture | None:
        """
        Get a future for an existing request by ID.

        Args:
            request_id: The request ID to look up

        Returns:
            The RequestFuture if found, None otherwise
        """
        with self._lock:
            return self._pending_requests.get(request_id)

    def handle_response(self, response: ProtocolMessage) -> None:
        """
        Handle an incoming response message.

        Args:
            response: The response message to handle
        """
        with self._lock:
            future = self._pending_requests.get(response.request_id)
            if future is not None:
                # Check if there's an error in the response
                if "error" in response.payload:
                    error_msg = response.payload["error"]
                    future.set_error(Exception(error_msg))
                else:
                    future.set_result(response.payload.get("result"))
                del self._pending_requests[response.request_id]

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending request.

        Args:
            request_id: The request ID to cancel

        Returns:
            True if the request was found and cancelled
        """
        with self._lock:
            if request_id in self._pending_requests:
                future = self._pending_requests[request_id]
                future.set_error(Exception("Request cancelled"))
                del self._pending_requests[request_id]
                return True
            return False

    def pending_count(self) -> int:
        """Return the number of pending requests."""
        with self._lock:
            return len(self._pending_requests)

    def get_pending_requests(self) -> list[str]:
        """Get list of pending request IDs."""
        with self._lock:
            return list(self._pending_requests.keys())


class NotificationProtocol(Protocol):
    """
    Fire-and-forget notification protocol.

    This protocol is used for one-way event notifications that don't
    require a response.
    """

    def __init__(self, teammate_manager: TeammateManager | None = None):
        """
        Initialize the notification protocol.

        Args:
            teammate_manager: Manager for tracking teammates
        """
        self._teammate_manager = teammate_manager or TeammateManager()
        self._subscribers: dict[str, list[Callable[[ProtocolMessage], None]]] = {}
        self._lock = threading.Lock()

    def create_request(self, to: str, action: str, params: dict) -> ProtocolMessage:
        """Create a notification message (same format as request but for events)."""
        import time

        return ProtocolMessage(
            request_id=str(uuid.uuid4()),
            action=action,
            from_="",
            to=to,
            payload=params,
            timestamp=time.time(),
            is_response=False,
        )

    def parse_response(self, raw: RawMessage) -> ProtocolMessage:
        """Notifications don't have responses, but we parse for completeness."""
        return self.parse_notification(raw)

    def parse_notification(self, raw: RawMessage) -> ProtocolMessage:
        """Parse a raw notification message."""
        try:
            data = json.loads(raw.content)
            return ProtocolMessage(
                request_id=data.get("request_id", str(uuid.uuid4())),
                action=data.get("action", ""),
                from_=raw.source,
                to=raw.destination,
                payload=data.get("payload", {}),
                timestamp=data.get("timestamp", time.time()),
                is_response=False,
            )
        except json.JSONDecodeError:
            return ProtocolMessage(
                request_id=str(uuid.uuid4()),
                action="notification",
                from_=raw.source,
                to=raw.destination,
                payload={"raw": raw.content},
                timestamp=time.time(),
                is_response=False,
            )

    def send_notification(
        self, to: str, event: str, data: dict, from_: str = ""
    ) -> None:
        """
        Send a notification to a recipient.

        Args:
            to: The recipient identifier
            event: The event type name
            data: Event data payload
            from_: The sender identifier
        """
        message = self.create_request(to, event, data)

        # In a real implementation, this would send over a transport
        # For now, we just notify local subscribers if they match
        self._dispatch_to_subscribers(message)

    def broadcast_notification(
        self, event: str, data: dict, from_: str = ""
    ) -> None:
        """
        Broadcast a notification to all subscribers of an event type.

        Args:
            event: The event type name
            data: Event data payload
            from_: The sender identifier
        """
        message = self.create_request("", event, data)
        self._dispatch_to_subscribers(message)

    def subscribe(
        self, event: str, handler: Callable[[ProtocolMessage], None]
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event: The event type to subscribe to
            handler: Callback function to handle the event
        """
        with self._lock:
            if event not in self._subscribers:
                self._subscribers[event] = []
            self._subscribers[event].append(handler)

    def unsubscribe(
        self, event: str, handler: Callable[[ProtocolMessage], None]
    ) -> bool:
        """
        Unsubscribe from an event type.

        Args:
            event: The event type to unsubscribe from
            handler: The handler to remove

        Returns:
            True if the handler was found and removed
        """
        with self._lock:
            if event in self._subscribers:
                try:
                    self._subscribers[event].remove(handler)
                    return True
                except ValueError:
                    pass
            return False

    def _dispatch_to_subscribers(self, message: ProtocolMessage) -> None:
        """Dispatch a message to all subscribers of the event type."""
        with self._lock:
            handlers = self._subscribers.get(message.action, []).copy()

        for handler in handlers:
            try:
                handler(message)
            except Exception:
                # Don't let handler errors break notification dispatch
                pass

    def get_subscribed_events(self) -> list[str]:
        """Get list of events with subscribers."""
        with self._lock:
            return list(self._subscribers.keys())
