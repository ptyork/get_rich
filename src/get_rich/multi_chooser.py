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
        title_text: str = "",
        header_text: str = "",
        header_location: str = "inside_top",
        height: int = 10,
        width: int | None = None,
        selected_indexes: list[int] | None = None,
        selected_values: list[str] | None = None,
        wrap_navigation: bool = True,
        styles: dict[str, Any] | None = None,
        messages: dict[str, Any] | None = None,
        console: Any = None,
        transient: bool = True,
        keybindings: dict[str, Sequence[str]] | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[tuple[list[str], list[int]] | tuple[None, None]], None] | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        on_confirm: Callable[[list[str], list[int]], bool] | None = None,
        should_exit: Callable[[], bool] | None = None,
        min_selected: int | None = None,
        max_selected: int | None = None,
    ) -> None:
        """Initialize a MultiChooser."""
        super().__init__(
            choices=choices,
            title_text=title_text,
            header_text=header_text,
            header_location=header_location,
            height=height,
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
        
        if selected_indexes:
            for i in selected_indexes:
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
            self._set_selected()
            choice = self.highlighted_choice
            choice.is_selected = not choice.is_selected
            if self.on_change:
                self.on_change()
            return None
        return super()._handle_other_key(key)

    def _render_choice_row(self, choice: Chooser.Choice) -> Text:
        """Render choice row with checkbox."""
        # Get the base rendering from parent
        base_row = super()._render_choice_row(choice)
        
        # Add checkbox prefix
        checkbox = (
            self.style.checkbox_checked 
            if choice.is_selected
            else self.style.checkbox_unchecked
        )
        return Text(f"{checkbox} ") + base_row

    def _validate_selection(self) -> str | None:
        """Validate that selected count meets constraints."""
        count = self._selected_count()
        min_sel = self.min_selected
        max_sel = self.max_selected

        if min_sel is not None and max_sel is not None:
            if count < min_sel or count > max_sel:
                return f"Please select between {min_sel} and {max_sel} items"
            return None

        if min_sel is not None and count < min_sel:
            return f"Please select at least {min_sel} items"

        if max_sel is not None and count > max_sel:
            return f"Please select at most {max_sel} items"

        return None

    def run(
        self, *, reader: KeyReader | None = None
    ) -> tuple[list[str], tuple[int]] | tuple[None, None]:
        """Run the chooser and return the selected value and index."""

        confirmed = self._run_main_loop(reader)

        if confirmed:
            values = []
            indexes = []
            for choice in self.all_choices:
                if choice.is_selected:
                    values.append(choice.value)
                    indexes.append(choice.index)
            return values, indexes
            
        return (None, None)
    
