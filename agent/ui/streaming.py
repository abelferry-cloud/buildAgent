"""Streaming output handler for LOOM CLI terminal UI."""

import asyncio
from typing import AsyncIterator, Callable, Optional

from rich.console import Console
from rich.live import Live
from rich.text import Text

from .theme import COLORS


class StreamingOutput:
    """Handles streaming output with typewriter effect."""

    def __init__(self, console: Console):
        self.console = console
        self._buffer = ""
        self._is_streaming = False
        self._cursor_char = "▊"

    @property
    def buffer(self) -> str:
        """Get current buffer content."""
        return self._buffer

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer = ""

    def append(self, text: str) -> None:
        """Append text to buffer."""
        self._buffer += text

    def get_renderable(self) -> Text:
        """Get current content as Text with cursor."""
        result = Text(self._buffer, style=f"ai")
        if self._is_streaming:
            result.append(f" {self._cursor_char}", style="accent blink")
        return result

    async def stream_from_asyncIterator(
        self,
        async_iterator: AsyncIterator[str],
        update_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Stream content from an async iterator (like LLM streaming).

        Args:
            async_iterator: Async iterator yielding text chunks
            update_callback: Optional callback called after each chunk

        Returns:
            Complete streamed text
        """
        self._is_streaming = True
        self._buffer = ""

        try:
            async for chunk in async_iterator:
                self._buffer += chunk
                if update_callback:
                    update_callback(chunk)
                # Small yield to allow UI updates
                await asyncio.sleep(0)
        finally:
            self._is_streaming = False

        return self._buffer

    def stream_from_sync_iterator(
        self,
        iterator: AsyncIterator[str],
        update_callback: Optional[Callable[[str], None]] = None,
    ) -> asyncio.Task:
        """
        Start streaming from a sync iterator in background.

        Args:
            iterator: Async iterator yielding text chunks
            update_callback: Optional callback called after each chunk

        Returns:
            Task that will complete when streaming is done
        """
        async def _stream():
            return await self.stream_from_asyncIterator(iterator, update_callback)

        return asyncio.create_task(_stream())


class StreamingDisplay:
    """Manages the live display of streaming content."""

    def __init__(self, console: Console, output: StreamingOutput):
        self.console = console
        self.output = output
        self._live: Optional[Live] = None

    def start(self) -> None:
        """Start the live display."""
        self._live = Live(
            self.output.get_renderable(),
            console=self.console,
            refresh_per_second=30,
            transient=False,
            auto_refresh=True,
        )
        self._live.start()

    def update(self) -> None:
        """Update the display with current buffer content."""
        if self._live:
            self._live.update(self.output.get_renderable())

    def stop(self) -> None:
        """Stop the live display."""
        if self._live:
            self._live.stop()
            self._live = None

    def refresh(self) -> None:
        """Force a refresh of the display."""
        self.update()


class TypewriterEffect:
    """Typewriter effect for smoother streaming display."""

    def __init__(self, output: StreamingOutput, chars_per_tick: int = 3):
        self.output = output
        self.chars_per_tick = chars_per_tick
        self._pending_chars = ""

    def add_chunk(self, chunk: str) -> str:
        """
        Add a chunk and return characters that should be displayed now.

        Implements a simple buffer to create smoother streaming.
        """
        self._pending_chars += chunk

        if len(self._pending_chars) >= self.chars_per_tick:
            display_chars = self._pending_chars[:self.chars_per_tick]
            self._pending_chars = self._pending_chars[self.chars_per_tick:]
            return display_chars
        return ""

    def flush(self) -> str:
        """Flush any remaining pending characters."""
        chars = self._pending_chars
        self._pending_chars = ""
        return chars
