from __future__ import annotations

from typing import Any, Callable, Sequence

from docstring_inheritance import GoogleDocstringInheritanceInitMeta
from rich.console import Console

from .key_reader import KeyReader, get_key_reader


class BaseControl(metaclass=GoogleDocstringInheritanceInitMeta):
    """
    Abstract base class for interactive controls.

    Supports lifecycle hooks and callbacks for customization:
        - before_run:
            Called before the control enters its main loop.
        - after_run:
            Called after the control exits, with the final result.
        - on_change:
            Called when the selection or state changes (control-specific).
        - on_key:
            Called for every key before default bindings are applied.
        - on_confirm:
            Called when user confirms a selection. Return False to cancel and
            continue.
        - should_exit:
            Called to check if the control should exit (e.g., for custom quit
            logic).
    """

    DEFAULT_KEYBINDINGS: dict[str, Sequence[str]] = {}

    def __init__(
        self,
        *,
        console: Console | None = None,
        keybindings: dict[str, Sequence[str]] | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[[], None] | None = None,
        after_run: Callable[[Any], None] | None = None,
        on_change: Callable[[], None] | None = None,
        on_key: Callable[[str], str | None] | None = None,
        on_confirm: Callable[[Any], bool] | None = None,
        should_exit: Callable[[], bool] | None = None,
    ) -> None:
        """Initialize the BaseControl.

        Args:
            console (Console | None):
                Optional Rich Console to use.
            keybindings (dict[str, Sequence[str]] | None):
                Optional dict of action names to key sequences.
            reader (KeyReader | None):
                Optional KeyReader to read key inputs.
            before_run (Callable[[], None] | None):
                Optional callback before running the control.
            after_run (Callable[[Any], None] | None):
                Optional callback after running the control.
            on_change (Callable[[], None] | None):
                Optional callback when state changes.
            on_key (Callable[[str], str | None] | None):
                Optional callback for each key press.
            on_confirm (Callable[[Any], bool] | None):
                Optional callback when user confirms selection.
            should_exit (Callable[[], bool] | None):
                Optional callback to determine if the control should exit.
        """
        self.console = console or Console()
        self.keybindings = self._merge_keybindings(keybindings)
        self.reader = reader

        # Lifecycle callbacks
        self.before_run = before_run
        self.after_run = after_run
        self.on_change = on_change
        self.on_key = on_key
        self.on_confirm = on_confirm
        self.should_exit = should_exit

        # Result storage
        self.result = None

    def _merge_keybindings(
        self, overrides: dict[str, Sequence[str]] | None
    ) -> dict[str, list[str]]:
        merged: dict[str, list[str]] = {
            key: list(values) for key, values in self.DEFAULT_KEYBINDINGS.items()
        }
        if overrides:
            for action, keys in overrides.items():
                merged[action] = list(keys)
        return merged

    def _get_reader(self) -> KeyReader:
        return self.reader or get_key_reader()
