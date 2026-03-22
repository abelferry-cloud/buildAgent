"""s02: Tools - Tests for Tool base class and DispatchMap."""

import pytest
import os
import tempfile
from agent.tools.base import Tool, ToolResult, ToolCall
from agent.core.dispatch import DispatchMap


class SimpleTool(Tool):
    """A simple tool for testing."""

    name = "simple"
    description = "A simple test tool"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_call_id=kwargs.get("_tool_call_id", ""),
            output=f"Simple tool executed with {kwargs}"
        )


class EchoTool(Tool):
    """Echo tool that returns input."""

    name = "echo"
    description = "Echoes the input back"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_call_id=kwargs.get("_tool_call_id", ""),
            output=f"Echo: {kwargs.get('message', '')}"
        )


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_tool_result_success(self):
        """Test successful tool result."""
        result = ToolResult(tool_call_id="123", output="Success!")
        assert result.tool_call_id == "123"
        assert result.output == "Success!"
        assert result.error is None

    def test_tool_result_with_error(self):
        """Test tool result with error."""
        result = ToolResult(tool_call_id="123", output="", error="Something went wrong")
        assert result.error == "Something went wrong"

    def test_tool_result_with_metadata(self):
        """Test tool result with metadata."""
        result = ToolResult(
            tool_call_id="123",
            output="Done",
            metadata={"duration": 0.5}
        )
        assert result.metadata == {"duration": 0.5}


class TestToolCall:
    """Tests for ToolCall dataclass."""

    def test_tool_call_creation(self):
        """Test creating a tool call."""
        call = ToolCall(id="1", name="bash", arguments={"command": "ls"})
        assert call.id == "1"
        assert call.name == "bash"
        assert call.arguments == {"command": "ls"}


class TestTool:
    """Tests for the Tool base class."""

    def test_tool_to_dict(self):
        """Test tool to_dict method."""
        tool = SimpleTool()
        d = tool.to_dict()
        assert d["name"] == "simple"
        assert d["description"] == "A simple test tool"


class TestDispatchMap:
    """Tests for the DispatchMap class."""

    def test_dispatch_map_initialization(self):
        """Test DispatchMap initialization."""
        dispatch = DispatchMap()
        assert len(dispatch.list_tools()) == 0
        assert len(dispatch.list_tool_names()) == 0

    def test_register_tool(self):
        """Test registering a tool."""
        dispatch = DispatchMap()
        tool = SimpleTool()
        dispatch.register(tool)
        assert "simple" in dispatch.list_tool_names()
        assert dispatch.has_tool("simple")

    def test_get_tool(self):
        """Test getting a registered tool."""
        dispatch = DispatchMap()
        tool = SimpleTool()
        dispatch.register(tool)
        retrieved = dispatch.get_tool("simple")
        assert retrieved is tool

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        dispatch = DispatchMap()
        retrieved = dispatch.get_tool("nonexistent")
        assert retrieved is None

    def test_dispatch_success(self):
        """Test successful tool dispatch."""
        dispatch = DispatchMap()
        dispatch.register(SimpleTool())
        result = dispatch.dispatch("simple", {"_tool_call_id": "123"})
        assert result.output == "Simple tool executed with {'_tool_call_id': '123'}"
        assert result.error is None

    def test_dispatch_with_args(self):
        """Test dispatching tool with arguments."""
        dispatch = DispatchMap()
        dispatch.register(EchoTool())
        result = dispatch.dispatch("echo", {"_tool_call_id": "123", "message": "Hello"})
        assert "Echo: Hello" in result.output

    def test_dispatch_nonexistent_tool(self):
        """Test dispatching a tool that doesn't exist."""
        dispatch = DispatchMap()
        result = dispatch.dispatch("nonexistent", {"_tool_call_id": "123"})
        assert result.error is not None
        assert "not found" in result.error

    def test_dispatch_with_exception(self):
        """Test dispatching when tool raises exception."""
        class FailingTool(Tool):
            name = "failing"
            description = "A tool that fails"

            def execute(self, **kwargs) -> ToolResult:
                raise ValueError("Intentional failure")

        dispatch = DispatchMap()
        dispatch.register(FailingTool())
        result = dispatch.dispatch("failing", {"_tool_call_id": "123"})
        assert result.error == "Intentional failure"

    def test_list_tools(self):
        """Test listing all tools."""
        dispatch = DispatchMap()
        dispatch.register(SimpleTool())
        dispatch.register(EchoTool())
        tools = dispatch.list_tools()
        assert len(tools) == 2

    def test_list_tool_names(self):
        """Test listing all tool names."""
        dispatch = DispatchMap()
        dispatch.register(SimpleTool())
        dispatch.register(EchoTool())
        names = dispatch.list_tool_names()
        assert "simple" in names
        assert "echo" in names


class TestBuiltinTools:
    """
    Tests for built-in tools based on TODO prompts.

    TODO prompts:
    - Read the file requirements.txt
    - Create a file called greet.py with a greet(name) function
    - Edit greet.py to add a docstring to the function
    - Read greet.py to verify the edit worked
    """

    def test_builtin_tools_registered(self):
        """Test that built-in tools are registered in DispatchMap."""
        from agent.core.dispatch import DispatchMap
        from agent.tools.builtin.bash import BashTool
        from agent.tools.builtin.read import ReadTool
        from agent.tools.builtin.write import WriteTool
        from agent.tools.builtin.glob import GlobTool

        dispatch = DispatchMap()
        dispatch.register(BashTool())
        dispatch.register(ReadTool())
        dispatch.register(WriteTool())
        dispatch.register(GlobTool())

        assert dispatch.has_tool("bash")
        assert dispatch.has_tool("read")
        assert dispatch.has_tool("write")
        assert dispatch.has_tool("glob")

    def test_read_tool_functionality(self):
        """Test ReadTool can read a file."""
        from agent.tools.builtin.read import ReadTool

        # Create a temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            tool = ReadTool()
            result = tool.execute(path=temp_path)
            assert "Hello, World!" in result.output
        finally:
            os.unlink(temp_path)

    def test_write_tool_functionality(self, tmp_path):
        """Test WriteTool can create a file."""
        from agent.tools.builtin.write import WriteTool

        file_path = str(tmp_path / "greet.py")
        content = 'def greet(name):\n    return f"Hello, {name}!"'

        tool = WriteTool()
        result = tool.execute(path=file_path, content=content)

        # Check file was created
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            assert "def greet(name)" in f.read()

    def test_glob_tool_functionality(self, tmp_path):
        """Test GlobTool can find files."""
        from agent.tools.builtin.glob import GlobTool

        # Create some Python files
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "file3.txt").touch()

        tool = GlobTool()
        # Use 'path' parameter instead of 'root_dir'
        result = tool.execute(pattern="*.py", path=str(tmp_path))
        assert "file1.py" in result.output
        assert "file2.py" in result.output
