from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import Chooser
from .key_reader import KeyReader
from .styles import ChooserStyles
from .messages import ChooserMessages


class FilterChooser(Chooser):
    """A scrollable, filterable inline chooser widget using Rich."""

    def __init__(
        self,
        *,
        choices: Iterable[str],
        title_text: str = "",
        header_text: str = "",
        header_location: str = "inside_top",
        height: int | None = None,
        max_height: int | None = None,
        width: int | None = None,
        selected_index: int | None = None,
        selected_value: str | None = None,
        keybindings: dict[str, Sequence[str]] | None = None,
        wrap_navigation: bool = True,
        styles: ChooserStyles | dict[str, Any] | None = None,
        messages: ChooserMessages | dict[str, Any] | None = None,
        disable_filtering: bool = False,
        console: Console | None = None,
        transient: bool = True,
        reader: KeyReader | None = None,
        before_run: Callable[["FilterChooser"], None] | None = None,
        after_run: Callable[["FilterChooser"], None] | None = None,
        on_change: Callable[["FilterChooser"], None] | None = None,
        on_key: Callable[[str, "FilterChooser"], str | None] | None = None,
        on_confirm: Callable[["FilterChooser"], bool] | None = None,
        should_exit: Callable[["FilterChooser"], bool] | None = None,
    ) -> None:
        """
        Initialize a FilterChooser.

        Args:
            disable_filtering (bool):
                If True, disables filtering functionality (default: False).
        """
        self.disable_filtering: bool = disable_filtering
        self.filter_text: str = ""
        self.filtered_choices: list[Chooser.Choice] = []

        super().__init__(
            choices=choices,
            title_text=title_text,
            header_text=header_text,
            header_location=header_location,
            height=height,
            max_height=max_height,
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
            on_confirm=on_confirm,
            should_exit=should_exit,
        )

    def _get_display_choices(self) -> list[Chooser.Choice]:
        """Get the filtered list of choices to display."""
        # Update is_highlighted for filtered choices
        for choice in self.filtered_choices:
            choice.is_highlighted = (choice.index == self.selected_index)
        return self.filtered_choices

    def _prepare_choices(self) -> None:
        """Prepare choices for display by filtering them."""
        self._filter_choices()

    def _filter_choices(self) -> None:
        """Apply current filter to choices."""
        # If filtering is disabled or no filter text, show all choices
        if self.disable_filtering or not self.filter_text:
            self.filtered_choices = self.all_choices
        else:
            # Apply text filter
            filter_lower = self.filter_text.lower()
            self.filtered_choices = [
                choice for choice in self.all_choices
                if filter_lower in choice.value.plain.lower()
            ]
        self._adjust_to_selection()

    def _render_header(self, table: Table) -> None:
        """Render filter line with count right-aligned."""
        if not self.disable_filtering:
            display_choices = self._get_display_choices()
            total_items = len(self.all_choices)
            displayed_items = len(display_choices)
            count_text = f"({displayed_items}/{total_items})"
            
            cursor = Text.from_markup(self.styles.filter_cursor)
            filter_label = Text.from_markup(self.messages.filter_label)
            filter_display = Text.assemble(filter_label, self.filter_text, cursor)
            
            # Create a table to right-align the count
            header_table = Table.grid(expand=True)
            header_table.add_column(ratio=1)
            header_table.add_column(justify="right", width=len(count_text) + 1)
            header_table.add_row(filter_display, count_text)
            
            table.add_row(header_table, style=self.styles.filter_style)

    def _handle_other_key(self, key: str) -> None:
        """Handle backspace and printable keys for filtering."""
        if self.disable_filtering:
            # When filtering disabled, don't handle filter keys
            return super()._handle_other_key(key)

        elif key in self.keybindings.get("backspace", []):
            if self.filter_text:
                self.filter_text = self.filter_text[:-1]
                self._filter_choices()
        elif key == "SPACE":
            # Special handling for space key
            self.filter_text += " "
            self._filter_choices()
        elif len(key) == 1 and key.isprintable():
            self.filter_text += key
            self._filter_choices()

        return False
