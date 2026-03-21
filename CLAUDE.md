# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

### Coding Guidelines

### Must-Read Files
- **PLAN.md**: Before starting any coding task, you must read `PLAN.md` to understand the project's TODO list and implementation plan
- **Official Documentation**: Refer to the 12-step learning path at https://learn.shareai.run/zh, using the official site as the primary standard
### Accessing Official Documentation
- Use **Playwright** (`mcp__plugin_playwright_*`) instead of WebSearch to access the official documentation
- Documentation URL format: `https://learn.shareai.run/zh/sXX/` (XX is the step number)

## Build and Test Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_filename.py

# Run tests with verbose output
pytest -v
```

Dependencies are listed in `pyproject.toml`. Install with:
```bash
pip install -e ".[dev]"
```

## Architecture Overview

BuildAgent is a general-purpose AI Agent following a **12-step progression** architecture. The codebase is organized around step modules (s01, s02, s04, etc.).

### Core Agent Loop (`agent/core/loop.py`)
The central `Agent` class implements a while-loop kernel:
1. Build messages for LLM
2. Call LLM to decide next action
3. Execute tool if needed
4. Return response

### Tool System (`agent/tools/`)
- **Base**: `agent/tools/base.py` defines `Tool` (ABC), `ToolCall`, `ToolResult`
- **Dispatch**: `agent/core/dispatch.py` - `DispatchMap` routes tool calls by name
- **Builtin Tools** (`agent/tools/builtin/`):
  - `bash.py`, `read.py`, `write.py`, `glob.py` - File operations
  - `task_*.py` - Task list management (create, update, list, depends)
  - `todo_*.py` - Todo management
  - `team_*.py` - Team messaging (send, broadcast, list, status)
  - `board_*.py` - Task board coordination (post, poll, claim, complete)
  - `background_*.py` - Background process management
  - `worktree_*.py` - Git worktree operations
  - `event_*.py` - Event subscription/listing
  - `spawn.py` - Subagent spawning

### Multi-Agent System
- **Subagents** (`agent/core/subagent.py`): Isolated execution with message passing via `SubagentManager`
- **Teams** (`agent/core/teams.py`): `TeammateManager` coordinates multiple agents with mailbox-based communication
- **Task Board** (`agent/core/autonomous.py`): File-based polling coordination via `TaskBoard`; `AutonomousGovernor` handles timeout/retry/escalation

### State Management (`agent/state/`)
- **Mailbox** (`state/mailbox.py`): File-based inbox/outbox using `inbox.jsonl` and `outbox.jsonl`
- **FileStore**: Generic file-based key-value storage
- **NotificationQueue**: Queue-based notification system

### Message Compression (`agent/core/compact.py`)
Three-layer system:
1. **Micro-compact**: Per-message whitespace removal
2. **Auto-compact**: Summarizes old messages at threshold
3. **Archive**: Moves old messages to file storage

### Skills (`agent/skills/loader.py`)
Runtime skill loading with hot-reload support. Skills can provide additional tools and behavior.

### Events (`agent/event/`)
- **EventEmitter**: Publish/subscribe event system
- **EventStream**: Streaming event handling

## Key Design Patterns

1. **Tool dispatch**: All tools inherit `Tool` base class, registered with `DispatchMap`
2. **Mailbox messaging**: Agents communicate via file-based inbox/outbox (JSONL)
3. **Polling coordination**: Task board uses file polling for multi-agent sync
4. **Step-based progression**: Architecture follows numbered progression steps (s01-s11)
