"""Protocol definitions."""

# Base classes are defined here
from agent.protocols.base import Protocol, ProtocolMessage, RawMessage

# Re-export core protocols lazily to avoid circular imports
# Use __getattr__ for lazy importing from agent.core.protocols
def __getattr__(name):
    if name in (
        "RequestResponseProtocol",
        "NotificationProtocol",
        "RequestFuture",
        "TeammateManager",
        "ProtocolManager",
        "ShutdownRequest",
        "PlanApprovalRequest",
    ):
        import agent.core.protocols as core_protocols

        return getattr(core_protocols, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Protocol",
    "ProtocolMessage",
    "RawMessage",
    "RequestResponseProtocol",
    "NotificationProtocol",
    "RequestFuture",
    "TeammateManager",
    "ProtocolManager",
    "ShutdownRequest",
    "PlanApprovalRequest",
]
