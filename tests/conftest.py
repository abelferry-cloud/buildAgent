"""Shared fixtures for tests."""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_llm_client():
    """Mock LLM client that returns simple responses."""
    class MockLLMClient:
        def __init__(self):
            self.call_count = 0

        async def chat(self, messages):
            self.call_count += 1
            # Return a simple tool call response
            return '{"tool": "bash", "args": {"command": "echo test"}}'

    return MockLLMClient()


@pytest.fixture
def mock_llm_client_no_tool():
    """Mock LLM client that returns text response (no tool call)."""
    class MockLLMClientNoTool:
        async def chat(self, messages):
            return "This is a simple text response without any tool call."

    return MockLLMClientNoTool()


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    from agent.core.loop import Message
    return [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello, how are you?"),
    ]
