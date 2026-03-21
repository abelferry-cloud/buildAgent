"""Default configuration for the AI Agent."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentConfig:
    """Main configuration for the AI Agent."""

    # Model settings
    model: str = "deepseek-chat"
    api_base: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    provider: str = "deepseek"  # "deepseek", "anthropic", "ollama"

    # Execution settings
    max_iterations: int = 100
    timeout_seconds: float = 300.0
    idle_timeout_seconds: float = 60.0

    # Compression settings (s06)
    micro_compact_threshold: int = 100
    auto_compact_interval: int = 50
    archive_after_messages: int = 100

    # Storage settings
    state_dir: str = ".agent/state"
    mailbox_dir: str = ".agent/mailbox"
    worktree_base: str = ".agent/worktrees"
    event_stream_file: str = ".agent/events.jsonl"

    # Tool settings
    builtin_tool_dir: str = "agent/tools/builtin"
    skill_dir: str = "agent/skills"

    # Team settings (s09-s10)
    team_id: str = "main"
    request_timeout: float = 30.0
    notification_enabled: bool = True

    # Autonomous settings (s11)
    self_correct_enabled: bool = True
    max_retries: int = 3

    # Worktree settings (s12)
    git_repo: str = "."
    max_worktrees: int = 10
