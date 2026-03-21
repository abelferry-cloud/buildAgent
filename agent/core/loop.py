"""s01: The Agent Loop - Core kernel with while loop + single tool execution."""

import time
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from agent.tools.base import Tool, ToolCall, ToolResult


@dataclass
class Message:
    """A message in the conversation."""

    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class AgentResponse:
    """Response from an agent step."""

    message: str
    tool_calls: list[ToolCall]
    done: bool
    error: Optional[str] = None


class Agent:
    """
    Core agent kernel: a while loop + tool execution.

    The minimal agent kernel is a while loop + one tool.
    Each iteration: think, decide tool, execute, repeat.
    """

    def __init__(
        self,
        tools: list[Tool],
        model: str = "llama3.2",
        system_prompt: Optional[str] = None,
        max_iterations: int = 100,
        llm_client: Optional[Any] = None,
    ):
        self.tools = {t.name: t for t in tools}
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful assistant with access to tools."
        self.max_iterations = max_iterations
        self.messages: list[Message] = []
        self._iteration_count = 0
        self._llm_client = llm_client

    def set_llm_client(self, client) -> None:
        """Set the LLM client for API calls."""
        self._llm_client = client

    def run(self, initial_message: str) -> str:
        """Run the agent with an initial message."""
        self.messages = []
        self._iteration_count = 0

        # Add system prompt
        self.messages.append(Message(role="system", content=self.system_prompt))

        # Add user message
        self.messages.append(Message(role="user", content=initial_message))

        # Main loop
        while self._iteration_count < self.max_iterations:
            response = self.step()
            if response.done:
                return response.message
            self._iteration_count += 1

        return "Max iterations reached."

    def step(self) -> AgentResponse:
        """
        Execute one step of the agent loop.

        1. Build messages for LLM
        2. Call LLM to decide next action
        3. Execute tool if needed
        4. Return response
        """
        self._iteration_count += 1

        if not self.messages:
            return AgentResponse(
                message="No messages.",
                tool_calls=[],
                done=True,
                error="Empty message history",
            )

        # Build tool descriptions for the LLM
        tool_descriptions = self._build_tool_descriptions()

        # If we have an LLM client, use it
        if self._llm_client:
            return self._llm_step(tool_descriptions)

        # Fallback: simulate response
        last_msg = self.messages[-1]
        if last_msg.role == "user":
            response_text = f"Echo: {last_msg.content} (No LLM configured - install Ollama and set --provider ollama)"
            self.messages.append(Message(role="assistant", content=response_text))
            return AgentResponse(
                message=response_text,
                tool_calls=[],
                done=True,
            )

        return AgentResponse(
            message="Conversation complete.",
            tool_calls=[],
            done=True,
        )

    def _llm_step(self, tool_descriptions: str) -> AgentResponse:
        """Execute a step using the LLM client (Ollama)."""
        try:
            # Build the prompt with tool context
            messages_for_llm = self.messages.copy()

            # Add tool context to system message
            system_with_tools = f"{self.system_prompt}\n\n## Available Tools:\n{tool_descriptions}\n\n## Instructions:\n- If you need to use a tool, respond with a JSON object: {{\"tool\": \"tool_name\", \"args\": {{\"arg1\": \"value1\"}}}}\n- If no tool is needed, just respond directly."

            # Update system message
            messages_for_llm[0] = Message(role="system", content=system_with_tools)

            # Convert Message objects to dicts for LLM API
            messages_dicts = [self._message_to_dict(m) for m in messages_for_llm]

            # Call LLM
            response_text = self._llm_client.chat(messages_dicts)

            # Check if LLM wants to call a tool
            tool_call = self._parse_tool_call(response_text)

            if tool_call:
                # Execute the tool
                result = self.execute_tool(tool_call)

                # Add assistant message with tool call
                self.messages.append(Message(
                    role="assistant",
                    content=response_text,
                    tool_calls=[tool_call],
                ))

                # Add tool result
                self.messages.append(Message(
                    role="tool",
                    content=result.output if not result.error else f"Error: {result.error}",
                    tool_call_id=tool_call.id,
                ))

                return AgentResponse(
                    message=f"[Tool {tool_call.name} executed]",
                    tool_calls=[tool_call],
                    done=False,
                )
            else:
                # No tool call, just respond
                self.messages.append(Message(role="assistant", content=response_text))
                return AgentResponse(
                    message=response_text,
                    tool_calls=[],
                    done=True,
                )

        except Exception as e:
            return AgentResponse(
                message=f"Error: {str(e)}",
                tool_calls=[],
                done=True,
                error=str(e),
            )

    def _build_tool_descriptions(self) -> str:
        """Build a description of all available tools."""
        if not self.tools:
            return "No tools available."

        descriptions = []
        for name, tool in self.tools.items():
            desc = f"- {name}: {tool.description}"
            descriptions.append(desc)

        return "\n".join(descriptions)

    def _parse_tool_call(self, response: str) -> Optional[ToolCall]:
        """Parse a tool call from LLM response."""
        # Try to find JSON in the response
        try:
            # Look for JSON object
            json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if "tool" in data and "args" in data:
                    import uuid
                    return ToolCall(
                        id=str(uuid.uuid4())[:8],
                        name=data["tool"],
                        arguments=data["args"],
                    )
        except (json.JSONDecodeError, KeyError):
            pass

        return None

    def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            return ToolResult(
                tool_call_id=tool_call.id,
                output="",
                error=f"Tool '{tool_call.name}' not found",
            )

        try:
            result = tool.execute(**tool_call.arguments)
            result.tool_call_id = tool_call.id
            return result
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                output="",
                error=str(e),
            )

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        """Add a tool result message."""
        self.messages.append(
            Message(role="tool", content=content, tool_call_id=tool_call_id)
        )

    def _message_to_dict(self, msg: Message) -> dict[str, Any]:
        """Convert a Message dataclass to a dict for LLM APIs."""
        d = {"role": msg.role, "content": msg.content}
        return d
