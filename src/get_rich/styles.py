from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, TypedDict, cast


class ChooserStyles(TypedDict, total=False):
    """Style configuration that users can provide to override defaults.

    All fields are optional - users only specify what they want to customize.
    """

    # Text styling
    body_style: str
    """Style for regular choice items."""

    selection_style: str
    """Style for the selected choice item."""

    selection_caret: str
    """The character(s) displayed before the selected choice."""

    header_style: str
    """Style for the header text."""

    footer_style: str
    """Style for the footer/instructions text."""

    border_style: str
    """Style for the panel border."""

    # Panel options
    show_border: bool
    """Whether to display the panel border."""

    # Table options
    option_padding: tuple[int, int] | tuple[int, int, int, int]
    """Padding for table cells. Can be (vertical, horizontal) or (top, right, bottom, left)."""

    scroll_indicator_style: str
    """Style for the scroll indicator arrows."""

    scroll_indicator_up: str
    """Character(s) for the scroll up indicator."""

    scroll_indicator_down: str
    """Character(s) for the scroll down indicator."""

    filter_style: str
    """Style for the filter input line (FilterChooser only)."""

    filter_cursor: str
    """Cursor/indicator for filter input (FilterChooser only)."""

    shortcut_prefix_style: str
    """Style for shortcut number prefixes (ShortcutChooser in auto mode only)."""

    full_path_style: str
    """Style for displaying full file paths in choices when applicable (FileChooser only)."""

    error_style: str
    """Style for validation error overlay messages."""


@dataclass
class _ChooserStyles:
    body_style: str = ""
    selection_style: str = "bold white on grey30"
    selection_caret: str = "▶"
    header_style: str = "bold"
    footer_style: str = "grey70"
    border_style: str = "grey70"
    show_border: bool = True
    option_padding: tuple[int, int] | tuple[int, int, int, int] = (0, 0)
    filter_style: str = "cyan"
    filter_cursor: str = "[blink2 bright_white bold underline]_[/]"
    scroll_indicator_style: str = "grey50"
    scroll_indicator_up: str = "··· ▲ ···"
    scroll_indicator_down: str = "··· ▼ ···"
    shortcut_prefix_style: str = "grey70"
    full_path_style: str = "grey70"
    checkbox_checked: str = "☒"
    checkbox_unchecked: str = "☐"
    error_style: str = "bright_white on dark_red"


def _merge_styles(
    user_styles: ChooserStyles | dict[str, Any] | None = None,
) -> _ChooserStyles:
    """Merge user styles with defaults."""
    if user_styles:
        defaults_dict = asdict(_ChooserStyles())
        user_dict = cast(dict[str, Any], user_styles)
        # Only update with keys that are in defaults
        for key in defaults_dict:
            if key in user_dict:
                defaults_dict[key] = user_dict[key]
        return _ChooserStyles(**defaults_dict)
    return _ChooserStyles()


# Preset style themes for easy customization
OCEAN_BLUE: ChooserStyles = {
    "body_style": "white on blue3",
    "selection_style": "bold black on bright_cyan",
    "header_style": "bold bright_cyan",
    "footer_style": "bright_blue",
    "border_style": "blue",
    "filter_style": "bright_cyan",
    "filter_cursor": "[blink2 bright_white bold underline]_[/]",
}

FOREST_GREEN: ChooserStyles = {
    "body_style": "white on dark_green",
    "selection_style": "bold black on bright_green",
    "header_style": "bold bright_green",
    "footer_style": "bright_green",
    "border_style": "green",
    "filter_style": "bright_green",
    "filter_cursor": "[blink2 bright_white bold underline]_[/]",
}

SUNSET_ORANGE: ChooserStyles = {
    "body_style": "bright_white on orange4",
    "selection_style": "bold black on bright_yellow",
    "selection_caret": "☀",
    "header_style": "bold bright_yellow",
    "footer_style": "bright_yellow",
    "border_style": "bright_yellow",
    "filter_style": "bright_yellow",
    "filter_cursor": "[blink2 black bold underline]_[/]",
}

PURPLE_HAZE: ChooserStyles = {
    "body_style": "plum1 on purple4",
    "selection_style": "bold black on plum2",
    "header_style": "bold plum3",
    "footer_style": "plum3",
    "border_style": "plum3",
    "filter_style": "plum3",
    "filter_cursor": "[blink2 bright_white bold underline]_[/]",
}

CYBERPUNK: ChooserStyles = {
    "body_style": "bright_cyan on grey11",
    "selection_style": "bold black on bright_magenta",
    "header_style": "bold bright_magenta",
    "footer_style": "bright_cyan",
    "border_style": "bright_magenta",
    "filter_style": "bold bright_magenta",
    "filter_cursor": "[blink2 bright_yellow bold underline]▌[/]",
}

MATRIX: ChooserStyles = {
    "body_style": "green on black",
    "selection_style": "bold black on bright_green",
    "selection_caret": "►",
    "header_style": "bold bright_green",
    "footer_style": "green",
    "border_style": "bright_green",
    "filter_style": "bold bright_green",
    "filter_cursor": "[blink2 bright_green bold]▌[/]",
}

BUBBLEGUM: ChooserStyles = {
    "body_style": "black on bright_magenta",
    "selection_style": "bold bright_magenta on bright_white",
    "selection_caret": "★",
    "header_style": "bold bright_white",
    "footer_style": "bright_white",
    "border_style": "bright_white",
    "filter_style": "bold bright_white",
    "filter_cursor": "[blink2 bright_magenta bold underline]_[/]",
}

TERMINAL_CLASSIC: ChooserStyles = {
    "body_style": "bright_green on black",
    "selection_style": "reverse",
    "selection_caret": ">",
    "header_style": "bold bright_white",
    "footer_style": "bright_green",
    "border_style": "bright_green",
    "filter_style": "bright_green",
    "filter_cursor": "[blink2 bright_white bold]_[/]",
}

MIDNIGHT_BLUE: ChooserStyles = {
    "body_style": "bright_white on blue3",
    "selection_style": "bold blue3 on bright_white",
    "header_style": "bold bright_white",
    "footer_style": "light_steel_blue1",
    "border_style": "light_steel_blue1",
    "filter_style": "bold light_steel_blue",
    "filter_cursor": "[blink2 bright_white bold underline]_[/]",
}

CREAMSICLE: ChooserStyles = {
    "body_style": "black on bright_yellow",
    "selection_style": "bold bright_yellow on red",
    "selection_caret": "►",
    "header_style": "bold red",
    "footer_style": "yellow",
    "border_style": "red",
    "filter_style": "bold red",
    "filter_cursor": "[blink2 red bold underline]_[/]",
}
