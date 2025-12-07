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
    table_padding: tuple[int, int] | tuple[int, int, int, int]
    """Padding for table cells. Can be (vertical, horizontal) or (top, right, bottom, left)."""

    inner_padding: bool
    """Whether to pad the table edges (pad_edge for Table)."""

    filter_style: str
    """Style for the filter input line (FilterChooser only)."""

    filter_cursor: str
    """Cursor/indicator for filter input (FilterChooser only)."""

    shortcut_prefix_style: str
    """Style for shortcut number prefixes (ShortcutChooser in auto mode only)."""

    full_path_style: str
    """Style for displaying full file paths in choices when applicable (FileChooser only)."""


@dataclass
class _ChooserStyles:
    body_style: str = ""
    selection_style: str = "bold white on grey30"
    selection_caret: str = "▶"
    header_style: str = "bold"
    footer_style: str = "grey70"
    border_style: str = "grey70"
    show_border: bool = True
    table_padding: tuple[int, int] | tuple[int, int, int, int] = (0, 0)
    inner_padding: bool = False
    filter_style: str = "cyan"
    filter_cursor: str = "[blink2 bright_white bold underline]_[/]"
    shortcut_prefix_style: str = "grey70"
    full_path_style: str = "grey70"

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
