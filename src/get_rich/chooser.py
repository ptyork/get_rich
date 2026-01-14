from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

from rich.align import Align
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
        "backspace": ["BACKSPACE"],
    }

    SCROLL_TOP_OFFSET = 3
    MIN_VISIBLE_WHEN_SCROLLING = SCROLL_TOP_OFFSET + 2

    @dataclass
    class Choice:
        index: int
        value: Text
        is_highlighted: bool = False  # Currently selected/cursor position
        is_selected: bool = False  # For MultiChooser - checked/selected state
        shortcut_key: str | None = None  # For ShortcutChooser - shortcut key to display

        def __str__(self) -> str:
            return str(self.value)

        def __eq__(self, other) -> bool:
            if isinstance(other, str):
                return str(self) == other
            if isinstance(other, Chooser.Choice):
                return self.value == other.value
            return False

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
        wrap_navigation: bool = True,
        styles: ChooserStyles | dict[str, Any] | None = None,
        messages: ChooserMessages | dict[str, Any] | None = None,
        enable_filtering: bool = False,
        console: Console | None = None,
        transient: bool = True,
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
            header_location (str):
                Position of header: "inside_top", "outside_top", "inside_left",
                "outside_left", "inside_right", "outside_right" (default: "inside_top")
            height (int | None):
                Absolute height of the control including borders, title, header, and footer.
                If specified, will pad with blank rows to reach this height. None = auto-size.
            enable_filtering (bool):
                If True, enables text filtering functionality (default: False).
            max_height (int | None):
                Maximum height constraint without padding. None = use console height.
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
            transient=transient,
            keybindings=keybindings,
            reader=reader,
            before_run=before_run,
            after_run=after_run,
            on_change=on_change,
            on_key=on_key,
            on_confirm=on_confirm,  # type: ignore
            should_exit=should_exit,
        )

        self.all_choices: list[Chooser.Choice] = []
        for i, choice in enumerate(choices):
            value = Text.from_markup(choice)
            self.all_choices.append(Chooser.Choice(i, value))

        self.styles: _ChooserStyles = _merge_styles(styles)
        self.title_text: Text = Text.from_markup(title_text) if title_text else None
        self.header_text: Text = (
            Text.from_markup(header_text, style=self.styles.header_style)
            if header_text
            else None
        )
        self.header_location: str = header_location
        self.height: int | None = height
        self.max_height: int | None = max_height
        self.width: int | None = width
        self.messages: _ChooserMessages = _merge_messages(messages)

        # Filtering attributes
        self.enable_filtering: bool = enable_filtering
        self.filter_text: str = ""
        self.filtered_choices: list[Chooser.Choice] = []

        self.highlighted_index: int = 0
        self.highlighted_filtered_index: int = 0
        self.on_confirm: Callable[[str, int], bool] | None = on_confirm
        self.result: tuple[str, int] | tuple[None, None] | None = None

        self.wrap_navigation = wrap_navigation

        # Footer parts for flexible footer rendering
        self.footer_parts: list[str] = [
            self.messages.nav_instructions,
            self.messages.confirm_instructions,
        ]

        # PRE-select choices if requested
        if selected_index is not None and 0 <= selected_index < len(self.all_choices):
            self.highlighted_index = selected_index
            self.highlighted_choice = self.all_choices[selected_index]
        elif selected_value:
            for choice in self.all_choices:
                if choice.plain.lower() == selected_value.lower():
                    self.highlighted_index = choice.index
                    self.highlighted_choice = choice
                    break
        self.highlighted_filtered_index = self.highlighted_index

    ################################################################@##########
    # VIRTUAL: _get_display_choices
    ################################################################@##########
    def _get_display_choices(self) -> list[Chooser.Choice]:
        """Get the list of choices to display. Can be overridden by subclasses."""
        if self.enable_filtering:
            # Update is_highlighted for filtered choices
            for choice in self.filtered_choices:
                choice.is_highlighted = choice.index == self.highlighted_index
            return self.filtered_choices
        return self.all_choices

    ################################################################@##########
    # VIRTUAL: _prepare_choices
    ################################################################@##########
    def _prepare_choices(self) -> None:
        """Prepare choices for display. Can be overridden by subclasses for filtering."""
        if self.enable_filtering:
            self._filter_choices()
        else:
            self._set_highlighted()

    ################################################################@##########
    # VIRTUAL: _validate_selection
    ################################################################@##########
    def _validate_selection(self) -> str | None:
        """Validate the current selection. Return error message or None.

        Override in subclasses to add validation logic.
        """
        return None

    ################################################################@##########
    # VIRTUAL: _handle_other_key
    ################################################################@##########
    def _handle_other_key(self, key: str) -> bool:
        """Handle any remaining keys. Can be overridden by subclasses."""
        if self.enable_filtering:
            if key in self.keybindings.get("backspace", []):
                if self.filter_text:
                    self.filter_text = self.filter_text[:-1]
                    self._filter_choices()
                return False
            elif key == "SPACE":
                # Special handling for space key
                self.filter_text += " "
                self._filter_choices()
                return False
            elif len(key) == 1 and key.isprintable():
                self.filter_text += key
                self._filter_choices()
                return False
        return False

    ################################################################@##########
    # VIRTUAL: _render_header
    ################################################################@##########
    def _render_header(self, table: Table) -> None:
        """Render header line if applicable. Can be overridden by subclasses."""
        if self.enable_filtering:
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

    ################################################################@##########
    # VIRTUAL: _render_footer
    ################################################################@##########
    def _render_footer(
        self, table: Table, display_choices: list[Chooser.Choice]
    ) -> None:
        """Render footer text from footer_parts. Can be overridden by subclasses."""
        if self.footer_parts:
            footer_text = Text(self.messages.footer_separator.join(self.footer_parts))
            footer_text.justify = "center"
            table.add_row(footer_text, style=self.styles.footer_style)

    ################################################################@##########
    # VIRTUAL: _render_choice_row
    ################################################################@##########
    def _render_choice_row(self, choice: Choice) -> tuple[Text, str]:
        """Render a single choice row. Override to customize display.

        Args:
            choice: The choice to render (contains all state: is_highlighted, is_selected, etc.)

        Returns:
            tuple of (Text to display, style for the row)
        """
        if choice.is_highlighted:
            caret = self.styles.selection_caret
            choice_text = Text.from_markup(
                f"{caret} {choice.value.markup}",
                style=self.styles.selection_style,
            )
            return choice_text, self.styles.body_style
        else:
            choice_text = Text.from_markup(f"  {choice.value.markup}")
            return choice_text, self.styles.body_style

    ################################################################@##########
    # UTILITY: _render
    ################################################################@##########
    def _render(self) -> RenderableType:
        display_choices = self._get_display_choices()

        # Parse header location
        is_header_inside = self.header_location.startswith("inside_")
        is_header_side = (
            "left" in self.header_location or "right" in self.header_location
        )
        is_header_left = "left" in self.header_location
        is_header_top = "top" in self.header_location

        # Determine table sizing based on header configuration
        if not is_header_inside and is_header_side:
            # Outside side headers: choices auto-size
            table_width, expand_table = None, False
            title_width = 0
        else:
            # width=0 means expand, None means auto-size, >0 means fixed
            border_width = 4 if self.styles.show_border else 0
            title_width = (len(self.title_text) + 2) if self.title_text else 0
            table_width = None
            if self.width:
                table_width = self.width - border_width
            expand_table = self.width == 0

        # Create and populate the choices table
        choices_table = Table(
            style=self.styles.body_style,
            padding=self.styles.option_padding,
            collapse_padding=True,
            show_edge=False,
            show_header=False,
            expand=expand_table,
            min_width=title_width,
        )
        choices_table.add_column(width=table_width, no_wrap=True)

        # When borderless, render title as part of choices table if present
        if not self.styles.show_border and self.title_text:
            self.title_text.justify = "center"
            self.title_text.style = self.styles.header_style
            choices_table.add_row(self.title_text)

        # Render inside_top header in the choices table
        if self.header_text and is_header_inside and is_header_top:
            choices_table.add_row(self.header_text)

        self._render_header(choices_table)

        # Calculate visible window for scrolling
        # Pass current row count so we know what's already in the table
        max_items = self._visible_count(display_choices, choices_table.row_count)
        total_items = len(display_choices)

        if total_items <= max_items:
            # Everything fits - no scrolling
            start = 0
            end = total_items
            show_up_arrow = show_down_arrow = False
        else:
            # Position selection SCROLL_TOP_OFFSET rows from top
            adjusted_top_offset = min(self.SCROLL_TOP_OFFSET, max_items // 2)
            start = max(0, self.highlighted_filtered_index - adjusted_top_offset)

            # Check if arrows will be needed and reserve rows for them
            show_up_arrow = start > 0
            show_down_arrow = (start + max_items) < total_items

            # a row for every True arrow -- int(true) = 1
            arrow_rows = int(show_up_arrow) + int(show_down_arrow)

            # When showing up arrow, skip an extra row so two items scroll under it.
            # Less awkward and more natural feeling.
            if show_up_arrow:
                start += 1

            # Calculate end, ensuring we don't scroll past the bottom
            choice_rows = max_items - arrow_rows
            start = min(start, total_items - choice_rows)
            end = start + choice_rows

        # Optionally render the scroll indicator at the top.
        if show_up_arrow:
            up_text = Text.from_markup(
                "  " + self.styles.scroll_indicator_up,
                style=self.styles.scroll_indicator_style,
            )
            choices_table.add_row(up_text)

        # Render each of the real choices.
        for i, choice in enumerate(display_choices[start:end]):
            choice_text, row_style = self._render_choice_row(choice)
            choices_table.add_row(choice_text, style=row_style)

        if show_down_arrow:
            down_text = Text.from_markup(
                "  " + self.styles.scroll_indicator_down,
                style=self.styles.scroll_indicator_style,
            )
            choices_table.add_row(down_text)

        # Pad with blank rows if absolute height is specified
        if self.height is not None:
            # Calculate target rows (height minus borders and footer)
            target_rows = self.height
            if self.styles.show_border:
                target_rows -= 2
            if self.footer_parts and any(self.footer_parts):
                target_rows -= 1

            # Add blank rows to reach target
            current_rows = choices_table.row_count
            blank_rows_needed = max(0, target_rows - current_rows)
            for _ in range(blank_rows_needed):
                choices_table.add_row(Text(""))

        # Wrap with header/footer based on location
        if is_header_inside and is_header_side:
            # Inside side header: wrap choices table with header and footer
            outer = Table.grid(expand=expand_table)
            outer.add_column()

            # Header and choices side-by-side
            inner = Table.grid(expand=expand_table)
            if is_header_left:
                inner.add_column(no_wrap=True)
                inner.add_column(width=table_width, no_wrap=True)
                inner.add_row(self.header_text, choices_table)
            else:
                inner.add_column(width=table_width, no_wrap=True)
                inner.add_column(no_wrap=True)
                inner.add_row(choices_table, self.header_text)

            outer.add_row(inner)
            if self.messages.instructions:
                outer.add_row(
                    self.messages.instructions, style=self.styles.footer_style
                )
            table = outer
        else:
            self._render_footer(choices_table, display_choices)
            table = choices_table

        # Apply outside header wrapper if needed
        if self.header_text and not is_header_inside:
            if is_header_side:
                return self._wrap_outside_side_header(
                    table, is_header_left, expand_table, table_width
                )
            else:  # outside top header
                container = Table.grid(expand=expand_table)
                container.add_column(
                    width=table_width if table_width else None, no_wrap=True
                )
                container.add_row(self.header_text)
                container.add_row(
                    self._wrap_in_panel(table, expand_table, table_width)
                    if self.styles.show_border
                    else table
                )
                return container

        # Return bordered or borderless table
        renderable = (
            self._wrap_in_panel(table, expand_table, table_width)
            if self.styles.show_border
            else table
        )

        # Check for error message (used by MultiChooser and potentially other subclasses)
        error_message = getattr(self, "_error_message", None)
        if error_message:
            # Calculate height: base table height + 2 if bordered (for panel borders)
            height = table.row_count if hasattr(table, "row_count") else 0
            if self.styles.show_border:
                height += 2

            # Render overlay panel with error message
            width = renderable.width if hasattr(renderable, "width") else None
            message_text = Text.from_markup(error_message)
            aligned_text = Align(message_text, align="center", vertical="middle")

            # Try to get error title from messages, fallback to generic
            error_title = getattr(self.messages, "multi_validation_error", "Error")

            return Panel(
                aligned_text,
                title=error_title,
                style=self.styles.error_style,
                width=width,
                height=height,
            )

        return renderable

    ################################################################@##########
    # UTILITY: _filter_choices
    ################################################################@##########
    def _filter_choices(self) -> None:
        """Apply current filter to choices."""
        # If no filter text, show all choices
        if not self.filter_text:
            self.filtered_choices = self.all_choices
        else:
            # Apply text filter
            filter_lower = self.filter_text.lower()
            self.filtered_choices = [
                choice
                for choice in self.all_choices
                if filter_lower in choice.value.plain.lower()
            ]

        """Adjust filtered index to match selected index. Can be overridden by subclasses."""
        display_choices = self._get_display_choices()
        filtered_indices = [choice.index for choice in display_choices]
        if self.highlighted_index in filtered_indices:
            self.highlighted_filtered_index = filtered_indices.index(self.highlighted_index)
        else:
            self.highlighted_filtered_index = 0
        self._set_highlighted()

    ################################################################@##########
    # UTILITY: _wrap_outside_side_header
    ################################################################@##########
    def _wrap_outside_side_header(
        self, table: Table, is_left: bool, expand: bool, width: int | None
    ) -> Table:
        """Wrap table with outside left/right header."""
        wrapped_table = (
            self._wrap_in_panel(table, False, None)
            if self.styles.show_border
            else table
        )

        # Fixed width case
        if self.width is not None and self.width > 0:
            outer = Table.grid(expand=False)
            outer.add_column(width=self.width)
            inner = Table.grid(expand=False, padding=(0, 1))

            if is_left:
                inner.add_column(justify="left", ratio=1)
                inner.add_column()
                inner.add_row(self.header_text, wrapped_table)
            else:
                inner.add_column()
                inner.add_column(justify="left", ratio=1)
                inner.add_row(wrapped_table, self.header_text)

            outer.add_row(inner)
            return outer

        # Auto-size case
        container = Table.grid(expand=expand, padding=(0, 1))
        container.show_lines = True

        if is_left:
            container.add_column(justify="left")
            container.add_column()
            container.add_row(
                self.header_text,
                self._wrap_in_panel(table, expand, None)
                if self.styles.show_border
                else table,
            )
        else:
            container.add_column()
            container.add_column(justify="left")
            container.add_row(
                self._wrap_in_panel(table, expand, None)
                if self.styles.show_border
                else table,
                self.header_text,
            )

        return container

    ################################################################@##########
    # UTILITY: _wrap_in_panel
    ################################################################@##########
    def _wrap_in_panel(
        self, table: Table, expand_table: bool, table_width: int | None
    ) -> Panel:
        """Wrap the table in a Panel with appropriate settings.

        Args:
            table: The table to wrap
            expand_table: Whether the panel should expand
            table_width: The width to apply to the panel (None means auto-size, not self.width)
        """
        panel_kwargs: dict[str, Any] = {
            "title": self.title_text,
            "style": self.styles.body_style,
            "border_style": self.styles.border_style,
        }

        # Use table_width parameter instead of self.width for panel sizing
        # This allows outside headers to control sizing independently
        panel_kwargs["expand"] = False
        if expand_table:
            panel_kwargs["expand"] = True
        elif table_width:
            panel_kwargs["width"] = table_width + 4

        return Panel(table, **panel_kwargs)

    ################################################################@##########
    # UTILITY: _set_highlighted
    ################################################################@##########
    def _set_highlighted(self) -> None:
        for choice in self.all_choices:
            choice.is_highlighted = False
        display_choices = self._get_display_choices()
        if display_choices:
            choice = display_choices[self.highlighted_filtered_index]
            self.highlighted_choice = choice
            self.highlighted_index = choice.index
            choice.is_highlighted = True
        else:
            self.highlighted_choice = None
            self.highlighted_index = 0
            
        if self.on_change:
            self.on_change(self)

    ################################################################@##########
    # UTILITY: _visible_count
    ################################################################@##########
    def _visible_count(
        self,
        display_choices: list[Chooser.Choice] | None = None,
        table_rows_so_far: int = 0,
    ) -> int:
        """Calculate the number of visible item slots based on absolute height constraints.

        Args:
            display_choices: List of choices to display
            table_rows_so_far: Number of rows already in the table (title, header, etc.)
        """
        if display_choices is None:
            display_choices = self._get_display_choices()

        # Determine the maximum absolute height
        if self.height is not None:
            absolute_height = self.height
        elif self.max_height is not None:
            absolute_height = self.max_height
        else:
            absolute_height = self.console.height

        # Calculate available rows for items
        available_rows = absolute_height

        # Subtract borders if enabled
        if self.styles.show_border:
            available_rows -= 2

        # Subtract rows already in the table (title, header text, filter row, etc.)
        available_rows -= table_rows_so_far

        # Subtract 1 for footer if present
        if self.footer_parts and any(self.footer_parts):
            available_rows -= 1

        # Ensure at least MIN_VISIBLE_WHEN_SCROLLING rows when scrolling is needed
        if len(display_choices) > available_rows:
            available_rows = max(available_rows, self.MIN_VISIBLE_WHEN_SCROLLING)

        return max(1, available_rows)

    ################################################################@##########
    # INTERNAL: _choose
    ################################################################@##########
    def _choose(self, reader: KeyReader) -> bool:
        """Run the main event loop until user confirms or cancels.

        Returns:
            True if user confirmed selection, False if cancelled.
        """
        with Live(
            self._render(),
            console=self.console,
            transient=self.transient,
            auto_refresh=False,
        ) as live:
            while True:
                # Check if we should exit early via custom logic
                if self.should_exit and self.should_exit(self):
                    return False

                key = reader.read_key()

                # Ignore empty keys (unrecognized sequences, etc.)
                if not key:
                    continue

                # If an error overlay is active, clear it on any key press and re-render
                if getattr(self, "_error_message", None):
                    self._error_message = None
                    live.update(self._render())
                    live.refresh()
                    continue

                # Allow custom on_key handler to intercept or modify the key
                if self.on_key:
                    intercepted = self.on_key(key, self)
                    if intercepted is None:
                        # Handler requested to skip default processing
                        live.update(self._render())
                        live.refresh()
                        continue
                    key = intercepted

                display_choices = self._get_display_choices()

                if key in self.keybindings.get("up", []):
                    if self.highlighted_filtered_index > 0:
                        self.highlighted_filtered_index -= 1
                    elif self.wrap_navigation and display_choices:
                        self.highlighted_filtered_index = len(display_choices) - 1

                elif key in self.keybindings.get("down", []):
                    if self.highlighted_filtered_index < len(display_choices) - 1:
                        self.highlighted_filtered_index += 1
                    elif self.wrap_navigation and display_choices:
                        self.highlighted_filtered_index = 0

                elif key in self.keybindings.get("home", []):
                    self.highlighted_filtered_index = 0

                elif key in self.keybindings.get("end", []):
                    if display_choices:
                        self.highlighted_filtered_index = len(display_choices) - 1

                elif key in self.keybindings.get("page_up", []):
                    step = max(1, self._visible_count(display_choices) - 1)
                    self.highlighted_filtered_index = max(
                        0, self.highlighted_filtered_index - step
                    )

                elif key in self.keybindings.get("page_down", []):
                    if display_choices:
                        step = max(1, self._visible_count(display_choices) - 1)
                        self.highlighted_filtered_index = min(
                            len(display_choices) - 1,
                            self.highlighted_filtered_index + step,
                        )

                elif key in self.keybindings.get("confirm", []):
                    return True

                elif key in self.keybindings.get("cancel", []):
                    return False

                else:
                    if self._handle_other_key(key):
                        return True

                self._set_highlighted()

                live.update(self._render())
                live.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self, *, reader: KeyReader | None = None
    ) -> tuple[str, int] | tuple[None, None]:
        """Run the chooser and return the selected value and index."""
        if self.before_run:
            self.before_run(self)

        self._prepare_choices()
        with reader or self._get_reader() as key_reader:
            while True:
                confirmed = self._choose(key_reader)

                if not confirmed:
                    self.result = (None, None)
                    break

                # Validate selection
                error = self._validate_selection()
                if error:
                    self._error_message = error
                    continue

                # Call confirmation hook if present
                if self.on_confirm:
                    if not self.on_confirm(self):
                        # Hook wants to continue
                        self._prepare_choices()
                        continue

                # All good - set result and return
                self._set_highlighted()
                choice = self.highlighted_choice
                if choice is None:
                    self.result = (None, None)
                else:
                    self.result = (str(choice.value), choice.index)
                break

        if self.after_run:
            self.after_run(self)

        return self.result  # type: ignore[return-value]
