from __future__ import annotations

from typing import Callable, Sequence

from docstring_inheritance import GoogleDocstringInheritanceInitMeta
from rich.console import Console

from .key_reader import KeyReader, get_key_reader


class BaseControl(metaclass=GoogleDocstringInheritanceInitMeta):
    """
    Abstract base class for interactive controls.

    Supports lifecycle hooks and callbacks for customization:
        - before_run(control):
            Called once before the control enters its main loop.
            No return value.
        - after_run(control):
            Called once after the control exits its main loop.
            No return value.
        - on_change(control):
            Called when the selection or state changes (control-specific).
            No return value.
        - on_key(key, control):
            Called for every key press before default bindings are applied.
            Return None to skip default key processing, or return a string
            (possibly modified) to continue processing with that key.
        - on_confirm(control):
            Called when user confirms a selection.
            Return True to accept the selection and exit, or False to reject
            and continue the control loop.
        - should_exit(control):
            Called at the start of each loop iteration to check if the control
            should exit early (e.g., for custom quit logic).
            Return True to exit immediately, or False to continue.
    """

    DEFAULT_KEYBINDINGS: dict[str, Sequence[str]] = {}

    def __init__(
        self,
        *,
        console: Console | None = None,
        transient: bool = True,
        keybindings: dict[str, Sequence[str]] | None = None,
        reader: KeyReader | None = None,
        before_run: Callable[["BaseControl"], None] | None = None,
        after_run: Callable[["BaseControl"], None] | None = None,
        on_change: Callable[["BaseControl"], None] | None = None,
        on_key: Callable[[str, "BaseControl"], str | None] | None = None,
        on_confirm: Callable[["BaseControl"], bool] | None = None,
        should_exit: Callable[["BaseControl"], bool] | None = None,
    ) -> None:
        """Initialize the BaseControl.

        Args:
            console (Console | None):
                Optional Rich Console to use.
            transient (bool):
                Whether to clear the control from the console after exit.
            keybindings (dict[str, Sequence[str]] | None):
                Optional dict of action names to key sequences.
            reader (KeyReader | None):
                Optional KeyReader to read key inputs.
            before_run (Callable[[BaseControl], None] | None):
                Optional callback before running the control.
            after_run (Callable[[BaseControl], None] | None):
                Optional callback after running the control.
            on_change (Callable[[BaseControl], None] | None):
                Optional callback when state changes.
            on_key (Callable[[str, BaseControl], str | None] | None):
                Optional callback for each key press. Return None to skip
                default processing, or return a key string to process.
            on_confirm (Callable[[BaseControl], bool] | None):
                Optional callback when user confirms selection.
            should_exit (Callable[[BaseControl], bool] | None):
                Optional callback to determine if the control should exit.
        """
        self.console = console or Console()
        self.transient = transient
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
