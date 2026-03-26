"""UI components for LOOM CLI terminal interface."""

import os
from datetime import datetime
from typing import Optional

from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table

from .theme import COLORS, STYLES, get_focused_input_style, get_default_input_style

# Built-in box styles from Rich - use default (no custom box)
BOX_DEFAULT = None


# ASCII Art Logo for LOOM CLI
# ASCII Art Logo for LOOM CLI
LOOM_LOGO = r"""
   __    ____  ____  __  __
  / /   / __ \/ __ \/  \/  \
 / /___/ /_/ / /_/ / /\_/ / /
/_____/\____/\____/_/  /_/ /
^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""


class Header:
    """Startup header panel showing logo, version, model, and directory."""

    def __init__(
        self,
        version: str = "0.1.0",
        model: str = "deepseek-chat",
        cwd: Optional[str] = None,
    ):
        self.version = version
        self.model = model
        self.cwd = cwd or os.getcwd()
        self._console = Console()

    def render(self) -> Panel:
        """Render the header panel."""
        # Logo line - ASCII art logo with gradient effect
        logo = Text()
        # Top part in bright cyan
        logo.append("   __    ____  ____  __  __\n", style="bold #00d4ff")
        logo.append("  / /   / __ \\/ __ \\/  \\/  \\\n", style="bold #00bbee")
        logo.append(" / /___/ /_/ / /_/ / /\\_/ / /\n", style="bold #00aaee")
        logo.append("/_____/\\____/\\____/_/  /_/ /\n", style="bold #0099dd")
        logo.append("^^^^^^^^^^^^^^^^^^^^^^^^^^^^", style="bold #f9e2af")

        # Version below logo
        version_line = Text()
        version_line.append(f"  v{self.version}", style="muted")
        version_line.append("  -  ", style="text_muted")
        version_line.append("AI Coding Assistant", style="accent")

        # Info lines
        info = Table(box=None, show_header=False, padding=0, pad_edge=False)
        info.add_column(style="text")
        info.add_column(style="text")

        # Model info
        model_text = Text()
        model_text.append(" [AI] ", style="accent")
        model_text.append("Model: ", style="muted")
        model_text.append(self.model, style="ai")
        info.add_row(model_text)

        # Directory info
        dir_text = Text()
        dir_text.append(" [DIR] ", style="accent")
        dir_text.append("Dir: ", style="muted")
        # Shorten home directory
        display_dir = self.cwd.replace(os.path.expanduser("~"), "~")
        dir_text.append(display_dir, style="ai")
        info.add_row(dir_text)

        # Time info
        time_text = Text()
        time_text.append(" [TIME] ", style="accent")
        time_text.append("Time: ", style="muted")
        time_text.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), style="ai")
        info.add_row(time_text)

        # Welcome message
        welcome = Text()
        welcome.append("Type a message to start chatting. ", style="muted")
        welcome.append("exit", style="accent")
        welcome.append("/", style="muted")
        welcome.append("quit", style="accent")
        welcome.append(" to end session.", style="muted")
        info.add_row(welcome)

        # Combine logo and info
        content = Group(logo, version_line, "", info)

        return Panel(
            content,
            title="[header.title]LOOM CLI[/header.title]",
            subtitle="[header.subtitle]AI Coding Assistant[/header.subtitle]",
            border_style=COLORS["border"],
            style=COLORS["panel_bg"],
            padding=(1, 2),
        )

    def __rich__(self):
        """Rich renderable protocol."""
        return self.render()


class InputPanel:
    """Input panel with border that changes color on focus."""

    def __init__(self, prompt: str = ">", focused: bool = False):
        self.prompt = prompt
        self.focused = focused
        self._input_text = ""

    @property
    def border_style(self) -> Style:
        """Get border style based on focus state."""
        return get_focused_input_style() if self.focused else get_default_input_style()

    def set_focused(self, focused: bool) -> None:
        """Set focus state."""
        self.focused = focused

    def render(self) -> Panel:
        """Render the input panel."""
        prompt_text = Text()
        prompt_text.append(f" {self.prompt} ", style="prompt bold")
        prompt_text.append(self._input_text, style="text")

        # Add blinking cursor indicator
        cursor = Text("▊", style="accent" if self.focused else "muted")
        if self._input_text or self.focused:
            prompt_text.append(cursor)

        return Panel(
            prompt_text,
            border_style=self.border_style,
            style=COLORS["panel_bg"],
            padding=(0, 1),
            height=3,
        )

    def set_text(self, text: str) -> None:
        """Set input text."""
        self._input_text = text

    def __rich__(self):
        """Rich renderable protocol."""
        return self.render()


class Message:
    """A chat message (user or AI)."""

    def __init__(
        self,
        role: str,  # "user" or "assistant"
        content: str,
        timestamp: Optional[datetime] = None,
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    @property
    def is_user(self) -> bool:
        return self.role == "user"

    @property
    def is_assistant(self) -> bool:
        return self.role == "assistant"

    def _format_content(self) -> Text:
        """Format message content with syntax highlighting for code blocks."""
        content = self.content

        # Simple code block detection (```language ... ```)
        if "```" in content:
            return self._format_with_code_blocks(content)

        # Plain text
        text = Text(content, style="ai" if self.is_assistant else "user")
        return text

    def _format_with_code_blocks(self, content: str) -> Text:
        """Format content with code block highlighting."""
        result = Text()
        lines = content.split("\n")
        in_code_block = False
        code_lines = []
        code_lang = ""

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block - render it
                    if code_lines:
                        code_text = "\n".join(code_lines)
                        try:
                            syntax = Syntax(
                                code_text,
                                code_lang if code_lang else "python",
                                theme="monokai",
                                background_color=COLORS["code_bg"],
                            )
                            result.append("\n")
                            result.append(syntax)
                            result.append("\n")
                        except Exception:
                            # Fallback to plain text if highlighting fails
                            result.append(Text(code_text, style="code_bg"))
                        code_lines = []
                    code_lang = ""
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_lang = line.strip()[3:].strip()
                    # Add text before code block marker
                    line_content = line[:line.index("```")]
                    if line_content:
                        result.append(line_content, style="ai" if self.is_assistant else "user")
                continue

            if in_code_block:
                code_lines.append(line)
            else:
                if line:
                    result.append(line, style="ai" if self.is_assistant else "user")
                result.append("\n")

        return result

    def render(self) -> Group:
        """Render the message with a label."""
        label = Text()
        if self.is_user:
            label.append("You: ", style="user bold")
        else:
            label.append("Assistant: ", style="accent bold")

        content = self._format_content()

        # Wrap in a simple group without a panel
        return Group(label, content, "")


class ToolCall:
    """A tool call display."""

    def __init__(self, name: str, arguments: dict, result: Optional[str] = None):
        self.name = name
        self.arguments = arguments
        self.result = result
        self.expanded = False

    def toggle_expanded(self) -> None:
        """Toggle expanded state."""
        self.expanded = not self.expanded

    def render(self) -> Panel:
        """Render the tool call."""
        header = Text()
        header.append("[TOOL] ", style="tool_call")
        header.append(f"Tool: {self.name}", style="tool_call bold")

        if self.result:
            header.append(" ✓", style="success")

        content = Text()
        if self.arguments:
            content.append("Args: ", style="muted")
            import json
            args_str = json.dumps(self.arguments, indent=2)
            content.append(args_str, style="code_bg")

        if self.result and self.expanded:
            content.append("\n\nResult: ", style="muted")
            content.append(self.result[:500] + "..." if len(self.result) > 500 else self.result, style="ai")

        return Panel(
            content,
            title=None,
            border_style=COLORS["warning"],
            style=COLORS["panel_bg"],
            padding=(0, 1),
        )


class StatusBar:
    """Status bar showing session info."""

    def __init__(self, session_num: int = 1, message_count: int = 0):
        self.session_num = session_num
        self.message_count = message_count

    def render(self) -> Panel:
        """Render status bar."""
        content = Text()
        content.append(f"Session #{self.session_num}", style="muted")
        content.append("  •  ", style="text_muted")
        content.append(f"Messages: {self.message_count}", style="muted")
        content.append("  •  ", style="text_muted")
        content.append("Ctrl+C interrupt", style="muted")
        content.append("  •  ", style="text_muted")
        content.append("Tab complete", style="muted")

        return Panel(
            content,
            border_style=COLORS["border"],
            style=COLORS["panel_bg"],
            padding=(0, 1),
            height=2,
        )
