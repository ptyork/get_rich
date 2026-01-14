from __future__ import annotations

from typing import Callable, Iterable, Sequence
from os import sep, stat
from pathlib import Path
import sys

from rich.console import Console
from rich.text import Text

from . import Chooser
from .key_reader import KeyReader
from .styles import ChooserStyles
from .messages import ChooserMessages

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import win32api


def _is_hidden(p: Path) -> bool:
    """Check if a file or directory is hidden."""
    if p.name.startswith("."):
        return True
    # Windows-specific hidden attribute check
    if IS_WINDOWS:
        try:
            attrs = stat(p).st_file_attributes  # type: ignore[attr-defined]
            FILE_ATTRIBUTE_HIDDEN = 0x2
            if attrs & FILE_ATTRIBUTE_HIDDEN:
                return True
        except (OSError, AttributeError):
            pass
    return False


def _get_volumes_win32():
    if IS_WINDOWS:
        drives_string = win32api.GetLogicalDriveStrings()
        drives = drives_string.split("\000")[:-1]
        volumes = {}
        for drive in drives:
            try:
                volume_info = win32api.GetVolumeInformation(drive)
                volumes[drive] = volume_info[0]
            except Exception:
                volumes[drive] = "Local Disk"
        return volumes
    return None


class FileChooser(Chooser):
    """A chooser that allows selection of a file or directory."""

    def __init__(
        self,
        *,
        initial_path: Path | str = ".",
        choose_dirs: bool = False,
        files_at_top: bool = True,
        exclude_hidden: bool = False,
        exclude_dunder: bool = False,
        glob: str | Iterable[str] = "*",
        auto_filter: bool = True,
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
        styles: ChooserStyles | None = None,
        messages: ChooserMessages | None = None,
        console: Console | None = None,
        transient: bool = True,
        reader: KeyReader | None = None,
        before_run: Callable[["FileChooser"], None] | None = None,
        after_run: Callable[["FileChooser"], None] | None = None,
        on_change: Callable[["FileChooser"], None] | None = None,
        on_key: Callable[[str, "FileChooser"], str | None] | None = None,
        on_confirm: Callable[["FileChooser"], bool] | None = None,
        should_exit: Callable[["FileChooser"], bool] | None = None,
    ) -> None:
        """
        Initialize a FileChooser.

        Args:
            initial_path (Path | str ):
                The initial directory path to display (default: current dir).
            choose_dirs (bool):
                If True, allows selection of directories instead of files
                (default: False).
            files_at_top (bool):
                If True, lists files grouped together before directories.
                Otherwise all files and directories are sorted together
                alphabetically. The special `.` and `..` dirs will alwasys
                appear at the top regardless of this setting (default: True).
            exclude_hidden (bool):
                If True, excludes hidden files and directories (default: False).
            exclude_dunder (bool):
                If True, excludes dunder files and directories (default: False).
            glob (str | Iterable[str]):
                A glob pattern or list of patterns to filter files. Does not
                apply to directories. (default: "*").
            auto_filter (bool):
                If True, disables file filtering until the number of files /
                folders exceeds the height. Setting disable_filtering to True
                overrides this behavior by always disabling filtering entirrely.
                (default: True).
        """
        self.current_path: Path = Path(initial_path)
        self.choose_dirs: bool = choose_dirs
        self.files_at_top: bool = files_at_top
        self.exclude_hidden: bool = exclude_hidden
        self.exclude_dunder: bool = exclude_dunder
        self.glob: Iterable[str] = glob
        self.auto_filter: bool = auto_filter

        super().__init__(
            choices=[],
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
            enable_filtering=True,
            console=console,
            transient=transient,
            reader=reader,
            before_run=before_run,
            after_run=after_run,
            on_change=on_change,
            on_key=on_key,
            on_confirm=on_confirm or self._on_confirm,
            should_exit=should_exit,
        )
        # Parent already calls _prepare_choices() which builds file list

    def _prepare_choices(self) -> None:
        """Build the file/directory list and prepare for display."""
        # Determine current directory and selected file
        highlighted_file = ""
        path = self.current_path = self.current_path.resolve()
        if not path.exists():
            path = self.current_path = Path(".").resolve()
        elif path.is_file():
            highlighted_file = path.name
            path = self.current_path = path.parent.resolve()

        dirs = []
        for dir_ in path.iterdir():
            if not dir_.is_dir():
                continue
            if self.exclude_hidden and _is_hidden(dir_):
                continue
            if self.exclude_dunder and dir_.name.startswith("__"):
                continue
            dir_str = f"{dir_.name}{sep} "  # trailing space needed to fix weird trailing \ issue on Windows
            dirs.append(dir_str)

        files = set()
        globs = [self.glob] if isinstance(self.glob, str) else self.glob
        for pattern in globs:
            for file in path.glob(pattern):
                if not file.is_file():
                    continue
                if self.exclude_hidden and _is_hidden(file):
                    continue
                if self.exclude_dunder and file.name.startswith("__"):
                    continue
                files.add(file.name)

        dirs = sorted(dirs, key=str.casefold)
        files = sorted(files, key=str.casefold)

        text_choices: list[Text] = []
        if self.choose_dirs:
            text_choices.append(Text.from_markup(f"SELECT {path}{sep}"))
        else:
            text_choices.append(
                Text.from_markup(
                    f".{sep}    [{self.styles.full_path_style}]({path})[/]"
                )
            )
        if path.parent and path.parent != path:
            text_choices.append(
                Text.from_markup(
                    f"..{sep}   [{self.styles.full_path_style}]({path.parent})[/]"
                )
            )
        elif IS_WINDOWS and path == Path(path.anchor):
            # On Windows, at root of drive, show other drives
            volumes = _get_volumes_win32()
            if volumes:
                drive_choices = []
                for drive, vol in volumes.items():
                    if Path(drive) != path:
                        drive_choices.append(
                            Text.from_markup(
                                f"{drive}   [{self.styles.full_path_style}]({vol})[/]"
                            )
                        )
                text_choices = drive_choices + text_choices

        all = dirs
        selected_index = 0  # default for choose_dirs mode
        if not self.choose_dirs:
            all = files + dirs
            if not self.files_at_top:
                all.sort(key=str.casefold)
            if all:
                selected_index = len(text_choices)  # first non-special entry
                if highlighted_file in all:
                    selected_index += all.index(highlighted_file)

        text_choices.extend([Text.from_markup(name) for name in all])

        # Update choices and selected index
        self.all_choices = [
            Chooser.Choice(i, text) for i, text in enumerate(text_choices)
        ]
        self.highlighted_index = self.highlighted_filtered_index = selected_index

        # Dynamically enable/disable filtering based on list size
        # Calculate visible count to determine if filtering is needed
        if self.auto_filter:
            visible_count = self._visible_count(self.all_choices, 0)
            if len(self.all_choices) > visible_count:
                # Only enable filtering if we have more items than visible space
                self.enable_filtering = True
            else:
                # Disable filtering if everything fits on screen
                self.enable_filtering = False
        else:
            # If auto_filter is False, always enable filtering
            self.enable_filtering = True

        # Call parent to apply text filtering and build filtered_choices
        super()._prepare_choices()

    def _on_confirm(self, chooser: "FileChooser") -> bool:
        selected_value = str(chooser.selected_value)
        selected_index = chooser.highlighted_index
        
        if self.choose_dirs:
            if selected_index != 0:
                selected_name = selected_value.split()[0]
                self.current_path = Path(self.current_path / selected_name).resolve()
                return False
        else:
            selected_name = selected_value.split()[0]
            self.current_path = Path(self.current_path / selected_name).resolve()
            if self.current_path.is_dir():
                return False

        return True

    def run(self, *, reader: KeyReader | None = None) -> Path | None:  # type: ignore[override]
        sel, _ = super().run(reader=reader)
        if not sel:
            return None
        else:
            return self.current_path  # set in _on_confirm
