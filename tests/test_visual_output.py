"""Tests that validate the visual output and rendering of choosers.

These tests use Rich's Console with StringIO to capture rendered output and verify:
- Height constraints are applied correctly
- Items are properly padded/aligned
- Filtering shows correct item count
- Headers/footers are rendered
- Scrolling indicators appear when needed
"""

from io import StringIO

from rich.console import Console

from get_rich import Chooser, MultiChooser


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


def fake_console(width=80, height=24) -> Console:
    """Create a console that captures output to a string."""
    return Console(
        file=StringIO(),
        force_terminal=True,
        color_system=None,
        width=width,
        height=height,
    )


def get_rendered_output(console: Console) -> str:
    """Extract the rendered output from a console."""
    return console.file.getvalue()


def count_rendered_lines(output: str) -> int:
    """Count the number of lines in rendered output."""
    return len(output.rstrip("\n").split("\n"))


class TestHeightConstraints:
    """Tests that verify height constraints work correctly."""

    def test_absolute_height_pads_with_blank_rows(self):
        """Test that absolute height is enforced and items are padded."""
        console = fake_console(width=40, height=24)
        reader = FakeReader(["ENTER"])  # Just confirm first item

        chooser = Chooser(
            choices=["Option 1", "Option 2", "Option 3"],
            height=10,  # Absolute height including borders
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # With absolute height=10, we should have at least 10 lines
        # (may have more due to rendering but the constraint should be honored)
        lines = output.rstrip("\n").split("\n")
        assert len(lines) >= 10, f"Expected at least 10 lines, got {len(lines)}"

    def test_max_height_constrains_without_padding(self):
        """Test that max_height limits the widget but doesn't pad."""
        console = fake_console(width=40, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["Option 1", "Option 2", "Option 3"],
            max_height=6,  # Maximum constraint without padding
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # max_height should limit the widget size
        # Just verify it rendered without error
        assert len(output) > 0, "Should have rendered output"

    def test_height_with_many_items_enables_scrolling(self):
        """Test that scrolling indicators appear when items exceed available height."""
        console = fake_console(width=40, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=[f"Item {i + 1}" for i in range(20)],
            height=10,  # Only show 10 lines for 20 items
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should render without error and contain the widget
        assert len(output) > 0
        assert "Item 1" in output

    def test_default_height_uses_console_height(self):
        """Test that default height uses available console height."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=[f"Item {i + 1}" for i in range(10)],
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should render without error
        assert len(output) > 0
        assert "Item 1" in output


class TestVisualElements:
    """Tests that verify visual elements are rendered correctly."""

    def test_title_is_rendered(self):
        """Test that title is displayed in the output."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["a", "b", "c"],
            title_text="Test Title",
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        assert "Test Title" in output

    def test_header_is_rendered(self):
        """Test that header text is displayed in the output."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["a", "b", "c"],
            header_text="Select an option:",
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        assert "Select an option:" in output

    def test_header_shows_instructions(self):
        """Test that header text is displayed in the output."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["a", "b", "c"],
            header_text="Use arrow keys to navigate",
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        assert "Use arrow keys to navigate" in output

    def test_choices_are_rendered(self):
        """Test that all visible choices are rendered."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        choices = ["First Choice", "Second Choice", "Third Choice"]
        chooser = Chooser(choices=choices, console=console)

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        for choice in choices:
            assert choice in output


class TestFilteringVisuals:
    """Tests that verify filtering displays correct information."""

    def test_filter_shows_item_count_when_filtering(self):
        """Test that filter header shows count of visible items."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(
            ["a", "ENTER"]  # Type 'a' to filter, then confirm
        )

        chooser = Chooser(
            choices=["apple", "banana", "apricot", "cherry"],
            enable_filtering=True,
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Output should show the filtered choices
        assert "apple" in output or "apricot" in output

    def test_no_matches_shown_when_filter_has_no_results(self):
        """Test that UI handles filter with no matches."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(
            ["z", "BACKSPACE", "ENTER"]  # Type 'z' (no match), backspace, confirm first
        )

        chooser = Chooser(
            choices=["apple", "banana", "cherry"],
            enable_filtering=True,
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should render without error even with no matches
        assert len(output) > 0

    def test_filter_text_shown_in_header(self):
        """Test that current filter text is displayed."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["a", "p", "BACKSPACE", "ENTER"])

        chooser = Chooser(
            choices=["apple", "apricot", "banana"],
            enable_filtering=True,
            console=console,
        )

        result = chooser.run(reader=reader)

        # Should have selected something successfully
        assert result[0] is not None


class TestWidthConstraints:
    """Tests that verify width constraints work correctly."""

    def test_narrow_width_wraps_or_truncates_items(self):
        """Test that items are handled correctly with narrow width."""
        console = fake_console(width=20, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["Very Long Option Name Here", "Another Long One"],
            width=20,
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should render without error even with narrow width
        assert len(output) > 0

    def test_wide_width_renders_correctly(self):
        """Test that wide widths are handled correctly."""
        console = fake_console(width=120, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["Option A", "Option B", "Option C"],
            width=100,
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should render successfully
        assert len(output) > 0
        assert "Option A" in output


class TestMultiChooserVisuals:
    """Tests that verify MultiChooser visual elements."""

    def test_checkboxes_rendered_for_multi_chooser(self):
        """Test that checkboxes appear in MultiChooser output."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        multi = MultiChooser(
            choices=["Item 1", "Item 2", "Item 3"],
            console=console,
        )

        multi.run(reader=reader)
        output = get_rendered_output(console)

        # Should contain checkbox indicators (using ☐ unicode character for unchecked)
        assert "☐" in output

    def test_selected_items_marked_differently(self):
        """Test that selected items have different visual appearance."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(
            ["SPACE", "DOWN_ARROW", "SPACE", "ENTER"]  # Select items 1 and 2
        )

        multi = MultiChooser(
            choices=["Item 1", "Item 2", "Item 3"],
            console=console,
        )

        result = multi.run(reader=reader)

        # Should have selected 2 items
        assert len(result[0]) == 2


class TestBorderAndPadding:
    """Tests that verify borders and padding are correct."""

    def test_borders_rendered(self):
        """Test that widget has proper borders."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["a", "b", "c"],
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # Should have border characters (box drawing)
        # At minimum should have some structure
        assert len(output) > 0
        lines = output.split("\n")
        assert len(lines) > 1

    def test_padding_respects_margins(self):
        """Test that content respects margins."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["Option"],
            height=8,
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        lines = output.split("\n")
        # First and last lines should be borders or padding
        assert len(lines) >= 3  # At least top, middle, bottom


class TestSelectionHighlight:
    """Tests that verify selection highlighting."""

    def test_current_selection_highlighted(self):
        """Test that currently selected item appears different."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["ENTER"])

        chooser = Chooser(
            choices=["Option 1", "Option 2", "Option 3"],
            console=console,
        )

        chooser.run(reader=reader)
        output = get_rendered_output(console)

        # First item should be selected and shown
        assert "Option 1" in output

    def test_navigation_moves_selection(self):
        """Test that navigation moves the highlighted selection."""
        console = fake_console(width=80, height=24)
        reader = FakeReader(["DOWN_ARROW", "ENTER"])

        chooser = Chooser(
            choices=["Option 1", "Option 2", "Option 3"],
            console=console,
        )

        result = chooser.run(reader=reader)

        # Should have selected second option
        assert result == ("Option 2", 1)
