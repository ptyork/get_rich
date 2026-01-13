"""Internationalization (i18n) configuration for Rich chooser controls."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, TypedDict, cast


class ChooserMessages(TypedDict, total=False):
    """Message strings that users can provide to override defaults.

    All fields are optional - users only specify what they want to customize.
    """

    nav_instructions: str
    """Navigation instructions for footer."""

    confirm_instructions: str
    """Confirmation instructions for footer."""

    footer_separator: str
    """Separator between footer parts."""

    # FilterChooser specific
    filter_label: str
    """Label text displayed before filter input."""

    # FilterChooser count display
    items_count: str
    """Format string for multiple items: use {count} as placeholder."""

    filtered_from: str
    """Text connecting filtered count to total count."""

    # ShortcutChooser specific
    shortcut_select_range: str
    """Label for selecting by shortcut range: use {start} and {end} as placeholders."""

    shortcut_select_key: str
    """Label for selecting by shortcut key."""

    # MultiChooser validation messages
    min_selected_error: str
    """Error message when fewer items selected than minimum."""

    max_selected_error: str
    """Error message when more items selected than maximum."""

    range_selected_error: str
    """Error message when selected count outside min/max range."""


@dataclass
class _ChooserMessages:
    nav_instructions: str = "↑↓ Navigate"
    confirm_instructions: str = "Enter Confirm"
    footer_separator: str = " • "
    filter_label: str = "Filter: "
    items_count: str = "{count} items"
    filtered_from: str = "filtered from"
    shortcut_select_range: str = "Press {start}-{end} to Select"
    shortcut_select_key: str = "Press Highlighted Key to Select"
    min_selected_error: str = "Please select at least {min} items"
    max_selected_error: str = "Please select at most {max} items"
    range_selected_error: str = "Please select between {min} and {max} items"


def _merge_messages(
    user_messages: ChooserMessages | dict[str, Any] | None = None,
) -> _ChooserMessages:
    """Merge user messages with defaults."""
    if user_messages:
        defaults_dict = asdict(_ChooserMessages())
        user_dict = cast(dict[str, Any], user_messages)
        # Only update with keys that are in defaults
        for key in defaults_dict:
            if key in user_dict:
                defaults_dict[key] = user_dict[key]
        return _ChooserMessages(**defaults_dict)
    return _ChooserMessages()
