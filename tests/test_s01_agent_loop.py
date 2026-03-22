"""s01: Agent Loop - Tests for core kernel with while loop + single tool execution."""

import pytest
from agent.core.loop import Agent, Message, AgentResponse, ToolCall, ToolResult
from agent.tools.base import Tool


class DummyTool(Tool):
    """A dummy tool for testing."""

    name = "dummy"
    description = "A dummy tool for testing"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_call_id="test",
            output=f"Executed with args: {kwargs}"
        )


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tool_calls is None
        assert msg.tool_call_id is None

    def test_message_with_tool_calls(self):
        """Test message with tool calls."""
        tool_call = ToolCall(id="1", name="bash", arguments={"command": "ls"})
        msg = Message(role="assistant", content="Using bash", tool_calls=[tool_call])
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].name == "bash"


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_response_with_tool_calls(self):
        """Test agent response with tool calls."""
        tool_calls = [ToolCall(id="1", name="bash", arguments={"command": "ls"})]
        response = AgentResponse(
            message="Executed bash",
            tool_calls=tool_calls,
            done=False
        )
        assert response.done is False
        assert len(response.tool_calls) == 1

    def test_response_without_tool_calls(self):
        """Test agent response without tool calls."""
        response = AgentResponse(message="Hello world", tool_calls=[], done=True)
        assert response.done is True
        assert len(response.tool_calls) == 0


class TestAgent:
    """Tests for the Agent class."""

    def test_agent_initialization(self):
        """Test Agent initialization with tools."""
        tools = [DummyTool()]
        agent = Agent(tools=tools)
        assert "dummy" in agent.tools
        assert agent.model == "llama3.2"
        assert agent.max_iterations == 100
        assert len(agent.messages) == 0

    def test_agent_with_custom_config(self):
        """Test Agent initialization with custom config."""
        tools = [DummyTool()]
        agent = Agent(
            tools=tools,
            model="custom-model",
            system_prompt="Custom prompt",
            max_iterations=50
        )
        assert agent.model == "custom-model"
        assert agent.system_prompt == "Custom prompt"
        assert agent.max_iterations == 50

    def test_add_message(self):
        """Test adding messages to conversation."""
        agent = Agent(tools=[])
        agent.add_message("user", "Hello")
        assert len(agent.messages) == 1
        assert agent.messages[0].content == "Hello"

    def test_add_tool_result(self):
        """Test adding tool result messages."""
        agent = Agent(tools=[])
        agent.add_tool_result("call-123", "Tool output here")
        assert len(agent.messages) == 1
        assert agent.messages[0].role == "tool"
        assert agent.messages[0].tool_call_id == "call-123"

    def test_execute_tool(self):
        """Test tool execution via Agent."""
        tools = [DummyTool()]
        agent = Agent(tools=tools)
        tool_call = ToolCall(id="1", name="dummy", arguments={"arg1": "value1"})
        result = agent.execute_tool(tool_call)
        assert result.output == "Executed with args: {'arg1': 'value1'}"

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        agent = Agent(tools=[])
        tool_call = ToolCall(id="1", name="nonexistent", arguments={})
        result = agent.execute_tool(tool_call)
        assert result.error is not None
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_run_fallback_no_llm(self):
        """Test run() falls back correctly without LLM client."""
        agent = Agent(tools=[])
        result = await agent.run("Hello")
        assert "Echo" in result or "No LLM configured" in result

    def test_build_tool_descriptions(self):
        """Test building tool descriptions."""
        tools = [DummyTool()]
        agent = Agent(tools=tools)
        descriptions = agent._build_tool_descriptions()
        assert "dummy" in descriptions
        assert "A dummy tool for testing" in descriptions

    def test_parse_tool_calls_from_json(self):
        """Test parsing tool calls from JSON response."""
        agent = Agent(tools=[])
        response = '{"tool": "dummy", "args": {"arg1": "value1"}}'
        tool_calls = agent._parse_tool_calls(response)
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "dummy"
        assert tool_calls[0].arguments == {"arg1": "value1"}

    def test_parse_tool_calls_from_code_block(self):
        """Test parsing tool calls from markdown code block."""
        agent = Agent(tools=[])
        response = '```json\n{"tool": "dummy", "args": {"arg1": "value1"}}\n```'
        tool_calls = agent._parse_tool_calls(response)
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "dummy"

    def test_parse_tool_calls_none(self):
        """Test parsing with no tool calls."""
        agent = Agent(tools=[])
        response = "This is just a regular text response"
        tool_calls = agent._parse_tool_calls(response)
        assert len(tool_calls) == 0

    def test_message_to_dict(self):
        """Test converting Message to dict for LLM API."""
        agent = Agent(tools=[])
        msg = Message(role="user", content="Hello")
        d = agent._message_to_dict(msg)
        assert d["role"] == "user"
        assert d["content"] == "Hello"


class TestAgentIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Create a file called hello.py that prints "Hello, World!"
    - List all Python files in this directory
    - What is the current git branch?
    - Create a directory called test_output and write 3 files in it
    """

    @pytest.mark.asyncio
    async def test_run_with_messages(self):
        """Test agent run with initial messages."""
        agent = Agent(tools=[])
        agent.add_message("system", "You are a helpful assistant.")
        agent.add_message("user", "Hello")
        response = await agent.step()
        assert response is not None
        assert isinstance(response, AgentResponse)

    def test_file_creation_scenario(self):
        """Test the scenario of creating hello.py file."""
        # This tests the concept - actual file creation would use WriteTool
        agent = Agent(tools=[])
        tool_call = ToolCall(
            id="1",
            name="write",
            arguments={"path": "hello.py", "content": 'print("Hello, World!")'}
        )
        result = agent.execute_tool(tool_call)
        # WriteTool would return success/error
        assert result.tool_call_id == "1"

    def test_directory_listing_scenario(self):
        """Test the scenario of listing Python files."""
        agent = Agent(tools=[])
        tool_call = ToolCall(
            id="2",
            name="glob",
            arguments={"pattern": "*.py"}
        )
        result = agent.execute_tool(tool_call)
        assert result.tool_call_id == "2"

    def test_git_branch_scenario(self):
        """Test the scenario of checking git branch."""
        agent = Agent(tools=[])
        tool_call = ToolCall(
            id="3",
            name="bash",
            arguments={"command": "git branch --show-current"}
        )
        result = agent.execute_tool(tool_call)
        assert result.tool_call_id == "3"

    def test_multiple_file_creation_scenario(self):
        """Test creating multiple files scenario."""
        agent = Agent(tools=[])
        # First create directory
        dir_call = ToolCall(
            id="4",
            name="bash",
            arguments={"command": "mkdir test_output"}
        )
        result1 = agent.execute_tool(dir_call)

        # Then write files
        for i in range(3):
            file_call = ToolCall(
                id=f"5-{i}",
                name="write",
                arguments={"path": f"test_output/file{i}.txt", "content": f"Content {i}"}
            )
            result = agent.execute_tool(file_call)
            assert result.tool_call_id == f"5-{i}"
