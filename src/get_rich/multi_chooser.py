"""Multi-select chooser with checkboxes."""

from __future__ import annotations

from typing import Iterable, Any, Sequence, Callable
from rich.text import Text

from .chooser import Chooser
from .key_reader import KeyReader


class MultiChooser(Chooser):
    """A chooser that allows selecting multiple items with checkboxes."""

    def __init__(
        self,
        *,
        choices: Iterable[str],
        min_selected: int | None = None,
        max_selected: int | None = None,
        title_text: str = "",
        header_text: str = "",
        header_location: str = "inside_top",
        height: int | None = None,
        max_height: int | None = None,
        width: int | None = None,
        selected_indices: list[int] | None = None,
        selected_values: list[str] | None = None,
        wrap_navigation: bool = True,
        styles: dict[str, Any] | None = None,
        messages: dict[str, Any] | None = None,
        console: Any = None,
        transient: bool = True,
        keybindings: dict[str, Sequence[str]] | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[tuple[list[str], list[int]] | tuple[None, None]], None]
        | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        on_confirm: Callable[[list[str], list[int]], bool] | None = None,
        should_exit: Callable[[], bool] | None = None,
    ) -> None:
        """Initialize a MultiChooser."""
        super().__init__(
            choices=choices,
            title_text=title_text,
            header_text=header_text,
            header_location=header_location,
            height=height,
            max_height=max_height,
            width=width,
            wrap_navigation=wrap_navigation,
            styles=styles,
            messages=messages,
            console=console,
            transient=transient,
            keybindings=keybindings,
            reader=reader,
            before_run=before_run,
            after_run=after_run,
            on_change=on_change,
            on_key=on_key,
            on_confirm=on_confirm,
            should_exit=should_exit,
        )

        if selected_indices:
            for i in selected_indices:
                self.all_choices[i].is_selected = True
        if selected_values:
            for choice in self.all_choices:
                if str(choice.value) in selected_values:
                    choice.is_selected = True

        self.min_selected = min_selected
        self.max_selected = max_selected
        self.result: tuple[list[str], list[int]] | tuple[None, None] = (None, None)

    def _selected_count(self):
        return sum(1 for choice in self.all_choices if choice.is_selected)

    def _handle_other_key(self, key: str) -> str | None:
        """Handle space to toggle selection of current item."""
        if key == "SPACE":
            self._set_highlighted()
            choice = self.highlighted_choice
            choice.is_selected = not choice.is_selected
            if self.on_change:
                self.on_change(self)
            return None
        return super()._handle_other_key(key)

    def _render_choice_row(self, choice: Chooser.Choice) -> tuple[Text, str]:
        """Render choice row with caret, checkbox, and full-row highlighting."""
        checkbox = (
            self.styles.checkbox_checked
            if choice.is_selected
            else self.styles.checkbox_unchecked
        )

        if choice.is_highlighted:
            # Highlighted: render with caret, checkbox, and selection style applied to entire row
            choice_text = Text.from_markup(
                f"{self.styles.selection_caret} {checkbox} {choice.value.markup}",
                style=self.styles.selection_style,
            )
            return choice_text, self.styles.body_style
        else:
            # Not highlighted: render with spacing, checkbox, and no selection style
            choice_text = Text.from_markup(f"  {checkbox} {choice.value.markup}")
            return choice_text, self.styles.body_style

    def _validate_selection(self) -> str | None:
        """Validate that selected count meets constraints."""
        count = self._selected_count()
        min_sel = self.min_selected
        max_sel = self.max_selected

        if min_sel is not None and max_sel is not None:
            if count < min_sel or count > max_sel:
                return self.messages.range_selected_error.format(
                    min=min_sel, max=max_sel
                )
            return None

        if min_sel is not None and count < min_sel:
            return self.messages.min_selected_error.format(min=min_sel)

        if max_sel is not None and count > max_sel:
            return self.messages.max_selected_error.format(max=max_sel)

        return None

    def run(
        self, *, reader: KeyReader | None = None
    ) -> tuple[list[str], list[int]] | tuple[None, None]:
        """Run the chooser and return selected values and indices."""
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

                # All good - collect selected items
                values = []
                indices = []
                for choice in self.all_choices:
                    if choice.is_selected:
                        values.append(choice.value)
                        indices.append(choice.index)

                # Set result
                if not values:
                    self.result = (None, None)
                else:
                    self.result = (values, indices)
                break

        if self.after_run:
            self.after_run(self)

        # Return the result
        return self.result  # type: ignore[return-value]
