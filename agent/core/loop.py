"""s01: The Agent Loop - Core kernel with while loop + single tool execution."""

import asyncio
import time
import json
import re
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

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

    TODO_TOOLS = {"todo_add", "todo_list", "todo_done", "todo_start"}

    def __init__(
        self,
        tools: list[Tool],
        model: str = "llama3.2",
        system_prompt: Optional[str] = None,
        max_iterations: int = 100,
        llm_client: Optional[Any] = None,
        todo_manager: Optional[Any] = None,
        skill_loader: Optional[Any] = None,
        compression_manager: Optional[Any] = None,
    ):
        self.tools = {t.name: t for t in tools}
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful assistant with access to tools."
        self.max_iterations = max_iterations
        self.messages: list[Message] = []
        self._iteration_count = 0
        self._llm_client = llm_client
        self._todo_manager = todo_manager
        self._skill_loader = skill_loader
        self._compression_manager = compression_manager

    def set_llm_client(self, client) -> None:
        """Set the LLM client for API calls."""
        self._llm_client = client

    def _build_skill_context(self) -> str:
        """
        Build Layer 1 context: skill names and short descriptions (~100 tokens/skill).

        This implements the two-layer skill injection:
        - Layer 1: Names + descriptions in system prompt
        - Layer 2: Full content loaded via load_skill tool
        """
        if not self._skill_loader:
            return ""
        skills = self._skill_loader.list_skills()
        if not skills:
            return ""
        lines = ["\n## Available Skills:"]
        for name in skills:
            skill = self._skill_loader.get_skill(name)
            if skill:
                lines.append(f"- {name}: {skill.description}")
        lines.append("\nUse the 'load_skill' tool to load a skill's full instructions when needed.")
        return "\n".join(lines)

    async def run(self, initial_message: str) -> str:
        """Run the agent with an initial message."""
        self.messages = []
        self._iteration_count = 0

        # Add system prompt
        self.messages.append(Message(role="system", content=self.system_prompt))

        # Add user message
        self.messages.append(Message(role="user", content=initial_message))

        # Main loop - execute steps until done
        all_messages = []
        while self._iteration_count < self.max_iterations:
            response = await self.step()
            all_messages.append(response.message)

            if response.done:
                break

        return "\n\n".join(all_messages)

    async def run_stream(self, initial_message: str) -> AsyncIterator[str]:
        """
        Run the agent with streaming output.

        Yields text chunks as they become available from the LLM.
        For tool calls, yields the tool execution result instead.
        """
        self.messages = []
        self._iteration_count = 0

        # Add system prompt
        self.messages.append(Message(role="system", content=self.system_prompt))

        # Add user message
        self.messages.append(Message(role="user", content=initial_message))

        # Main loop - execute steps until done
        while self._iteration_count < self.max_iterations:
            async for chunk in self._step_stream():
                yield chunk

            # Check if done after iteration
            if self.messages and self.messages[-1].role == "assistant":
                last_msg = self.messages[-1]
                # If last assistant message has no tool calls, we're done
                if not last_msg.tool_calls:
                    break

    async def _step_stream(self) -> AsyncIterator[str]:
        """
        Execute one step with streaming LLM output.

        Yields text chunks as they arrive from the LLM.
        """
        self._iteration_count += 1

        if not self.messages:
            yield "No messages."
            return

        tool_descriptions = self._build_tool_descriptions()

        if self._llm_client:
            async for chunk in self._llm_step_stream(tool_descriptions):
                yield chunk
            return

        # Fallback: simulate response
        last_msg = self.messages[-1]
        if last_msg.role == "user":
            response_text = f"Echo: {last_msg.content} (No LLM configured)"
            self.messages.append(Message(role="assistant", content=response_text))
            yield response_text
            return

        self.messages.append(Message(role="assistant", content="Conversation complete."))
        yield "Conversation complete."

    async def _llm_step_stream(self, tool_descriptions: str) -> AsyncIterator[str]:
        """
        Execute a step using the LLM client with streaming output.

        Yields text chunks as they arrive. For tool calls, yields execution result.
        """
        try:
            messages_for_llm = self.messages.copy()

            system_with_tools = f"{self.system_prompt}\n\n## Available Tools:\n{tool_descriptions}\n\n## Instructions:\n- If you need to use a tool, respond with a JSON object: {{\"tool\": \"tool_name\", \"args\": {{\"arg1\": \"value1\"}}}}\n- If no tool is needed, just respond directly."

            if self._todo_manager and self._todo_manager.should_nag():
                nag_msg = self._todo_manager.get_nag_message()
                system_with_tools = f"{system_with_tools}\n\n{nag_msg}"

            skill_context = self._build_skill_context()
            if skill_context:
                system_with_tools = f"{system_with_tools}{skill_context}"

            messages_for_llm[0] = Message(role="system", content=system_with_tools)
            messages_dicts = [self._message_to_dict(m) for m in messages_for_llm]

            # Call LLM with streaming
            result = await self._llm_client.chat(messages_dicts, stream=True)

            # Collect streaming response while yielding chunks
            response_text = ""
            async for chunk in result:
                response_text += chunk
                yield chunk

            # Check if LLM wants to call a tool (only after full response)
            tool_calls = self._parse_tool_calls(response_text)

            if tool_calls:
                all_results = []
                for tool_call in tool_calls:
                    result = self.execute_tool(tool_call)
                    all_results.append((tool_call, result))

                self.messages.append(Message(
                    role="assistant",
                    content=response_text,
                    tool_calls=tool_calls,
                ))

                for tool_call, result in all_results:
                    self.messages.append(Message(
                        role="tool",
                        content=result.output if not result.error else f"Error: {result.error}",
                        tool_call_id=tool_call.id,
                    ))

                if self._todo_manager:
                    self._todo_manager._rounds_since_todo = 0

                if self._compression_manager:
                    self.messages = self._compression_manager.compress_if_needed(self.messages)

                result_messages = []
                for tool_call, result in all_results:
                    msg = f"[Tool {tool_call.name} executed]\n{result.output}"
                    result_messages.append(msg)
                    yield msg
            else:
                self.messages.append(Message(role="assistant", content=response_text))

                if self._todo_manager:
                    self._todo_manager.increment_round()

                if self._compression_manager:
                    self.messages = self._compression_manager.compress_if_needed(self.messages)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield error_msg

    async def step(self) -> AgentResponse:
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
            return await self._llm_step(tool_descriptions)

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

    async def _llm_step(self, tool_descriptions: str) -> AgentResponse:
        """Execute a step using the LLM client (DeepSeek)."""
        try:
            # Build the prompt with tool context
            messages_for_llm = self.messages.copy()

            # Build base system message with tools
            system_with_tools = f"{self.system_prompt}\n\n## Available Tools:\n{tool_descriptions}\n\n## Instructions:\n- If you need to use a tool, respond with a JSON object: {{\"tool\": \"tool_name\", \"args\": {{\"arg1\": \"value1\"}}}}\n- If no tool is needed, just respond directly.\n- IMPORTANT: Use the 'write' tool to create or modify files, NOT bash commands like 'echo' or output redirection."

            # Inject nag reminder if threshold reached (s03: TodoWrite)
            if self._todo_manager and self._todo_manager.should_nag():
                nag_msg = self._todo_manager.get_nag_message()
                system_with_tools = f"{system_with_tools}\n\n{nag_msg}"

            # Inject skill context (s05: Layer 1 - names and descriptions only)
            skill_context = self._build_skill_context()
            if skill_context:
                system_with_tools = f"{system_with_tools}{skill_context}"

            # Update system message
            messages_for_llm[0] = Message(role="system", content=system_with_tools)

            # Convert Message objects to dicts for LLM API
            messages_dicts = [self._message_to_dict(m) for m in messages_for_llm]

            # Call LLM (non-blocking async call)
            result = await self._llm_client.chat(messages_dicts)

            # Check if result is streaming iterator or full text
            if hasattr(result, '__aiter__'):
                # It's a streaming iterator - collect all chunks
                chunks = []
                async for chunk in result:
                    chunks.append(chunk)
                response_text = ''.join(chunks)
            else:
                response_text = result

            # Check if LLM wants to call a tool
            tool_calls = self._parse_tool_calls(response_text)

            # Track if any todo tool was used
            todo_tool_used = any(tc.name in self.TODO_TOOLS for tc in tool_calls) if tool_calls else False

            if tool_calls:
                # Execute all tool calls
                all_results = []
                for tool_call in tool_calls:
                    result = self.execute_tool(tool_call)
                    all_results.append((tool_call, result))

                # Add assistant message with tool calls FIRST (required by API)
                self.messages.append(Message(
                    role="assistant",
                    content=response_text,
                    tool_calls=tool_calls,
                ))

                # Then add tool result messages
                for tool_call, result in all_results:
                    self.messages.append(Message(
                        role="tool",
                        content=result.output if not result.error else f"Error: {result.error}",
                        tool_call_id=tool_call.id,
                    ))

                # Update nag counter (todo tool used, reset counter)
                if self._todo_manager:
                    self._todo_manager._rounds_since_todo = 0

                # Apply compression if enabled (s06: Compact)
                if self._compression_manager:
                    self.messages = self._compression_manager.compress_if_needed(self.messages)

                # Build result message
                result_messages = []
                for tool_call, result in all_results:
                    result_messages.append(f"[Tool {tool_call.name} executed]\n{result.output}")

                return AgentResponse(
                    message="\n\n".join(result_messages),
                    tool_calls=tool_calls,
                    done=False,
                )
            else:
                # No tool call, just respond
                self.messages.append(Message(role="assistant", content=response_text))

                # Update nag counter (no todo tool, increment)
                if self._todo_manager:
                    self._todo_manager.increment_round()

                # Apply compression if enabled (s06: Compact)
                if self._compression_manager:
                    self.messages = self._compression_manager.compress_if_needed(self.messages)

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

    def _parse_tool_calls(self, response: str) -> list[ToolCall]:
        """Parse all tool calls from LLM response."""
        import re
        import uuid
        tool_calls = []

        # Strategy 1: Try to find JSON in markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*\})', response, re.DOTALL)
        if code_block_match:
            try:
                data = json.loads(code_block_match.group(1))
                if "tool" in data and "args" in data:
                    tool_calls.append(ToolCall(
                        id=str(uuid.uuid4())[:8],
                        name=data["tool"],
                        arguments=data["args"],
                    ))
                    return tool_calls  # Found in code block, return immediately
            except json.JSONDecodeError:
                pass

        # Strategy 2: Robust JSON extraction - find {" or [{ and parse progressively
        # This handles nested braces correctly by using json.loads instead of regex
        for start_idx in re.finditer(r'\{', response):
            start = start_idx.start()
            # Try parsing from this position with increasing lengths
            for end_offset in range(10, len(response) - start + 1):
                try:
                    candidate = response[start:start + end_offset]
                    data = json.loads(candidate)
                    if "tool" in data and "args" in data:
                        tool_calls.append(ToolCall(
                            id=str(uuid.uuid4())[:8],
                            name=data["tool"],
                            arguments=data["args"],
                        ))
                        return tool_calls
                except json.JSONDecodeError:
                    # Not valid JSON yet, continue trying
                    continue

        return tool_calls

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
        if msg.tool_call_id:
            d["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    }
                }
                for tc in msg.tool_calls
            ]
        return d
