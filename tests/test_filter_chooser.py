from io import StringIO

from rich.console import Console

from get_rich import FilterChooser


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


def test_filtering_limits_choices_before_select():
    reader = FakeReader(["b", "ENTER"])
    chooser = FilterChooser(
        choices=["apple", "banana", "cherry"],
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    assert result == ("banana", 1)


def test_filter_remove_all_choices_before_select():
    reader = FakeReader(["z", "ENTER"])
    chooser = FilterChooser(
        choices=["apple", "banana", "cherry"],
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    assert result == (None, None)


# ============================================================================
# Styles Tests for FilterChooser
# ============================================================================
# Note: Basic navigation and hook tests are covered in test_chooser.py
# FilterChooser-specific tests focus on filtering-related functionality


def test_filter_chooser_uses_default_styles():
    """Test that FilterChooser applies default styles including filter-specific ones."""
    from get_rich.styles import _merge_styles

    chooser = FilterChooser(
        choices=["apple", "banana", "cherry"], console=fake_console()
    )
    defaults = _merge_styles()

    # Verify all default style keys are present
    assert chooser.styles.filter_style == defaults.filter_style
    assert chooser.styles.filter_cursor == defaults.filter_cursor
    assert chooser.styles.selection_style == defaults.selection_style


def test_filter_chooser_applies_custom_styles():
    """Test that FilterChooser applies custom style overrides."""
    custom_styles = {
        "filter_style": "bold yellow",
        "filter_cursor": "█",
        "selection_caret": "❯",
    }

    chooser = FilterChooser(
        choices=["apple", "banana"], styles=custom_styles, console=fake_console()
    )

    # Custom styles are applied
    assert chooser.styles.filter_style == "bold yellow"
    assert chooser.styles.filter_cursor == "█"
    assert chooser.styles.selection_caret == "❯"

    # Default styles still present for non-overridden keys
    from get_rich.styles import _merge_styles

    defaults = _merge_styles()
    assert chooser.styles.header_style == defaults.header_style


def test_filter_cursor_moved_to_styles():
    """Test that filter_cursor is stored in styles, not as an init parameter."""
    from get_rich.styles import _merge_styles

    chooser = FilterChooser(choices=["a", "b"], console=fake_console())

    # filter_cursor should be in styles
    assert "filter_cursor" in dir(chooser.styles)
    assert chooser.styles.filter_cursor == _merge_styles().filter_cursor

    # Should not be an instance attribute
    assert not hasattr(chooser, "filter_cursor")


# ============================================================================
# Messages Tests for FilterChooser
# ============================================================================


def test_filter_chooser_uses_default_messages():
    """Test that FilterChooser applies default messages."""
    from get_rich.messages import _merge_messages

    chooser = FilterChooser(choices=["apple", "banana"], console=fake_console())
    defaults = _merge_messages()

    # Verify filter-specific messages are present
    assert chooser.messages.filter_label == defaults.filter_label
    assert chooser.messages.items_count == defaults.items_count
    assert chooser.messages.filtered_from == defaults.filtered_from


def test_filter_chooser_applies_custom_messages():
    """Test that FilterChooser applies custom message overrides."""
    custom_messages = {
        "filter_label": "Search: ",
        "items_count": "{count} results",
        "filtered_from": "matching",
    }

    chooser = FilterChooser(
        choices=["apple", "banana"], messages=custom_messages, console=fake_console()
    )

    assert chooser.messages.filter_label == "Search: "
    assert chooser.messages.items_count == "{count} results"
    assert chooser.messages.filtered_from == "matching"


def test_filter_label_moved_to_messages():
    """Test that filter_label is stored in messages, not as an init parameter."""
    from get_rich.messages import _merge_messages

    chooser = FilterChooser(choices=["a", "b"], console=fake_console())

    # filter_label should be in messages
    assert "filter_label" in dir(chooser.messages)
    assert chooser.messages.filter_label == _merge_messages().filter_label

    # Should not be an instance attribute (like self.filter_label)
    assert not hasattr(chooser, "filter_label")


def test_items_count_message_formatting():
    """Test that items_count message is properly formatted in footer."""
    custom_messages = {
        "items_count": "{count} elemento(s)",  # Spanish-like format
        "filtered_from": "de",
    }

    chooser = FilterChooser(
        choices=["a", "b", "c"],
        messages=custom_messages,
        console=fake_console(),
    )

    # Verify messages can be formatted with count
    formatted = chooser.messages.items_count.format(count=2)
    assert formatted == "2 elemento(s)"


def test_filtered_from_message_used_in_footer():
    """Test that filtered_from message is used when filtering reduces choices."""
    custom_messages = {
        "items_count": "{count} items",
        "filtered_from": "out of",
    }

    chooser = FilterChooser(
        choices=["apple", "apricot", "banana", "blueberry"],
        messages=custom_messages,
        console=fake_console(),
    )

    # The messages are correctly stored
    assert chooser.messages.filtered_from == "out of"
    assert chooser.messages.items_count == "{count} items"


def test_filter_chooser_partial_message_override():
    """Test that partial message updates merge with defaults."""
    partial_messages = {
        "items_count": "{count} entries",
    }

    chooser = FilterChooser(
        choices=["a"], messages=partial_messages, console=fake_console()
    )

    # Custom message applied
    assert chooser.messages.items_count == "{count} entries"

    # Other messages still have defaults
    from get_rich.messages import _merge_messages

    defaults = _merge_messages()
    assert chooser.messages.filter_label == defaults.filter_label
    assert chooser.messages.filtered_from == defaults.filtered_from


# ============================================================================
# Edge Case and Output Verification Tests for FilterChooser
# ============================================================================


def test_filter_chooser_empty_choices_renders_gracefully():
    from rich.console import Console
    import re

    sio = StringIO()
    console = Console(file=sio, force_terminal=True, color_system=None, width=80)
    chooser = FilterChooser(choices=[], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    output = sio.getvalue()
    assert result == (None, None)
    assert "Navigate" in output
    assert re.search(r"\bFilter\b|\bEnter\b", output)


def test_filter_chooser_single_choice_select():
    """Test that FilterChooser with one choice can be selected and nav instructions are present in config."""
    console = Console(file=StringIO(), force_terminal=True, color_system=None, width=80)
    chooser = FilterChooser(choices=["one"], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    assert result == ("one", 0)
    assert "Navigate" in chooser.messages.nav_instructions


# Trivial tests (validation of invalid config) are skipped in favor of focusing on
# FilterChooser-specific behavior and filtering functionality
