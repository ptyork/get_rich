"""Simple demo entrypoint for manual testing."""

from __future__ import annotations

import inspect
from rich import print
from rich.align import Align

from get_rich import (
    Chooser,
    FilterChooser,
    FileChooser,
    MultiChooser,
    ShortcutChooser,
    ChooserStyles,
    ChooserMessages,
    OCEAN_BLUE,
    FOREST_GREEN,
    SUNSET_ORANGE,
    PURPLE_HAZE,
    CYBERPUNK,
    MATRIX,
    BUBBLEGUM,
    TERMINAL_CLASSIC,
    MIDNIGHT_BLUE,
    CREAMSICLE,
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
        width=60,
    )
    path = file_chooser.run()  # returns a Path object
    if path:
        print(f"You selected: {path.resolve()}")
    else:
        print("Cancelled")


def min_height_file_chooser() -> None:
    file_chooser = FileChooser(
        initial_path=".",
        choose_dirs=False,
        title_text="Select a file:",
        header_text="There's a minimum height for scrollable content",
        height=1,
        width=60,
    )
    path = file_chooser.run()  # returns a Path object
    if path:
        print(f"You selected: {path.resolve()}")
    else:
        print("Cancelled")


def no_width_file_chooser() -> None:
    file_chooser = FileChooser(
        initial_path=".",
        choose_dirs=False,
        title_text="Select a file:",
        header_text="Can grow and shrink = bad for usability",
        height=10,
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
        "Paste ([u bright_red]V[/])",
        "Cut ([u bright_red]X[/])",
        "Undo ([u bright_red]Z[/])",
        "Redo ([u bright_red]Y[/])",
    ]
    custom_shortcut_keys = ["c", "v", "x", "z", "y"]
    shortcut_chooser = ShortcutChooser(
        choices=choices,
        title_text="Select an action (press c/v/x/z/y):",
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


def style_ocean_blue() -> None:
    """Chooser with OCEAN_BLUE preset style."""
    chooser = Chooser(
        choices=["Whale", "Dolphin", "Shark", "Octopus", "Jellyfish"],
        title_text="🌊 Ocean Blue Style",
        header_text="Cool blue tones with bright white text",
        styles=OCEAN_BLUE,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_forest_green() -> None:
    """Chooser with FOREST_GREEN preset style."""
    chooser = FilterChooser(
        choices=["Oak", "Pine", "Maple", "Birch", "Cedar"],
        title_text="🌲 Forest Green Style",
        header_text="Natural green theme with high contrast",
        styles=FOREST_GREEN,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_sunset_orange() -> None:
    """Chooser with SUNSET_ORANGE preset style."""
    chooser = FilterChooser(
        choices=["Dawn", "Morning", "Noon", "Dusk", "Twilight"],
        title_text="🌅 Sunset Orange Style",
        header_text="Warm yellow/orange palette",
        styles=SUNSET_ORANGE,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_purple_haze() -> None:
    """Chooser with PURPLE_HAZE preset style."""
    chooser = FilterChooser(
        choices=["Lavender", "Violet", "Plum", "Amethyst", "Orchid"],
        title_text="💜 Purple Haze Style",
        header_text="Vibrant magenta/purple theme",
        styles=PURPLE_HAZE,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_cyberpunk() -> None:
    """Chooser with CYBERPUNK preset style."""
    chooser = FilterChooser(
        choices=["Neon", "Chrome", "Circuit", "Matrix", "Neural"],
        title_text="🤖 Cyberpunk Style",
        header_text="Cyan and magenta neon aesthetic",
        styles=CYBERPUNK,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_matrix() -> None:
    """Chooser with MATRIX preset style."""
    chooser = FilterChooser(
        choices=["Neo", "Trinity", "Morpheus", "Agent Smith", "Oracle"],
        title_text="💚 Matrix Style",
        header_text="Green-on-black hacker style",
        styles=MATRIX,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_bubblegum() -> None:
    """Chooser with BUBBLEGUM preset style."""
    chooser = FilterChooser(
        choices=["Cotton Candy", "Lollipop", "Gumdrops", "Taffy", "Rock Candy"],
        title_text="🍬 Bubblegum Style",
        header_text="Sweet pink and white inverted theme",
        styles=BUBBLEGUM,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_terminal_classic() -> None:
    """Chooser with TERMINAL_CLASSIC preset style."""
    chooser = FilterChooser(
        choices=["ls", "cd", "grep", "awk", "vim"],
        title_text="💻 Terminal Classic Style",
        header_text="Retro green-on-black terminal aesthetic",
        styles=TERMINAL_CLASSIC,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_midnight_blue() -> None:
    """Chooser with MIDNIGHT_BLUE preset style."""
    chooser = FilterChooser(
        choices=["Moon", "Stars", "Night", "Cosmos", "Galaxy"],
        title_text="🌙 Midnight Blue Style",
        header_text="Inverted blue theme with white backgrounds",
        styles=MIDNIGHT_BLUE,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def style_creamsicle() -> None:
    """Chooser with CREAMSICLE preset style."""
    chooser = Chooser(
        choices=["Vanilla", "Orange", "Lemon", "Peach", "Mango"],
        title_text="🍊 Creamsicle Style",
        header_text="Yellow and red summer treat theme",
        styles=CREAMSICLE,
        height=7,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def header_outside_top() -> None:
    """Header positioned outside the panel, above it."""
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Header Outside Top",
        header_text="This header appears above the panel",
        header_location="outside_top",
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def header_inside_left() -> None:
    """Header positioned inside the panel, to the left of choices."""
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Header Inside Left",
        header_text="Left header →",
        header_location="inside_left",
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def header_outside_left() -> None:
    """Header positioned outside the panel, to the left."""
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Header Outside Left",
        header_text="Outside →",
        header_location="outside_left",
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def header_inside_right() -> None:
    """Header positioned inside the panel, to the right of choices."""
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Header Inside Right",
        header_text="← Right header",
        header_location="inside_right",
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def header_outside_right() -> None:
    """Header positioned outside the panel, to the right."""
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Header Outside Right",
        header_text="← Outside",
        header_location="outside_right",
        height=5,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected #{index}: {value}")
    else:
        print("Cancelled")


def simple_yes_no_borderless() -> None:
    """Simple yes/no question without borders."""
    chooser = Chooser(
        choices=["Yes", "No"],
        header_text="Do you want to continue?",
        header_location="outside_left",
        styles={"show_border": False},
        height=2,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You answered: {value}")
    else:
        print("Cancelled")


def confirm_cancel_borderless_with_wrapping() -> None:
    """Confirmation prompt without borders, outside header."""
    chooser = Chooser(
        choices=["Confirm", "Cancel"],
        header_text="You are about to do something really dangerous. This action cannot be undone. Are you 100% sure?",
        header_location="outside_left",
        width=80,
        styles={
            "show_border": False,
            "body_style": "white on red",
            "selection_style": "bold bright_white on red",
            "option_padding": (0, 1),
        },
        messages={"instructions": None},
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected: {value}")
    else:
        print("Cancelled")


def confirm_cancel_with_border_not_transient() -> None:
    """Confirmation prompt without borders, outside header."""
    chooser = Chooser(
        choices=["Confirm", "Cancel"],
        title_text="!!! [blink]WARNING[/] !!!",
        header_text="You are about to do something really dangerous. Like the world is going to end if yo umake a mistake. This action cannot be undone. Are you 100% sure?",
        header_location="outside_left",
        width=80,
        styles={
            "body_style": "bold white on red",
            "border_style": "bold bright_white"
        },
        messages={"instructions": None},
        transient=False,
    )
    value, index = chooser.run()
    if value is not None:
        print(f"You selected: {value}")
    else:
        print("Cancelled")


def basic_multi_chooser() -> None:
    """Basic MultiChooser for selecting multiple items."""
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
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Select multiple fruits:",
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_preselection() -> None:
    """MultiChooser with pre-selected items."""
    choices = [
        "red",
        "green",
        "blue",
        "yellow",
        "purple",
        "orange",
        "pink",
        "cyan",
    ]
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Colors (red, blue, and orange pre-selected):",
        selected_indexes=[0, 2, 5],  # red, blue, orange
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_custom_styles() -> None:
    """MultiChooser with custom styles and checkbox characters."""
    custom_styles: ChooserStyles = {
        "body_style": "white on dark_blue",
        "border_style": "yellow on dark_blue",
        "selection_style": "bold bright_white on blue",
        "footer_style": "yellow",
    }
    choices = [
        "Frontend",
        "Backend",
        "Database",
        "DevOps",
        "QA",
        "Documentation",
    ]
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Select project components:",
        styles=custom_styles,
        height=8,
        width=50,
        checkbox_checked="[✓]",
        checkbox_unchecked="[ ]",
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_filtering() -> None:
    """MultiChooser with filtering enabled (disabled by default)."""
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
    custom_messages: ChooserMessages = {}
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Multi-select with filtering enabled:",
        messages=custom_messages,
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_minimum() -> None:
    """MultiChooser requiring at least a minimum selection."""
    choices = [
        "pizza",
        "sushi",
        "tacos",
        "pasta",
        "salad",
        "ramen",
    ]
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Pick at least two foods:",
        min_selected=2,
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_maximum() -> None:
    """MultiChooser enforcing a maximum selection count."""
    choices = [
        "python",
        "javascript",
        "rust",
        "go",
        "c++",
    ]
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Pick up to two languages:",
        max_selected=2,
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
    else:
        print("Cancelled")


def multi_chooser_with_range() -> None:
    """MultiChooser requiring a selection within a range."""
    choices = [
        "api",
        "cli",
        "ui",
        "docs",
        "tests",
        "ops",
    ]
    multi_chooser = MultiChooser(
        choices=choices,
        title_text="Pick between 2 and 4 workstreams:",
        min_selected=2,
        max_selected=4,
        height=8,
        width=50,
    )
    values, indices = multi_chooser.run()
    if indices is not None:
        print(f"You selected: {values}")
        print(f"Indices: {indices}")
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
    "MultiChooser": [
        basic_multi_chooser,
        multi_chooser_with_preselection,
        multi_chooser_with_custom_styles,
        multi_chooser_with_filtering,
        multi_chooser_with_minimum,
        multi_chooser_with_maximum,
        multi_chooser_with_range,
    ],
    "FileChooser": [
        basic_file_chooser,
        min_height_file_chooser,
        no_width_file_chooser,
        file_chooser_with_glob_pattern,
        file_chooser_for_directories,
    ],
    "ShortcutChooser": [
        basic_shortcut_chooser,
        shortcut_chooser_with_custom_keys_and_no_confirm,
    ],
    "Style Presets": [
        style_ocean_blue,
        style_forest_green,
        style_sunset_orange,
        style_purple_haze,
        style_cyberpunk,
        style_matrix,
        style_bubblegum,
        style_terminal_classic,
        style_midnight_blue,
        style_creamsicle,
    ],
    "Header Positions": [
        header_outside_top,
        header_inside_left,
        header_outside_left,
        header_inside_right,
        header_outside_right,
        simple_yes_no_borderless,
        confirm_cancel_borderless_with_wrapping,
        confirm_cancel_with_border_not_transient,
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
