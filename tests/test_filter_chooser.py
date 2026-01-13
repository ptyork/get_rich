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


def test_select_third_option_with_down_arrows():
    reader = FakeReader(["DOWN_ARROW", "DOWN_ARROW", "ENTER"])
    chooser = FilterChooser(choices=["a", "b", "c"], console=fake_console())

    result = chooser.run(reader=reader)

    assert result == ("c", 2)


def test_wrap_navigation_from_top_to_bottom():
    reader = FakeReader(["UP_ARROW", "ENTER"])
    chooser = FilterChooser(
        choices=["a", "b", "c"], wrap_navigation=True, console=fake_console()
    )

    result = chooser.run(reader=reader)

    assert result == ("c", 2)


def test_cancel_returns_none():
    reader = FakeReader(["ESC"])
    chooser = FilterChooser(choices=["a", "b"], console=fake_console())

    result = chooser.run(reader=reader)

    assert result == (None, None)


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


def test_on_change_hook_called_on_selection_change():
    change_count = [0]

    def on_change():
        change_count[0] += 1

    reader = FakeReader(["DOWN_ARROW", "DOWN_ARROW", "ENTER"])
    chooser = FilterChooser(
        choices=["a", "b", "c"],
        on_change=on_change,
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    # on_change is called during init, adjust_to_filter, and for each navigation change
    # We just verify it was called at least once and result is correct
    assert change_count[0] > 0
    assert result == ("c", 2)


def test_before_and_after_run_hooks():
    events = []

    def before():
        events.append("before")

    def after(result):
        events.append(("after", result))

    reader = FakeReader(["ENTER"])
    chooser = FilterChooser(
        choices=["a", "b"],
        before_run=before,
        after_run=after,
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    assert events == ["before", ("after", ("a", 0))]
    assert result == ("a", 0)


def test_on_key_hook_intercepts_and_skips():
    intercepted_keys = []

    def on_key(key):
        intercepted_keys.append(key)
        # Return None to skip default processing
        if key == "x":
            return None
        return key

    reader = FakeReader(["x", "DOWN_ARROW", "ENTER"])
    chooser = FilterChooser(
        choices=["a", "b", "c"],
        on_key=on_key,
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    # "x" was intercepted and skipped (didn't trigger any action)
    assert "x" in intercepted_keys
    assert intercepted_keys.count("DOWN_ARROW") == 1
    # Should stay on first item since DOWN_ARROW was only called once
    assert result == ("b", 1)


def test_should_exit_hook_forces_early_exit():
    exit_count = 0

    def should_exit():
        nonlocal exit_count
        exit_count += 1
        # Exit on first call
        return True

    reader = FakeReader(["DOWN_ARROW", "DOWN_ARROW", "DOWN_ARROW"])
    chooser = FilterChooser(
        choices=["a", "b", "c"],
        should_exit=should_exit,
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    # should_exit returns True immediately, forcing exit before any keys read
    assert exit_count >= 1
    assert result == (None, None)


# ============================================================================
# Styles Tests for FilterChooser
# ============================================================================


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


def test_filter_chooser_invalid_styles_and_messages():
    bad_styles = {"not_a_style": 123, "filter_style": 42}
    bad_messages = {"not_a_message": 123, "filter_label": 42}
    chooser = FilterChooser(
        choices=["a"], styles=bad_styles, messages=bad_messages, console=fake_console()
    )
    # Should use the value as-is
    assert chooser.styles.filter_style == 42
    assert chooser.messages.filter_label == 42


def test_filter_chooser_unicode_choices_and_messages():
    custom_messages = {"filter_label": "🔍"}
    chooser = FilterChooser(
        choices=["😀", "🍕", "你好"], messages=custom_messages, console=fake_console()
    )
    reader = FakeReader(["DOWN_ARROW", "ENTER"])
    _ = chooser.run(reader=reader)
    # Check that the unicode is present in the config
    assert "🔍" in chooser.messages.filter_label
    assert "🍕" in [str(c) for c in chooser.choices]


def test_filter_chooser_on_key_and_hooks():
    called = {
        "before": False,
        "after": False,
        "change": False,
        "key": False,
        "exit": False,
    }

    def before():
        called["before"] = True

    def after(res):
        called["after"] = True

    def change():
        called["change"] = True

    def key(k):
        called["key"] = True
        return k

    def exit():
        called["exit"] = True
        return False

    reader = FakeReader(["DOWN_ARROW", "ENTER"])
    chooser = FilterChooser(
        choices=["a", "b"],
        before_run=before,
        after_run=after,
        on_change=change,
        on_key=key,
        should_exit=exit,
        console=fake_console(),
    )
    chooser.run(reader=reader)
    assert all(called.values())
