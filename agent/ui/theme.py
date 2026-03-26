"""Theme configuration for LOOM CLI terminal UI."""

from rich.theme import Theme
from rich.style import Style

# Color scheme - Catppuccin Mocha inspired
COLORS = {
    "bg": "#1e1e2e",           # Main background (dark gray)
    "panel_bg": "#181825",     # Panel background (darker)
    "surface": "#313244",      # Elevated surfaces
    "accent": "#89b4fa",      # Soft blue (accent/focus)
    "accent_dim": "#74c7ec",   # Dimmed accent
    "user_msg": "#f5c2e7",    # Pink (user messages)
    "ai_msg": "#cdd6f4",      # Light gray (AI messages)
    "text": "#bac2de",        # Default text
    "text_muted": "#6c7086",  # Muted/secondary text
    "success": "#a6e3a1",     # Green (success)
    "warning": "#f9e2af",     # Yellow (warning)
    "error": "#f38ba8",       # Red (error)
    "code_bg": "#11111b",     # Code block background
    "border": "#45475a",      # Border color
    "border_focus": "#89b4fa", # Focus border color
}

# Custom Theme for Rich
LOOM_THEME = Theme({
    # Backgrounds
    "bg": COLORS["bg"],
    "panel": COLORS["panel_bg"],
    "surface": COLORS["surface"],
    "code_bg": COLORS["code_bg"],

    # Text colors
    "text": COLORS["text"],
    "text.muted": COLORS["text_muted"],
    "user": COLORS["user_msg"],
    "ai": COLORS["ai_msg"],

    # Accent colors
    "accent": COLORS["accent"],
    "accent.dim": COLORS["accent_dim"],
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["error"],

    # Borders
    "border": COLORS["border"],
    "border.focus": COLORS["border_focus"],

    # Special
    "prompt": COLORS["accent"],
    "tool_call": COLORS["warning"],
    "header.title": COLORS["accent"] + " bold",
    "header.subtitle": COLORS["text_muted"],
})


# Styles
STYLES = {
    "header_panel": "border=" + COLORS["border"],
    "input_panel": "border=" + COLORS["border"],
    "input_panel_focused": "border=" + COLORS["border_focus"],
    "user_bubble": "fg=" + COLORS["user_msg"],
    "ai_bubble": "fg=" + COLORS["ai_msg"],
    "code_block": "fg=" + COLORS["ai_msg"] + " bg=" + COLORS["code_bg"],
    "tool_call": "fg=" + COLORS["warning"] + " italic",
    "error": "fg=" + COLORS["error"],
    "success": "fg=" + COLORS["success"],
    "muted": "fg=" + COLORS["text_muted"],
    "accent": "fg=" + COLORS["accent"],
}


def get_focused_input_style():
    """Return Style for focused input border."""
    return Style(border_color=COLORS["border_focus"])


def get_default_input_style():
    """Return Style for default input border."""
    return Style(border_color=COLORS["border"])
