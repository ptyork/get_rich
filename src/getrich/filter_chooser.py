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
        height: int = 10,
        width: int | None = None,
        selected_index: int | None = None,
        selected_value: str | None = None,
        keybindings: dict[str, Sequence[str]] | None = None,
        wrap_navigation: bool = True,
        styles: ChooserStyles | dict[str, Any] | None = None,
        messages: ChooserMessages | dict[str, Any] | None = None,
        disable_filtering: bool = False,
        console: Console | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[tuple[str, int] | None], None] | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        on_confirm: Callable[[str, int], bool] | None = None,
        should_exit: Callable[[], bool] | None = None,
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
            height=height,
            width=width,
            selected_index=selected_index,
            selected_value=selected_value,
            keybindings=keybindings,
            wrap_navigation=wrap_navigation,
            styles=styles,
            messages=messages,
            console=console,
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
        return self.filtered_choices

    def _prepare_choices(self) -> None:
        """Prepare choices for display by filtering them."""
        self._filter_choices()

    def _filter_choices(self) -> None:
        """Apply current filter to choices."""
        # If filtering is disabled or no filter text, show all choices
        if self.disable_filtering or not self.filter_text:
            self.filtered_choices = [
                Chooser.Choice(i, self.choices[i]) for i in range(len(self.choices))
            ]
        else:
            # Apply text filter
            filter_lower = self.filter_text.lower()
            self.filtered_choices = [
                Chooser.Choice(i, choice)
                for i, choice in enumerate(self.choices)
                if filter_lower in choice.plain.lower()
            ]
        self._adjust_to_selection()

    def _render_header(self, table: Table) -> None:
        """Render filter line."""
        if not self.disable_filtering:
            cursor = Text.from_markup(self.styles.filter_cursor)
            filter_label = Text.from_markup(self.messages.filter_label)
            filter_display = Text.assemble(filter_label, self.filter_text, cursor)
            table.add_row(filter_display, style=self.styles.filter_style)

    def _render_footer(
        self, table: Table, display_choices: list[Chooser.Choice]
    ) -> None:
        """Render count text with filter information and navigation instructions."""
        if self.disable_filtering:
            # When filtering disabled, use simple footer
            super()._render_footer(table, display_choices)
        else:
            # When filtering enabled, show count and filter info
            count_text = self.messages.items_count.format(count=len(display_choices))
            if len(display_choices) != len(self.choices):
                count_text += f" ({self.messages.filtered_from} {len(self.choices)})"
            footer = f"{count_text} • {self.messages.instructions}"
            table.add_row(footer, style=self.styles.footer_style)

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
