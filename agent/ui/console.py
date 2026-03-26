"""Main console class for LOOM CLI terminal interface."""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .theme import LOOM_THEME, COLORS, STYLES
from .components import Header, Message, StatusBar
from .streaming import StreamingOutput


class LoomConsole:
    """
    Main console class for LOOM CLI terminal UI.

    Integrates all UI components and manages the interactive session.
    """

    def __init__(
        self,
        version: str = "0.1.0",
        model: str = "deepseek-chat",
        tool_names: Optional[list[str]] = None,
    ):
        # Rich console with custom theme
        self.console = Console(
            theme=LOOM_THEME,
            color_system="256",
            force_terminal=True,
            record=False,
        )

        self.version = version
        self.model = model
        self.cwd = os.getcwd()
        self.tool_names = tool_names or []

        # Message history
        self.messages: list[Message] = []
        self.session_num = 1
        self.message_count = 0

        # Streaming state
        self._streaming_output = StreamingOutput(self.console)

        # Command history for simple navigation
        self._history: list[str] = []
        self._history_index: int = -1

        # Control flags
        self._should_exit = False
        self._is_streaming = False

    def _get_prompt(self) -> str:
        """Get the prompt text."""
        return "> "

    def _print_prompt(self) -> None:
        """Print the input prompt with styling."""
        prompt = Text()
        prompt.append("> ", style="bold #89b4fa")
        self.console.print(prompt, end="")

    def print_header(self) -> None:
        """Print the startup header."""
        header = Header(
            version=self.version,
            model=self.model,
            cwd=self.cwd,
        )
        self.console.print(header)

    def print_welcome(self) -> None:
        """Print welcome message."""
        self.console.print()
        welcome = Text()
        welcome.append("Welcome to ", style=COLORS["text_muted"])
        welcome.append("LOOM CLI", style=f"bold {COLORS['accent']}")
        welcome.append("! Start typing to chat. ", style=COLORS["text_muted"])
        welcome.append("/help", style=COLORS["accent"])
        welcome.append(" for commands.", style=COLORS["text_muted"])
        self.console.print(welcome)
        self.console.print()

    def _print_status(self) -> None:
        """Print status bar."""
        status = StatusBar(
            session_num=self.session_num,
            message_count=self.message_count,
        )
        self.console.print(status)

    def add_user_message(self, content: str) -> None:
        """Add a user message to history only (don't display)."""
        msg = Message(role="user", content=content)
        self.messages.append(msg)
        self.message_count += 1
        self._history.append(content)
        self._history_index = len(self._history)

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        msg = Message(role="assistant", content=content)
        self.messages.append(msg)
        self.message_count += 1
        self.console.print(msg.render())

    async def stream_assistant_message(
        self,
        async_iterator,
    ) -> str:
        """
        Add an assistant message with streaming effect.

        Args:
            async_iterator: Async iterator of text chunks from LLM

        Returns:
            Complete streamed text
        """
        self._is_streaming = True
        self._streaming_output.clear()

        # Create live display
        live = Live(
            self._streaming_output.get_renderable(),
            console=self.console,
            refresh_per_second=30,
            transient=False,
            auto_refresh=True,
        )

        # Create the message placeholder
        msg = Message(role="assistant", content="")
        self.messages.append(msg)
        self.message_count += 1

        live.start()

        try:
            async for chunk in async_iterator:
                if not self._is_streaming:
                    break
                self._streaming_output.append(chunk)
                live.update(self._streaming_output.get_renderable())
                await asyncio.sleep(0)
        finally:
            live.stop()
            self._is_streaming = False

        # Final update
        msg.content = self._streaming_output.buffer
        self.console.print(msg.render())

        return self._streaming_output.buffer

    def run(self) -> None:
        """Run the console synchronously."""
        try:
            asyncio.run(self.input_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self.console.print()
            self.console.print(f"Goodbye!", style=COLORS["accent"])

    async def input_loop(self) -> None:
        """Main input loop using standard input()."""
        self.print_header()
        self.print_welcome()

        while not self._should_exit:
            try:
                # Print styled prompt
                self._print_prompt()

                # Use standard input (no prompt_toolkit for better compatibility)
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                user_input = user_input.rstrip("\n\r")

                if not user_input.strip():
                    continue

                if user_input.lower() in ("exit", "quit"):
                    self._should_exit = True
                    continue

                # Add user message
                self.add_user_message(user_input)

            except KeyboardInterrupt:
                if self._is_streaming:
                    self._is_streaming = False
                    self.console.print()
                    self.console.print("[Interrupted]", style=COLORS["warning"])
                else:
                    self._should_exit = True
            except EOFError:
                break

    def print_separator(self) -> None:
        """Print a visual separator."""
        self.console.print()
        self.console.print("─" * self.console.width, style=COLORS["border"])
        self.console.print()
