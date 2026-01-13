from io import StringIO

import pytest
from rich.console import Console

from get_rich import ShortcutChooser


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


def test_shortcut_chooser_auto_mode_select_by_number():
    """Test auto mode selection using 1-9, 0 shortcuts."""
    reader = FakeReader(["2", "ENTER"])
    chooser = ShortcutChooser(choices=["a", "b", "c"], console=fake_console())

    result = chooser.run(reader=reader)

    assert result == ("b", 1)


def test_shortcut_chooser_auto_mode_select_tenth_with_zero():
    """Test auto mode selection of 10th item with 0."""
    reader = FakeReader(["0", "ENTER"])
    choices = [str(i) for i in range(10)]
    chooser = ShortcutChooser(choices=choices, console=fake_console())

    result = chooser.run(reader=reader)

    assert result == ("9", 9)


def test_shortcut_chooser_custom_keys():
    """Test with custom shortcut keys."""
    reader = FakeReader(["x", "ENTER"])
    chooser = ShortcutChooser(
        choices=["apple", "banana", "cherry"],
        shortcut_keys=["a", "b", "c"],
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    # 'x' doesn't match any key, so it stays on first choice
    assert result == ("apple", 0)


def test_shortcut_chooser_custom_keys_match():
    """Test with custom shortcut keys that match."""
    reader = FakeReader(["b", "ENTER"])
    chooser = ShortcutChooser(
        choices=["apple", "banana", "cherry"],
        shortcut_keys=["a", "b", "c"],
        console=fake_console(),
    )

    result = chooser.run(reader=reader)

    assert result == ("banana", 1)


def test_shortcut_chooser_with_arrow_navigation():
    """Test that arrow keys still work alongside shortcuts."""
    reader = FakeReader(["DOWN_ARROW", "2", "ENTER"])
    chooser = ShortcutChooser(choices=["a", "b", "c"], console=fake_console())

    result = chooser.run(reader=reader)

    # DOWN_ARROW moves to b, then 2 selects b
    assert result == ("b", 1)


def test_shortcut_chooser_too_few_keys_non_strict():
    """Test that too few keys don't raise in non-strict mode."""
    # With 3 choices but only 2 shortcut keys, should use available keys
    chooser = ShortcutChooser(
        choices=["a", "b", "c"],
        shortcut_keys=["x", "y"],
        strict_mode=False,
        console=fake_console(),
    )

    # Should not raise
    assert len(chooser.shortcut_keys) == 2
    assert chooser.shortcut_key_to_index == {"x": 0, "y": 1}


def test_shortcut_chooser_too_many_keys_non_strict():
    """Test that too many keys are ignored in non-strict mode."""
    # With 2 choices but 4 shortcut keys, should use only 2
    chooser = ShortcutChooser(
        choices=["a", "b"],
        shortcut_keys=["a", "b", "c", "d"],
        strict_mode=False,
        console=fake_console(),
    )

    # Should not raise
    assert len(chooser.shortcut_keys) == 2
    assert chooser.shortcut_key_to_index == {"a": 0, "b": 1}


def test_shortcut_chooser_duplicate_keys_non_strict():
    """Test that duplicate keys are tolerated in non-strict mode."""
    # Non-strict: later duplicates overwrite earlier ones
    chooser = ShortcutChooser(
        choices=["a", "b", "c"],
        shortcut_keys=["x", "x", "y"],
        strict_mode=False,
        console=fake_console(),
    )

    # Should not raise
    assert chooser.shortcut_key_to_index["x"] == 1  # Overwritten by second "x"
    assert chooser.shortcut_key_to_index["y"] == 2


def test_shortcut_chooser_too_few_keys_strict():
    """Test that too few keys raise in strict mode."""
    with pytest.raises(ValueError, match="Too few shortcut keys"):
        ShortcutChooser(
            choices=["a", "b", "c"],
            shortcut_keys=["x", "y"],
            strict_mode=True,
            console=fake_console(),
        )


def test_shortcut_chooser_too_many_keys_strict():
    """Test that too many keys raise in strict mode."""
    with pytest.raises(ValueError, match="Too many shortcut keys"):
        ShortcutChooser(
            choices=["a", "b"],
            shortcut_keys=["a", "b", "c", "d"],
            strict_mode=True,
            console=fake_console(),
        )


def test_shortcut_chooser_duplicate_keys_strict():
    """Test that duplicate keys raise in strict mode."""
    with pytest.raises(ValueError, match="Duplicate shortcut keys"):
        ShortcutChooser(
            choices=["a", "b", "c"],
            shortcut_keys=["x", "x", "y"],
            strict_mode=True,
            console=fake_console(),
        )


# ============================================================================
# Styles Tests for ShortcutChooser
# ============================================================================


def test_shortcut_chooser_uses_default_styles():
    """Test that ShortcutChooser applies default styles including shortcut-specific ones."""
    from get_rich.styles import _merge_styles

    chooser = ShortcutChooser(choices=["a", "b", "c"], console=fake_console())
    defaults = _merge_styles()

    # Verify shortcut-specific style is present
    assert chooser.styles.shortcut_prefix_style == defaults.shortcut_prefix_style
    assert chooser.styles.selection_style == defaults.selection_style


def test_shortcut_chooser_applies_custom_styles():
    """Test that ShortcutChooser applies custom style overrides."""
    custom_styles = {
        "shortcut_prefix_style": "bold magenta",
        "selection_style": "bold cyan on black",
    }

    chooser = ShortcutChooser(
        choices=["a", "b"], styles=custom_styles, console=fake_console()
    )

    # Custom styles are applied
    assert chooser.styles.shortcut_prefix_style == "bold magenta"
    assert chooser.styles.selection_style == "bold cyan on black"

    # Default styles still present for non-overridden keys
    from get_rich.styles import _merge_styles

    defaults = _merge_styles()
    assert chooser.styles.header_style == defaults.header_style


# ============================================================================
# Messages Tests for ShortcutChooser
# ============================================================================


def test_shortcut_chooser_uses_default_messages():
    """Test that ShortcutChooser applies default messages."""
    from get_rich.messages import _merge_messages

    chooser = ShortcutChooser(choices=["a", "b", "c"], console=fake_console())
    defaults = _merge_messages()

    # Verify shortcut-specific messages are present
    assert chooser.messages.shortcut_select_range == defaults.shortcut_select_range
    assert chooser.messages.shortcut_select_key == defaults.shortcut_select_key
    assert chooser.messages.nav_instructions == defaults.nav_instructions


def test_shortcut_chooser_applies_custom_messages():
    """Test that ShortcutChooser applies custom message overrides."""
    custom_messages = {
        "shortcut_select_range": "{start} to {end} to pick",
        "shortcut_select_key": "Press a key",
        "nav_instructions": "Navigate and select",
    }

    chooser = ShortcutChooser(
        choices=["a", "b"], messages=custom_messages, console=fake_console()
    )

    assert chooser.messages.shortcut_select_range == "{start} to {end} to pick"
    assert chooser.messages.shortcut_select_key == "Press a key"
    assert chooser.messages.nav_instructions == "Navigate and select"


def test_shortcut_select_range_formatting():
    """Test that shortcut_select_range message is properly formatted."""
    custom_messages = {
        "shortcut_select_range": "Appuyez sur {start}-{end} pour sélectionner",
    }

    chooser = ShortcutChooser(
        choices=["a", "b", "c", "d", "e"],
        messages=custom_messages,
        console=fake_console(),
    )

    # Verify message can be formatted with start/end values
    formatted = chooser.messages.shortcut_select_range.format(start=1, end=5)
    assert formatted == "Appuyez sur 1-5 pour sélectionner"


def test_shortcut_chooser_auto_mode_uses_select_range():
    """Test that auto mode uses shortcut_select_range message."""
    # Auto mode uses shortcut_select_range with the range of available shortcuts
    chooser = ShortcutChooser(choices=["opt1", "opt2", "opt3"], console=fake_console())

    # In auto mode, the footer will use shortcut_select_range
    # We verify the message is present and correctly formatted
    formatted = chooser.messages.shortcut_select_range.format(start=1, end=3)
    assert "to Select" in formatted  # Contains the default message


def test_shortcut_chooser_partial_message_override():
    """Test that partial message updates merge with defaults."""
    partial_messages = {
        "shortcut_select_range": "{start}..{end} picks",
    }

    chooser = ShortcutChooser(
        choices=["a", "b"], messages=partial_messages, console=fake_console()
    )

    # Custom message applied
    assert chooser.messages.shortcut_select_range == "{start}..{end} picks"

    # Other messages still have defaults
    from get_rich.messages import _merge_messages

    defaults = _merge_messages()
    assert chooser.messages.shortcut_select_key == defaults.shortcut_select_key
    assert chooser.messages.nav_instructions == defaults.nav_instructions


def test_shortcut_chooser_style_and_message_together():
    """Test that custom styles and messages work together."""
    custom_styles = {
        "shortcut_prefix_style": "bold yellow",
    }
    custom_messages = {
        "shortcut_select_range": "Pick {start} to {end}",
        "nav_instructions": "Use keyboard to select",
    }

    chooser = ShortcutChooser(
        choices=["a", "b", "c"],
        styles=custom_styles,
        messages=custom_messages,
        console=fake_console(),
    )

    # Both custom styles and messages are applied
    assert chooser.styles.shortcut_prefix_style == "bold yellow"
    assert chooser.messages.shortcut_select_range == "Pick {start} to {end}"
    assert chooser.messages.nav_instructions == "Use keyboard to select"

    # Verify formatting works
    formatted = chooser.messages.shortcut_select_range.format(start=1, end=3)
    assert formatted == "Pick 1 to 3"


# ============================================================================
# Edge Case and Output Verification Tests for ShortcutChooser
# ============================================================================


def test_shortcut_chooser_empty_choices_renders_gracefully():
    from rich.console import Console
    import re

    sio = StringIO()
    console = Console(file=sio, force_terminal=True, color_system=None, width=80)
    chooser = ShortcutChooser(choices=[], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    output = sio.getvalue()
    assert result == (None, None)
    assert "Navigate" in chooser.messages.nav_instructions
    assert re.search(r"\bKey\b|\bSelect\b|\bEnter\b", output)


def test_shortcut_chooser_single_choice_select():
    """Test that ShortcutChooser with one choice can be selected and nav instructions are present in config."""
    console = Console(file=StringIO(), force_terminal=True, color_system=None, width=80)
    chooser = ShortcutChooser(choices=["one"], console=console)
    reader = FakeReader(["ENTER"])
    result = chooser.run(reader=reader)
    assert result == ("one", 0)
    assert "Navigate" in chooser.messages.nav_instructions


# Trivial tests (validation of invalid config) and redundant hook tests are skipped
# in favor of focusing on ShortcutChooser-specific behavior and shortcut functionality
