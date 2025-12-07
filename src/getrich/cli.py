"""Simple demo entrypoint for manual testing."""

from __future__ import annotations

import inspect
from rich import print
from rich.align import Align

from getrich import (
    Chooser,
    FilterChooser,
    FileChooser,
    ShortcutChooser,
    ChooserStyles,
    ChooserMessages,
)

def basic_chooser() -> None:
    choices = [
        "apple",
        "banana",
        "cherry",
        "date",
        "elderberry",
        "fig",
        "grape",
        "honeydew",
    ]
    chooser = Chooser(
        choices=choices,
        title_text="Select a fruit:",
        height=8,
        width=50,
    )
    value, index = chooser.run()
    if value is not None:
            print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def chooser_with_custom_styles() -> None:
    custom_styles: ChooserStyles = {
        "body_style": "white on dark_blue",
        "border_style": "yellow on dark_blue",
        "selection_style": "bold bright_white on blue",
        "selection_caret": "➜",
        "footer_style": "yellow",
    }
    chooser = Chooser(
        choices=["option 1", "option 2", "option 3"],
        title_text="Custom Styled Chooser:",
        styles=custom_styles,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def basic_filter_chooser() -> None:
    choices = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
    ]
    filter_chooser = FilterChooser(
        choices=choices,
        title_text="Filter and select an option:",
        height=6,
    )
    value, index = filter_chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def filter_chooser_with_custom_messages() -> None:
    colors = [
        "red",
        "green",
        "blue",
        "yellow",
        "purple",
        "orange",
        "pink",
        "brown",
        "black",
        "white",
    ]
    custom_messages: ChooserMessages = {
        "instructions": "Type to filter • ↑↓ Navigate • Enter Confirm",
        "filter_label": "Type to filter options: ",
        "items_count": "{count} fruits",
    }
    filter_chooser = FilterChooser(
        choices=colors,
        title_text="Custom Messages FilterChooser:",
        messages=custom_messages,
    )
    value, index = filter_chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def basic_file_chooser() -> None:
    file_chooser = FileChooser(
        initial_path=".",
        choose_dirs=False,
        title_text="Select a file:",
        height=10,
        width=60,
    )
    path = file_chooser.run()  # returns a Path object
    if path:
        print(f"You selected: {path.resolve()}")
    else:
        print("Cancelled")


def file_chooser_with_glob_pattern() -> None:
    """FileChooser with glob patterns to filter specific file types."""
    file_chooser = FileChooser(
        initial_path=".",
        glob=["*.py", "*.md", "*.txt"],
        exclude_hidden=True,
        title_text="Select a Python, Markdown, or Text file:",
        height=12,
    )
    path = file_chooser.run()
    if path:
        print(f"You selected: {path.resolve()}")
    else:
        print("Cancelled")


def file_chooser_for_directories() -> None:
    """FileChooser configured to select directories instead of files."""
    file_chooser = FileChooser(
        initial_path=".",
        choose_dirs=True,
        exclude_hidden=True,
        title_text="Select a directory:",
        height=10,
    )
    path = file_chooser.run()
    if path:
        print(f"You selected directory: {path.resolve()}")
    else:
        print("Cancelled")


