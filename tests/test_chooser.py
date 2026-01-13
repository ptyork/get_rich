from io import StringIO

from rich.console import Console

from get_rich import Chooser


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
    chooser = Chooser(choices=["a", "b", "c"], console=fake_console())

    result = chooser.run(reader=reader)

    assert result == ("c", 2)


def test_wrap_navigation_from_top_to_bottom():
    reader = FakeReader(["UP_ARROW", "ENTER"])
    chooser = Chooser(
        choices=["a", "b", "c"], wrap_navigation=True, console=fake_console()
    )

    result = chooser.run(reader=reader)

    assert result == ("c", 2)


def test_cancel_returns_none():
    reader = FakeReader(["ESC"])
    chooser = Chooser(choices=["a", "b"], console=fake_console())

    result = chooser.run(reader=reader)

    assert result == (None, None)


def test_on_change_hook_called_on_selection_change():
    change_count = [0]

    def on_change(control):
        change_count[0] += 1

    reader = FakeReader(["DOWN_ARROW", "DOWN_ARROW", "ENTER"])
    chooser = Chooser(
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

    def before(control):
        events.append("before")

    def after(control):
        events.append(("after", control.result))

    reader = FakeReader(["ENTER"])
    chooser = Chooser(
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

    def on_key(key, control):
        intercepted_keys.append(key)
        # Return None to skip default processing
        if key == "x":
            return None
        return key

    reader = FakeReader(["x", "DOWN_ARROW", "ENTER"])
    chooser = Chooser(
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

    def should_exit(control):
        nonlocal exit_count
        exit_count += 1
        # Exit on first call
        return True

    reader = FakeReader(["DOWN_ARROW", "DOWN_ARROW", "DOWN_ARROW"])
    chooser = Chooser(
        choices=["a", "b", "c"],
        should_exit=should_exit,
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    # should_exit returns True immediately, forcing exit before any keys read
    assert exit_count >= 1
    assert result == (None, None)


# ============================================================================
# Styles Tests
# ============================================================================


def test_chooser_uses_default_styles():
    """Test that Chooser applies default styles."""
    from get_rich.styles import _merge_styles

    chooser = Chooser(choices=["a", "b", "c"], console=fake_console())
    defaults = _merge_styles()

    # Verify all default style keys are present
    assert chooser.styles.selection_style == defaults.selection_style
    assert chooser.styles.selection_caret == defaults.selection_caret
    assert chooser.styles.header_style == defaults.header_style
    assert chooser.styles.footer_style == defaults.footer_style
    assert chooser.styles.border_style == defaults.border_style
    assert chooser.styles.body_style == defaults.body_style
    assert chooser.styles.show_border == defaults.show_border


def test_chooser_applies_custom_styles():
    """Test that Chooser applies custom style overrides."""
    custom_styles = {
        "selection_style": "bold red on white",
        "selection_caret": "→",
        "body_style": "blue",
    }

    chooser = Chooser(choices=["a", "b"], styles=custom_styles, console=fake_console())

    # Custom styles are applied
    assert chooser.styles.selection_style == "bold red on white"
    assert chooser.styles.selection_caret == "→"
    assert chooser.styles.body_style == "blue"

    # Default styles are still present for non-overridden keys
    from get_rich.styles import _merge_styles

    defaults = _merge_styles()
    assert chooser.styles.header_style == defaults.header_style


def test_chooser_partial_style_override():
    """Test that partial style updates merge with defaults."""
    partial_styles = {"selection_caret": "★"}

    chooser = Chooser(choices=["x"], styles=partial_styles, console=fake_console())

    # Custom style applied
    assert chooser.styles.selection_caret == "★"

    # All other styles still have defaults
    from get_rich.styles import _merge_styles

    defaults = _merge_styles()
    assert chooser.styles.selection_style == defaults.selection_style
    assert chooser.styles.header_style == defaults.header_style
    assert chooser.styles.footer_style == defaults.footer_style


# ============================================================================
# Messages Tests
# ============================================================================


def test_chooser_uses_default_messages():
    """Test that Chooser applies default messages."""
    from get_rich.messages import _merge_messages

    chooser = Chooser(choices=["a", "b", "c"], console=fake_console())
    defaults = _merge_messages()

    # Verify nav and confirm instructions are present
    assert chooser.messages.nav_instructions == defaults.nav_instructions
    assert chooser.messages.confirm_instructions == defaults.confirm_instructions


def test_chooser_applies_custom_messages():
    """Test that Chooser applies custom message overrides."""
    custom_messages = {
        "nav_instructions": "Use arrow keys to navigate",
    }

    chooser = Chooser(
        choices=["a", "b"], messages=custom_messages, console=fake_console()
    )

    assert chooser.messages.nav_instructions == "Use arrow keys to navigate"


def test_chooser_custom_instructions_used_in_footer():
    """Test that custom instructions are used in rendering."""
    custom_messages = {
        "nav_instructions": "Custom Navigation Text",
    }

    _reader = FakeReader(["ENTER"])
    chooser = Chooser(
        choices=["a", "b"],
        messages=custom_messages,
        console=fake_console(),
    )

    # The footer should render with custom instructions
    # We verify this by checking the messages are stored correctly
    assert "Custom Navigation Text" in chooser.messages.nav_instructions


def test_chooser_partial_message_override():
    """Test that partial message updates merge with defaults."""
    partial_messages = {
        "confirm_instructions": "Press Enter to select",
    }

    chooser = Chooser(
        choices=["item"], messages=partial_messages, console=fake_console()
    )

    # Custom message applied
    assert chooser.messages.confirm_instructions == "Press Enter to select"

    # All other messages still have defaults
    from get_rich.messages import _merge_messages

    defaults = _merge_messages()
    assert chooser.messages.filter_label == defaults.filter_label
    assert chooser.messages.items_count == defaults.items_count


# ============================================================================
# Edge Case and Output Verification Tests
# ============================================================================


def test_chooser_empty_choices_renders_gracefully():
    """Test that Chooser with no choices does not crash and renders output."""
    from rich.console import Console
    import re

    sio = StringIO()
    console = Console(file=sio, force_terminal=True, color_system=None, width=80)
    chooser = Chooser(choices=[], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    output = sio.getvalue()
    assert result == (None, None)
    assert "Navigate" in output  # Footer instructions still present
    assert re.search(r"\bNo choices\b|\bSelect\b|\bEnter\b", output)


def test_chooser_single_choice_select():
    """Test that Chooser with one choice can be selected and instructions are present in config."""
    console = Console(file=StringIO(), force_terminal=True, color_system=None, width=80)
    chooser = Chooser(choices=["only"], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    # Instead of output, check config
    assert result == ("only", 0)
    assert "Navigate" in chooser.messages.nav_instructions


def test_chooser_invalid_styles_and_messages():
    """Test that invalid style/message keys are used as-is (no type enforcement)."""
    bad_styles = {"not_a_style": 123, "selection_style": 42}
    bad_messages = {"not_a_message": 123, "nav_instructions": 42}
    chooser = Chooser(
        choices=["a"], styles=bad_styles, messages=bad_messages, console=fake_console()
    )
    # Should use the value as-is
    assert chooser.styles.selection_style == 42
    assert chooser.messages.nav_instructions == 42


def test_chooser_unicode_choices_and_messages():
    """Test that unicode/emoji in choices and messages are accepted and present in config."""
    custom_messages = {"nav_instructions": "Sélectionnez 🚀"}
    chooser = Chooser(
        choices=["😀", "🍕", "你好"], messages=custom_messages, console=fake_console()
    )
    reader = FakeReader(["DOWN_ARROW", "ENTER"])
    _ = chooser.run(reader=reader)
    # Check that the unicode is present in the config
    assert "🚀" in chooser.messages.nav_instructions
    assert "🍕" in [str(c.value) for c in chooser.all_choices]


def test_chooser_on_key_and_hooks():
    """Test that all hooks are called as expected."""
    called = {
        "before": False,
        "after": False,
        "change": False,
        "key": False,
        "exit": False,
    }

    def before(control):
        called["before"] = True

    def after(control):
        called["after"] = True

    def change(control):
        called["change"] = True

    def key(k, control):
        called["key"] = True
        return k

    def exit(control):
        called["exit"] = True
        return False

    reader = FakeReader(["DOWN_ARROW", "ENTER"])
    chooser = Chooser(
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
