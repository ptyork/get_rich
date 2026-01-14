from io import StringIO

from rich.console import Console

from get_rich import MultiChooser


class FakeReader:
    """Deterministic key reader for tests."""

    def __init__(self, keys):
        self._keys = list(keys)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read_key(self):
        if not self._keys:
            raise AssertionError("Reader exhausted before chooser exited")
        return self._keys.pop(0)


def fake_console() -> Console:
    return Console(file=StringIO(), force_terminal=True, color_system=None, width=80)


# ============================================================================
# Basic Selection Tests
# ============================================================================


def test_multi_chooser_select_single_with_space():
    """Test selecting a single item with space bar."""
    reader = FakeReader(["SPACE", "ENTER"])
    chooser = MultiChooser(choices=["a", "b", "c"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    assert indices == [0]
    assert [str(v) for v in values] == ["a"]


def test_multi_chooser_select_multiple_with_space():
    """Test selecting multiple items with space bar."""
    reader = FakeReader(
        ["SPACE", "DOWN_ARROW", "SPACE", "DOWN_ARROW", "SPACE", "ENTER"]
    )
    chooser = MultiChooser(choices=["a", "b", "c"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    # Selected indices 0, 1, 2
    assert set(indices) == {0, 1, 2}
    assert set(str(v) for v in values) == {"a", "b", "c"}


def test_multi_chooser_toggle_selection():
    """Test toggling selection on/off with space bar."""
    reader = FakeReader(["SPACE", "SPACE", "ENTER"])
    chooser = MultiChooser(choices=["a", "b", "c"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    # Selected then deselected
    assert indices is None
    assert values is None


def test_multi_chooser_select_with_navigation():
    """Test selecting items while navigating."""
    reader = FakeReader(
        ["SPACE", "DOWN_ARROW", "DOWN_ARROW", "SPACE", "UP_ARROW", "SPACE", "ENTER"]
    )
    chooser = MultiChooser(choices=["x", "y", "z"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    # Selected x (0), z (2), y (1) = {0, 1, 2} sorted
    assert set(indices) == {0, 1, 2}


def test_multi_chooser_cancel_returns_none():
    """Test that ESC returns None for both values and indices."""
    reader = FakeReader(["SPACE", "ESC"])
    chooser = MultiChooser(choices=["a", "b"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    assert values is None
    assert indices is None


def test_multi_chooser_empty_selection_returns_none():
    """Test that confirming with no selection returns None."""
    reader = FakeReader(["ENTER"])
    chooser = MultiChooser(choices=["a", "b", "c"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    assert values is None
    assert indices is None


# ============================================================================
# Pre-selection Tests
# ============================================================================


def test_multi_chooser_pre_selected_by_index():
    """Test initializing with pre-selected items by index."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        selected_indices=[0, 2],
        console=fake_console(),
    )
    reader = FakeReader(["ENTER"])

    values, indices = chooser.run(reader=reader)

    assert set(indices) == {0, 2}
    assert set(str(v) for v in values) == {"a", "c"}


def test_multi_chooser_pre_selected_by_value():
    """Test initializing with pre-selected items by value."""
    chooser = MultiChooser(
        choices=["apple", "banana", "cherry"],
        selected_values=["apple", "cherry"],
        console=fake_console(),
    )
    reader = FakeReader(["ENTER"])

    values, indices = chooser.run(reader=reader)

    assert set(indices) == {0, 2}
    assert set(str(v) for v in values) == {"apple", "cherry"}


def test_multi_chooser_deselect_pre_selected():
    """Test deselecting items that were pre-selected."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        selected_indices=[0, 1, 2],
        console=fake_console(),
    )
    reader = FakeReader(["SPACE", "DOWN_ARROW", "SPACE", "ENTER"])

    values, indices = chooser.run(reader=reader)

    # Deselected a and b, only c remains
    assert indices == [2]
    assert [str(v) for v in values] == ["c"]


# ============================================================================
# Validation Tests - Min Selected
# ============================================================================


def test_multi_chooser_min_selected_constraint():
    """Test that min_selected validation prevents confirming with too few."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        min_selected=2,
        console=fake_console(),
    )
    # Try to confirm with only 1 selected, dismiss error, then ESC to exit
    reader = FakeReader(["SPACE", "ENTER", "UP_ARROW", "ESC"])

    values, indices = chooser.run(reader=reader)

    # Validation prevented confirmation, ESC cancels
    assert values is None
    assert indices is None


def test_multi_chooser_min_selected_passes():
    """Test that min_selected validation passes when met."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        min_selected=2,
        console=fake_console(),
    )
    reader = FakeReader(["SPACE", "DOWN_ARROW", "SPACE", "ENTER"])

    values, indices = chooser.run(reader=reader)

    assert len(indices) == 2
    assert set(indices) == {0, 1}


# ============================================================================
# Validation Tests - Max Selected
# ============================================================================


def test_multi_chooser_max_selected_constraint():
    """Test that max_selected validation prevents selecting too many."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        max_selected=2,
        console=fake_console(),
    )
    # Try to select all 3, dismiss error, then ESC to exit
    reader = FakeReader(
        [
            "SPACE",
            "DOWN_ARROW",
            "SPACE",
            "DOWN_ARROW",
            "SPACE",
            "ENTER",
            "UP_ARROW",
            "ESC",
        ]
    )

    values, indices = chooser.run(reader=reader)

    # Validation prevented confirmation, ESC cancels
    assert values is None
    assert indices is None


def test_multi_chooser_max_selected_passes():
    """Test that max_selected validation passes when met."""
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        max_selected=2,
        console=fake_console(),
    )
    reader = FakeReader(["SPACE", "DOWN_ARROW", "SPACE", "ENTER"])

    values, indices = chooser.run(reader=reader)

    assert len(indices) == 2


# ============================================================================
# Validation Tests - Range (Min and Max)
# ============================================================================


def test_multi_chooser_range_constraint_too_few():
    """Test range validation with too few selections."""
    chooser = MultiChooser(
        choices=["a", "b", "c", "d"],
        min_selected=2,
        max_selected=3,
        console=fake_console(),
    )
    # Try with only 1, dismiss error, then ESC to exit
    reader = FakeReader(["SPACE", "ENTER", "UP_ARROW", "ESC"])

    values, indices = chooser.run(reader=reader)

    # Validation prevented confirmation, ESC cancels
    assert values is None
    assert indices is None


def test_multi_chooser_range_constraint_too_many():
    """Test range validation with too many selections."""
    chooser = MultiChooser(
        choices=["a", "b", "c", "d"],
        min_selected=2,
        max_selected=3,
        console=fake_console(),
    )
    # Try to select all 4, dismiss error, then ESC to exit
    reader = FakeReader(
        [
            "SPACE",
            "DOWN_ARROW",
            "SPACE",
            "DOWN_ARROW",
            "SPACE",
            "DOWN_ARROW",
            "SPACE",
            "ENTER",
            "UP_ARROW",
            "ESC",
        ]
    )

    values, indices = chooser.run(reader=reader)

    # Validation prevented confirmation, ESC cancels
    assert values is None
    assert indices is None


def test_multi_chooser_range_constraint_passes():
    """Test range validation when within bounds."""
    chooser = MultiChooser(
        choices=["a", "b", "c", "d"],
        min_selected=2,
        max_selected=3,
        console=fake_console(),
    )
    # Select 2
    reader = FakeReader(["SPACE", "DOWN_ARROW", "SPACE", "ENTER"])

    values, indices = chooser.run(reader=reader)

    assert len(indices) == 2
    assert set(indices) == {0, 1}


# ============================================================================
# Hooks Tests
# ============================================================================


def test_multi_chooser_on_change_hook_on_space():
    """Test that on_change hook is called when toggling with space."""
    change_count = [0]

    def on_change(control):
        change_count[0] += 1

    reader = FakeReader(["SPACE", "SPACE", "ENTER"])
    chooser = MultiChooser(
        choices=["a", "b"], on_change=on_change, console=fake_console()
    )

    chooser.run(reader=reader)

    # Called on init + 2 space presses
    assert change_count[0] >= 2


def test_multi_chooser_before_after_run_hooks():
    """Test before_run and after_run hooks are called."""
    events = []

    def before(control):
        events.append("before")

    def after(control):
        events.append(("after", control.result))

    reader = FakeReader(["SPACE", "ENTER"])
    chooser = MultiChooser(
        choices=["a", "b"],
        before_run=before,
        after_run=after,
        console=fake_console(),
    )

    chooser.run(reader=reader)

    assert events[0] == "before"
    assert events[1][0] == "after"
    assert [str(v) for v in events[1][1][0]] == ["a"]  # values
    assert events[1][1][1] == [0]  # indices


def test_multi_chooser_on_confirm_hook():
    """Test on_confirm hook controls whether selection is accepted."""

    def on_confirm(control):
        # Check which items are currently selected
        current_selected = {c.index for c in control.all_choices if c.is_selected}
        # Reject selections without item at index 1
        if 1 not in current_selected:
            return False
        return True

    reader = FakeReader(
        [
            "SPACE",  # Select index 0
            "ENTER",  # Try to confirm (should be rejected)
            "DOWN_ARROW",
            "SPACE",  # Select index 1
            "ENTER",  # Try again (should be accepted)
        ]
    )
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        on_confirm=on_confirm,
        console=fake_console(),
    )

    _, indices = chooser.run(reader=reader)

    assert set(indices) == {0, 1}


# ============================================================================
# Styles and Messages Tests
# ============================================================================


def test_multi_chooser_uses_default_styles():
    """Test that MultiChooser applies default styles including checkboxes."""
    from get_rich.styles import _merge_styles

    chooser = MultiChooser(choices=["a", "b"], console=fake_console())
    defaults = _merge_styles()

    assert chooser.styles.checkbox_checked == defaults.checkbox_checked
    assert chooser.styles.checkbox_unchecked == defaults.checkbox_unchecked


def test_multi_chooser_custom_checkbox_styles():
    """Test custom checkbox characters."""
    custom_styles = {
        "checkbox_checked": "[✓]",
        "checkbox_unchecked": "[ ]",
    }
    chooser = MultiChooser(
        choices=["a", "b"], styles=custom_styles, console=fake_console()
    )

    assert chooser.styles.checkbox_checked == "[✓]"
    assert chooser.styles.checkbox_unchecked == "[ ]"


def test_multi_chooser_validation_messages():
    """Test that validation error messages use message config."""
    custom_messages = {
        "min_selected_error": "Need at least {min}",
        "max_selected_error": "Too many, max {max}",
        "range_selected_error": "Pick {min}-{max}",
    }
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        min_selected=2,
        messages=custom_messages,
        console=fake_console(),
    )

    # The error message should use the custom format
    error = chooser._validate_selection()
    assert error is not None
    assert "Need at least" in error


# ============================================================================
# Edge Cases
# ============================================================================


def test_multi_chooser_wrap_navigation():
    """Test that wrap_navigation works in MultiChooser."""
    reader = FakeReader(["UP_ARROW", "SPACE", "ENTER"])
    chooser = MultiChooser(
        choices=["a", "b", "c"],
        wrap_navigation=True,
        console=fake_console(),
    )

    values, indices = chooser.run(reader=reader)

    # UP from position 0 should wrap to last item (index 2)
    assert indices == [2]
    assert [str(v) for v in values] == ["c"]


def test_multi_chooser_single_choice():
    """Test MultiChooser with single choice."""
    reader = FakeReader(["SPACE", "ENTER"])
    chooser = MultiChooser(choices=["only"], console=fake_console())

    values, indices = chooser.run(reader=reader)

    assert [str(v) for v in values] == ["only"]
    assert indices == [0]


def test_multi_chooser_many_choices():
    """Test MultiChooser with many choices."""
    many_choices = [f"item_{i}" for i in range(100)]
    # Space to select item 0, then down-arrow 5 times, then space to select item 5
    reader = FakeReader(["SPACE"] + ["DOWN_ARROW"] * 5 + ["SPACE", "ENTER"])
    chooser = MultiChooser(choices=many_choices, console=fake_console())

    values, indices = chooser.run(reader=reader)

    assert set(indices) == {0, 5}