def basic_shortcut_chooser() -> None:
    choices = [
        "New File",
        "Open File",
        "Save File",
        "Close File",
        "Exit Application",
    ]
    shortcut_chooser = ShortcutChooser(
        choices=choices,
        title_text="Select an action (use shortcuts 1-5):",
        height=7,
        show_shortcuts=True,
    )
    value, index = shortcut_chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def shortcut_chooser_with_custom_keys_and_no_confirm() -> None:
    choices = [
        "[u bright_red]C[/]opy",
        "[u bright_red]P[/]aste",
        "[u bright_red]C[/]ut",
        "[u bright_red]U[/]ndo",
        "[u bright_red]R[/]edo",
    ]
    custom_shortcut_keys = ["c", "v", "x", "z", "y"]
    shortcut_chooser = ShortcutChooser(
        choices=choices,
        title_text="Select an action:",
        shortcut_keys=custom_shortcut_keys,
        no_confirm=True,
        show_shortcuts=False,
        strict_mode=True,
    )
    value, index = shortcut_chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def borderless_chooser_expanded() -> None:
    """Chooser without borders that expands to fill terminal width."""
    choices = ["Option A", "Option B", "Option C", "Option D"]
    chooser = Chooser(
        choices=choices,
        title_text="🎨 Borderless & Expanded",
        header_text="This chooser has no border and expands to full width",
        width=0,  # 0 = expand to fill terminal
        styles={"show_border": False},
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def chooser_with_hooks() -> None:
    """Chooser with before_run, after_run, and on_change hooks."""
    counter = {"changes": 0}
    
    def before():
        print("[dim]🔔 Chooser is starting...[/]")
    
    def after(result):
        val, idx = result if result else (None, None)
        print(f"[dim]🔔 Chooser finished. Changes: {counter['changes']}, Result: {val}[/]")
    
    def on_change():
        counter["changes"] += 1
    
    chooser = Chooser(
        choices=["Red", "Green", "Blue", "Yellow"],
        title_text="Chooser with Hooks",
        header_text="Navigate to trigger on_change",
        before_run=before,
        after_run=after,
        on_change=on_change,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")


def chooser_with_custom_keybindings() -> None:
    """Chooser with custom keybindings (WASD instead of arrows)."""
    custom_keys = {
        "up": ["w", "W"],
        "down": ["s", "S"],
        "confirm": ["ENTER", "SPACE"],
        "cancel": ["ESC", "q", "Q"],
    }
    chooser = Chooser(
        choices=["Forward", "Back", "Left", "Right", "Jump"],
        title_text="WASD Navigation",
        header_text="Use W/S to navigate, Space/Enter to confirm, Q to cancel",
        keybindings=custom_keys,
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def filter_chooser_with_large_dataset() -> None:
    """FilterChooser with many items demonstrating filtering performance."""
    # Generate a larger dataset
    choices = [
        f"{category}-{i:03d}" 
        for category in ["alpha", "beta", "gamma", "delta", "epsilon"]
        for i in range(1, 21)
    ]
    filter_chooser = FilterChooser(
        choices=choices,
        title_text="🔍 Large Dataset Filter Demo",
        header_text="Type to filter 100 items",
        height=12,
        width=0,
    )
    value, index = filter_chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def chooser_no_wrap_navigation() -> None:
    """Chooser with wrap_navigation disabled (stops at ends)."""
    chooser = Chooser(
        choices=["First", "Second", "Third", "Fourth", "Last"],
        title_text="No Wrap Navigation",
        header_text="Navigation stops at top/bottom (no wrapping)",
        wrap_navigation=False,
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


chooser_demos = {
    "Chooser": [
        basic_chooser,
        chooser_with_custom_styles,
        borderless_chooser_expanded,
        chooser_with_hooks,
        chooser_with_custom_keybindings,
        chooser_no_wrap_navigation,
    ],
    "FilterChooser": [
        basic_filter_chooser,
        filter_chooser_with_custom_messages,
        filter_chooser_with_large_dataset,
    ],
    "FileChooser": [
        basic_file_chooser,
        file_chooser_with_glob_pattern,
        file_chooser_for_directories,
    ],
    "ShortcutChooser": [
        basic_shortcut_chooser,
        shortcut_chooser_with_custom_keys_and_no_confirm,
    ],
}


def main() -> None:
    while True:
        val, _ = Chooser(
            choices=chooser_demos.keys(),
            title_text="Select a chooser to demo:",
            messages={
                "instructions": "↑↓ Navigate • Enter Confirm • Esc Exit",
            },
        ).run()
        if val:
            demos = chooser_demos.get(val, [])
            choices = [func.__name__.replace("_"," ").title() for func in demos]
            _, index = Chooser(
                choices=choices,
                title_text=f"Select a demo for {val}:",
                messages={
                    "instructions": "↑↓ Navigate • Enter Confirm • Esc Go Back",
                },
            ).run()
            if index is not None:
                demos[index]()
                print(Align.center("Source Code", style="bold bright_white on blue"))
                print(inspect.getsource(demos[index]))
        else:
            break

if __name__ == "__main__":
    main()
