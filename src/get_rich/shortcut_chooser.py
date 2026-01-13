from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

from rich.console import Console
from rich.table import Table

from . import Chooser
from .key_reader import KeyReader
from .styles import ChooserStyles
from .messages import ChooserMessages


class ShortcutChooser(Chooser):
    """A chooser that allows selection via keyboard shortcuts (letters/numbers)."""

    def __init__(
        self,
        *,
        choices: Iterable[str],
        title_text: str = "",
        header_text: str = "",
        header_location: str = "inside_top",
        height: int = 10,
        width: int | None = None,
        selected_index: int | None = None,
        selected_value: str | None = None,
        keybindings: dict[str, Sequence[str]] | None = None,
        wrap_navigation: bool = True,
        styles: ChooserStyles | dict[str, Any] | None = None,
        messages: ChooserMessages | dict[str, Any] | None = None,
        shortcut_keys: Sequence[str] | None = None,
        no_confirm: bool = False,
        show_shortcuts: bool = True,
        strict_mode: bool = False,
        console: Console | None = None,
        transient: bool = True,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[tuple[str, int] | None], None] | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        should_exit: Callable[[], bool] | None = None,
    ) -> None:
        """
        Initialize a ShortcutChooser.

        Args:
            shortcut_keys (Sequence[str] | None):
                Optional list of keys corresponding to each choice. If None,
                auto mode uses 1-9, 0 for choices. If provided, can be
                shorter/longer than choices list.
            no_confirm (bool):
                If True, pressing a shortcut key immediately confirms the selection.
            show_shortcuts (bool):
                If True (default), shows shortcut keys in the display.
            strict_mode (bool):
                If True, raises exceptions for misconfigured keys (duplicates,
                too few, or too many keys). If False (default), tolerates these
                conditions.
        """
        self.shortcut_keys: list[str] = []
        self.shortcut_key_to_index: dict[str, int] = {}
        self.no_confirm: bool = no_confirm
        self.show_shortcuts: bool = show_shortcuts
        self.strict_mode: bool = strict_mode
        self.auto_mode: bool = shortcut_keys is None

        # Initialize the shortcuts before calling super().__init__
        self._init_shortcuts(choices, shortcut_keys)

        super().__init__(
            choices=choices,
            title_text=title_text,
            header_text=header_text,
            header_location=header_location,
            height=height,
            width=width,
            selected_index=selected_index,
            selected_value=selected_value,
            keybindings=keybindings,
            wrap_navigation=wrap_navigation,
            styles=styles,
            messages=messages,
            console=console,
            transient=transient,
            reader=reader,
            before_run=before_run,
            after_run=after_run,
            on_change=on_change,
            on_key=on_key,
            should_exit=should_exit,
        )

    def _init_shortcuts(
        self, choices: Iterable[str], shortcut_keys: Sequence[str] | None
    ) -> None:
        """Initialize shortcut key mappings."""
        choices_list = list(choices)
        num_choices = len(choices_list)

        if shortcut_keys is None:
            # Auto mode: use 1-9, 0 for choices
            self.shortcut_keys = [str((i + 1) % 10) for i in range(num_choices)]
        else:
            shortcut_keys_list = list(shortcut_keys)

            # Check for issues
            if self.strict_mode:
                if len(shortcut_keys_list) < num_choices:
                    raise ValueError(
                        f"Too few shortcut keys: {len(shortcut_keys_list)} keys "
                        f"for {num_choices} choices"
                    )
                if len(shortcut_keys_list) > num_choices:
                    raise ValueError(
                        f"Too many shortcut keys: {len(shortcut_keys_list)} keys "
                        f"for {num_choices} choices"
                    )
                # Check for duplicates in the valid range
                valid_keys = shortcut_keys_list[:num_choices]
                if len(valid_keys) != len(set(valid_keys)):
                    raise ValueError("Duplicate shortcut keys found")

            # Use only the keys we need
            self.shortcut_keys = shortcut_keys_list[:num_choices]

        # Build the mapping from key to index
        self.shortcut_key_to_index = {}
        for i, key in enumerate(self.shortcut_keys):
            # In non-strict mode, later duplicates overwrite earlier ones
            self.shortcut_key_to_index[key] = i

    def _render_footer(
        self, table: Table, display_choices: list[Chooser.Choice]
    ) -> None:
        """Render selection and navigation instructions."""
        sel_text = ""
        if self.auto_mode:
            sel_text = self.messages.shortcut_select_range.format(
                start=1, end=len(self.shortcut_keys)
            )
            sel_text += self.messages.footer_separator
        elif self.show_shortcuts:
            sel_text = self.messages.shortcut_select_key + self.messages.footer_separator
        footer = f"{sel_text}{self.messages.nav_instructions}"
        table.add_row(footer, style="dim")

    def _get_display_choices(self) -> list[Chooser.Choice]:
        """Get the list of choices with shortcut_key populated for rendering."""
        display_choices = []
        for i in range(len(self.choices)):
            display_choices.append(
                Chooser.Choice(
                    index=i,
                    value=self.choices[i],
                    is_highlighted=(i == self.selected_index),
                    shortcut_key=self.shortcut_keys[i] if self.show_shortcuts else None
                )
            )
        return display_choices

    def _render_choice_row(self, choice: Chooser.Choice) -> tuple[Text, str]:
        """Render choice with shortcut prefix if present."""
        from rich.text import Text
        
        if choice.shortcut_key:
            # Render shortcut prefix
            prefix = f"{choice.shortcut_key}) "
            choice_text = Text.assemble(
                Text(prefix, style=self.styles.shortcut_prefix_style),
                choice.value,
            )
        else:
            choice_text = choice.value
        
        # Add caret and apply selection style if highlighted
        if choice.is_highlighted:
            caret = self.styles.selection_caret
            final_text = Text.from_markup(f"{caret} ")
            final_text.append(choice_text)
            final_text.stylize(self.styles.selection_style)
            return final_text, self.styles.body_style
        else:
            final_text = Text.from_markup("  ")
            final_text.append(choice_text)
            return final_text, self.styles.body_style

    def _handle_other_key(self, key: str) -> bool:
        """Handle shortcut keys for direct selection."""
        if key in self.shortcut_key_to_index:
            # Set the filtered index to the shortcut's target
            self.selected_filtered_index = self.shortcut_key_to_index[key]
            self._set_selected()
            if self.no_confirm:
                # Immediately confirm selection
                return True
        return False
