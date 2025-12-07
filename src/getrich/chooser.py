from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import BaseControl
from .key_reader import KeyReader
from .styles import ChooserStyles, _ChooserStyles, _merge_styles
from .messages import ChooserMessages, _ChooserMessages, _merge_messages


# TODO:
#   - Add support for multiple columns (automatic up to specified max_cols)
#   - Add tabular layouts using Craftable library with column defs and headers
#   - Add support for mouse input (click to select, scroll to navigate)
#   - Add support for multi-select mode (with Ctrl/Shift keys)


class Chooser(BaseControl):
    """A scrollable inline chooser widget using Rich."""

    DEFAULT_KEYBINDINGS: dict[str, Sequence[str]] = {
        "up": ["UP_ARROW"],
        "down": ["DOWN_ARROW"],
        "confirm": ["ENTER"],
        "cancel": ["ESC", "CTRL_C"],
        "home": ["HOME"],
        "end": ["END"],
        "page_up": ["PAGE_UP"],
        "page_down": ["PAGE_DOWN"],
    }

    @dataclass
    class Choice:
        index: int
        value: Text

        def __str__(self) -> str:  # pragma: no cover - simple delegator
            return str(self.value)

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
        wrap_navigation: bool = True,
        styles: ChooserStyles | dict[str, Any] | None = None,
        messages: ChooserMessages | dict[str, Any] | None = None,
        console: Console | None = None,
        keybindings: dict[str, Sequence[str]] | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[tuple[str, int] | None], None] | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        on_confirm: Callable[[str, int], bool] | None = None,
        should_exit: Callable[[], bool] | None = None,
    ) -> None:
        """
        Initialize a Chooser.

        Args:
            choices (Iterable[str]):
                List of choice strings
            title_text (str):
                Title text displayed at the top of the chooser
            header_text (str):
                Header text displayed below the title
            height (int):
                Number of visible items in the chooser
            width (int | None):
                Width of the chooser. None = auto-size to content (default),
                0 = expand to fill screen width, >0 = fixed width in columns.
            selected_index (int | None):
                Optional initial selected index
            selected_value (str | None):
                Optional initial selected value (overrides index if found)
            wrap_navigation (bool):
                If True, navigation wraps around at ends
            styles (ChooserStyles | dict[str, Any] | None):
                Optional styles overrides. See ChooserStyles for defaults.
            messages (ChooserMessages | dict[str, Any] | None):
                Optional messages overrides.
        """
        super().__init__(
            console=console,
            keybindings=keybindings,
            reader=reader,
            before_run=before_run,
            after_run=after_run,
            on_change=on_change,
            on_key=on_key,
            on_confirm=on_confirm,  # type: ignore
            should_exit=should_exit,
        )

        self.choices: list[Text] = [Text.from_markup(choice) for choice in choices]
        self.title_text: str = title_text
        self.header_text: str = header_text
        self.height: int = height
        self.width: int | None = width
        self.styles: _ChooserStyles = _merge_styles(styles)
        self.messages: _ChooserMessages = _merge_messages(messages)

        self.selected_index: int = 0
        self.selected_filtered_index: int = 0
        self.selected_value: Text | None = None
        self.on_confirm: Callable[[str, int], bool] | None = on_confirm

        self.wrap_navigation = wrap_navigation

        self._apply_initial_selection(selected_index, selected_value)
        self._prepare_choices()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_initial_selection(
        self, selected_index: int | None, selected_value: str | None
    ) -> None:
        if selected_index is not None and 0 <= selected_index < len(self.choices):
            self.selected_index = selected_index
        elif selected_value:
            for i, choice in enumerate(self.choices):
                if choice.plain.lower() == selected_value.lower():
                    self.selected_index = i
                    break
        self.selected_filtered_index = self.selected_index
        if self.choices:
            self.selected_value = self.choices[self.selected_index]

    def _get_display_choices(self) -> list[Chooser.Choice]:
        """Get the list of choices to display. Can be overridden by subclasses."""
        return [Chooser.Choice(i, self.choices[i]) for i in range(len(self.choices))]

    def _prepare_choices(self) -> None:
        """Prepare choices for display. Can be overridden by subclasses for filtering."""
        pass

    def _render(self) -> RenderableType:
        display_choices = self._get_display_choices()

        # width=0 means expand to fill screen, None means auto-size to content
        table_width = None if self.width == 0 else self.width
        expand_table = self.width == 0

        table = Table.grid(
            padding=self.styles.table_padding,
            pad_edge=self.styles.inner_padding,
            expand=expand_table,
        )
        table.add_column(width=table_width, no_wrap=True)

        # When borderless, render title as part of table if present
        if not self.styles.show_border and self.title_text:
            table.add_row(Text(self.title_text, style=self.styles.header_style, justify="center"))

        if self.header_text:
            table.add_row(Text(self.header_text, style=self.styles.header_style))

        self._render_header(table)

        max_items = self._visible_count(display_choices)
        visible_start = max(
            0, min(self.selected_filtered_index, len(display_choices) - max_items)
        )
        visible_end = visible_start + max_items

        # Show up arrow if there are hidden items above
        has_items_above = visible_start > 0
        has_items_below = visible_end < len(display_choices)

        if has_items_above:
            table.add_row(Text("  ▲ ···", style="dim"))

        for choice in display_choices[visible_start:visible_end]:
            if choice.index == self.selected_index:
                caret = self.styles.selection_caret
                table.add_row(
                    Text.from_markup(f"{caret} {choice.value.markup}", style=self.styles.selection_style)
                )
            else:
                table.add_row(Text.from_markup(f"  {choice.value.markup}", style=self.styles.body_style))

        if has_items_below:
            table.add_row(Text("  ▼ ···", style="dim"))

        self._render_footer(table, display_choices)

        # If show_border is False, return the table directly
        if not self.styles.show_border:
            return table

        # Otherwise, wrap in a Panel
        panel_kwargs: dict[str, Any] = {
            "title": self.title_text,
            "style": self.styles.body_style,
            "border_style": self.styles.border_style,
        }

        # width=0: expand to fill, width=None: auto-size, width>0: fixed width
        if self.width == 0:
            panel_kwargs["expand"] = True
        elif self.width is None:
            panel_kwargs["expand"] = False
        else:
            panel_kwargs["width"] = self.width
            panel_kwargs["expand"] = False

        return Panel(table, **panel_kwargs)

    def _render_header(self, table: Table) -> None:
        """Render header line if applicable. Can be overridden by subclasses."""
        pass

    def _render_footer(
        self, table: Table, display_choices: list[Chooser.Choice]
    ) -> None:
        """Render footer text. Can be overridden by subclasses."""
        table.add_row(self.messages.instructions, style=self.styles.footer_style)

    def _set_selected(self) -> None:
        display_choices = self._get_display_choices()
        if display_choices:
            choice = display_choices[self.selected_filtered_index]
            self.selected_index = choice.index
            self.selected_value = self.choices[self.selected_index]
        else:
            self.selected_index = 0
            self.selected_value = None
        if self.on_change:
            self.on_change()

    def _adjust_to_selection(self) -> None:
        """Adjust filtered index to match selected index. Can be overridden by subclasses."""
        display_choices = self._get_display_choices()
        filtered_indices = [choice.index for choice in display_choices]
        if self.selected_index in filtered_indices:
            self.selected_filtered_index = filtered_indices.index(self.selected_index)
        else:
            self.selected_filtered_index = 0
        self._set_selected()

    def _visible_count(
        self, display_choices: list[Chooser.Choice] | None = None
    ) -> int:
        if display_choices is None:
            display_choices = self._get_display_choices()
        return max(1, min(len(display_choices), self.height))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self, *, reader: KeyReader | None = None
    ) -> tuple[str, int] | tuple[None, None]:
        if self.before_run:
            self.before_run()

        self._prepare_choices()
        with reader or self._get_reader() as key_reader:
            with Live(
                self._render(), console=self.console, transient=True, auto_refresh=False
            ) as live:
                while True:
                    confirmed = False

                    # Check if we should exit early via custom logic
                    if self.should_exit and self.should_exit():
                        self.result = (None, None)
                        self._result_set_by_hook = True
                        break

                    key = key_reader.read_key()

                    # Allow custom on_key handler to intercept or modify the key
                    if self.on_key:
                        intercepted = self.on_key(key)
                        if intercepted is None:
                            # Handler requested to skip default processing
                            live.update(self._render())
                            live.refresh()
                            continue
                        key = intercepted

                    display_choices = self._get_display_choices()

                    if key in self.keybindings.get("up", []):
                        if self.selected_filtered_index > 0:
                            self.selected_filtered_index -= 1
                        elif self.wrap_navigation and display_choices:
                            self.selected_filtered_index = len(display_choices) - 1
                        self._set_selected()

                    elif key in self.keybindings.get("down", []):
                        if self.selected_filtered_index < len(display_choices) - 1:
                            self.selected_filtered_index += 1
                        elif self.wrap_navigation and display_choices:
                            self.selected_filtered_index = 0
                        self._set_selected()

                    elif key in self.keybindings.get("home", []):
                        self.selected_filtered_index = 0
                        self._set_selected()

                    elif key in self.keybindings.get("end", []):
                        if display_choices:
                            self.selected_filtered_index = len(display_choices) - 1
                            self._set_selected()

                    elif key in self.keybindings.get("page_up", []):
                        step = max(1, self._visible_count(display_choices) - 1)
                        self.selected_filtered_index = max(
                            0, self.selected_filtered_index - step
                        )
                        self._set_selected()

                    elif key in self.keybindings.get("page_down", []):
                        if display_choices:
                            step = max(1, self._visible_count(display_choices) - 1)
                            self.selected_filtered_index = min(
                                len(display_choices) - 1,
                                self.selected_filtered_index + step,
                            )
                            self._set_selected()

                    elif key in self.keybindings.get("confirm", []):
                        self._set_selected()
                        confirmed = True

                    elif key in self.keybindings.get("cancel", []):
                        self.selected_index = 0
                        self.selected_value = None
                        break

                    else:
                        confirmed = self._handle_other_key(key)

                    if confirmed:
                        # Call on_confirm hook - return False to cancel and continue
                        if self.on_confirm:
                            should_break = self.on_confirm(
                                str(self.selected_value), self.selected_index
                            )
                            if not should_break:
                                # Hook requested to continue (e.g., hierarchical selection)
                                # Rebuild choices in case callback modified them
                                self._prepare_choices()
                                # Re-sync filtered index in case callback modified selected_index
                                self._adjust_to_selection()
                                live.update(self._render())
                                live.refresh()
                                continue
                        break

                    live.update(self._render())
                    live.refresh()

        # Only update result if it wasn't already set by should_exit
        if not hasattr(self, "_result_set_by_hook"):
            if self.selected_value is None:
                self.result = (None, None)
            else:
                self.result = (str(self.selected_value), self.selected_index)

        if self.after_run:
            self.after_run(self.result)

        return self.result

    def _handle_other_key(self, key: str) -> bool:
        """Handle any remaining keys. Can be overridden by subclasses."""
        return False
