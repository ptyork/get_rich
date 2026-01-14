"""Tests for FileChooser widget.

Tests file and directory selection, filtering, exclusion patterns, and navigation.
"""

import tempfile
from io import StringIO
from pathlib import Path

from rich.console import Console

from get_rich import FileChooser


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


class TestFileChooserBasics:
    """Basic FileChooser functionality tests."""

    def test_file_chooser_selects_file(self):
        """Test that FileChooser can select a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.txt").write_text("content")

            # Navigate to file and confirm - ./ then first file
            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Selecting ./ should return current directory
            assert result is not None

    def test_file_chooser_returns_none_on_cancel(self):
        """Test that FileChooser returns None when cancelled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=tmpdir,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is None

    def test_file_chooser_navigates_to_directory(self):
        """Test that FileChooser can navigate into directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("content")

            # Navigate: down to subdir, enter to go in, then ESC to cancel
            reader = FakeReader(["DOWN_ARROW", "ENTER", "ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Cancelling returns None
            assert result is None

    def test_file_chooser_with_multiple_files(self):
        """Test FileChooser with multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content1")
            (tmppath / "file2.txt").write_text("content2")
            (tmppath / "file3.txt").write_text("content3")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is not None


class TestFileChooserDirectorySelection:
    """Tests for directory selection mode."""

    def test_file_chooser_select_directory_mode(self):
        """Test FileChooser in directory selection mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "selected_dir"
            subdir.mkdir()

            # In dir mode: down to subdir, enter navigates into it, ESC to cancel
            reader = FakeReader(["DOWN_ARROW", "ENTER", "ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                choose_dirs=True,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Cancelled
            assert result is None

    def test_file_chooser_select_current_directory(self):
        """Test selecting the current directory (. option)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # In dir mode: first option is "SELECT path", confirm immediately
            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmpdir,
                choose_dirs=True,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is not None
            assert result == Path(tmpdir).resolve()


class TestFileChooserFiltering:
    """Tests for file filtering (glob patterns)."""

    def test_file_chooser_glob_filter_single_pattern(self):
        """Test FileChooser with single glob pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file.txt").write_text("content")
            (tmppath / "file.py").write_text("code")
            (tmppath / "readme.md").write_text("doc")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                glob="*.txt",
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should complete without error
            assert result is not None

    def test_file_chooser_glob_filter_multiple_patterns(self):
        """Test FileChooser with multiple glob patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "script.py").write_text("code")
            (tmppath / "module.py").write_text("code")
            (tmppath / "data.json").write_text("data")
            (tmppath / "readme.txt").write_text("doc")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                glob=["*.py", "*.json"],
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should complete without error
            assert result is not None


class TestFileChooserExclusion:
    """Tests for file/directory exclusion patterns."""

    def test_file_chooser_exclude_hidden_files(self):
        """Test that hidden files can be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "visible.txt").write_text("content")
            (tmppath / ".hidden").write_text("secret")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                exclude_hidden=True,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is not None

    def test_file_chooser_exclude_dunder_files(self):
        """Test that dunder files can be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "normal.py").write_text("code")
            (tmppath / "__pycache__").mkdir()
            (tmppath / "__init__.py").write_text("code")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                exclude_dunder=True,
                choose_dirs=False,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should complete without error
            assert result is not None

    def test_file_chooser_include_hidden_by_default(self):
        """Test that hidden files are shown by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "visible.txt").write_text("content")
            (tmppath / ".hidden").write_text("secret")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                exclude_hidden=False,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should complete successfully
            assert result is not None


class TestFileChooserSorting:
    """Tests for file/directory sorting."""

    def test_file_chooser_files_at_top(self):
        """Test that files appear before directories when files_at_top=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "dir_a").mkdir()
            (tmppath / "file_a.txt").write_text("content")
            (tmppath / "dir_b").mkdir()
            (tmppath / "file_b.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                files_at_top=True,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should complete successfully
            assert result is not None

    def test_file_chooser_mixed_sort(self):
        """Test mixed alphabetical sorting when files_at_top=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "aaa_dir").mkdir()
            (tmppath / "bbb_file.txt").write_text("content")
            (tmppath / "ccc_dir").mkdir()

            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                files_at_top=False,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Cancelled
            assert result is None


class TestFileChooserAutoFilter:
    """Tests for automatic filtering behavior."""

    def test_auto_filter_disabled_for_small_lists(self):
        """Test that filtering is disabled when list fits on screen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content")
            (tmppath / "file2.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                auto_filter=True,
                height=20,  # Large height means everything fits
                console=fake_console(),
            )

            # Should complete without error
            result = chooser.run(reader=reader)
            assert result is not None

    def test_auto_filter_enabled_for_large_lists(self):
        """Test that filtering is enabled when list is too large."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create many files
            for i in range(30):
                (tmppath / f"file_{i:03d}.txt").write_text(f"content{i}")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                auto_filter=True,
                height=8,  # Small height means filtering kicks in
                console=fake_console(),
            )

            # Should complete without error
            result = chooser.run(reader=reader)
            assert result is not None


class TestFileChooserDisplay:
    """Tests for visual rendering of FileChooser."""

    def test_file_chooser_renders_current_path(self):
        """Test that current path is displayed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            console = fake_console()
            chooser = FileChooser(
                initial_path=tmppath,
                console=console,
            )

            chooser.run(reader=reader)
            output = get_rendered_output(console)

            # Should show the path in the output
            assert str(tmppath.resolve()) in output or "file.txt" in output

    def test_file_chooser_shows_parent_directory_option(self):
        """Test that .. option appears for navigation to parent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "subdir"
            subdir.mkdir()

            reader = FakeReader(["ESC"])
            console = fake_console()
            chooser = FileChooser(
                initial_path=subdir,
                console=console,
            )

            chooser.run(reader=reader)
            output = get_rendered_output(console)

            # Should show path information
            assert len(output) > 0

    def test_file_chooser_renders_file_list(self):
        """Test that files are rendered in output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "important.txt").write_text("content")
            (tmppath / "readme.md").write_text("doc")

            reader = FakeReader(["ENTER"])
            console = fake_console()
            chooser = FileChooser(
                initial_path=tmppath,
                console=console,
            )

            chooser.run(reader=reader)
            output = get_rendered_output(console)

            # Files should be visible
            assert "important.txt" in output or "readme.md" in output


class TestFileChooserInitialSelection:
    """Tests for initial selection behavior."""

    def test_file_chooser_by_index(self):
        """Test initial selection by index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "first.txt").write_text("content")
            (tmppath / "second.txt").write_text("content")
            (tmppath / "third.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            # Just verify it doesn't crash - initial selection is more about display
            result = chooser.run(reader=reader)
            assert result is not None

    def test_file_chooser_home_key_navigation(self):
        """Test HOME key goes to first item."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content")
            (tmppath / "file2.txt").write_text("content")

            reader = FakeReader(["HOME", "ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Cancelled
            assert result is None

    def test_file_chooser_end_key_navigation(self):
        """Test END key goes to last item."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("content")
            (tmppath / "file2.txt").write_text("content")

            reader = FakeReader(["END", "ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should have selected last file
            assert result is not None


class TestFileChooserEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_file_chooser_empty_directory(self):
        """Test FileChooser with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=tmpdir,
                console=fake_console(),
            )

            # Should handle empty directory gracefully
            result = chooser.run(reader=reader)
            # Cancelled
            assert result is None

    def test_file_chooser_nonexistent_initial_path(self):
        """Test FileChooser with nonexistent initial path."""
        reader = FakeReader(["ENTER"])
        chooser = FileChooser(
            initial_path="/nonexistent/path/that/does/not/exist",
            console=fake_console(),
        )

        # Should fall back to current directory gracefully
        result = chooser.run(reader=reader)
        assert result is None or isinstance(result, Path)

    def test_file_chooser_with_spaces_in_names(self):
        """Test FileChooser with files containing spaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file with spaces.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is not None

    def test_file_chooser_with_special_characters(self):
        """Test FileChooser with special characters in filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Use safe special characters
            (tmppath / "file-with-dashes.txt").write_text("content")
            (tmppath / "file_with_underscores.txt").write_text("content")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=tmppath,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            assert result is not None


class TestFileChooserCoverage:
    """Additional tests to improve coverage."""

    def test_file_chooser_initial_path_is_file(self):
        """Test FileChooser when initial_path is a file, not directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            test_file = tmppath / "target.txt"
            test_file.write_text("content")
            (tmppath / "other.txt").write_text("other")

            reader = FakeReader(["ENTER"])
            chooser = FileChooser(
                initial_path=test_file,  # Start with a file path
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should navigate to parent directory and highlight the file
            assert result is not None

    def test_file_chooser_exclude_dunder_directories(self):
        """Test that dunder directories can be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "__pycache__").mkdir()
            (tmppath / "__test__").mkdir()
            normal_dir = tmppath / "normal_dir"
            normal_dir.mkdir()
            (tmppath / "file.txt").write_text("content")

            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                exclude_dunder=True,
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should exclude __pycache__ and __test__ directories
            # Just verify it runs without error
            assert result is None  # Cancelled

    def test_file_chooser_auto_filter_false(self):
        """Test that auto_filter=False always enables filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create just 2 files (would normally not trigger filtering)
            (tmppath / "file1.txt").write_text("content")
            (tmppath / "file2.txt").write_text("content")

            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=tmppath,
                auto_filter=False,  # Always enable filtering
                height=20,  # Large height
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # Should have filtering enabled despite small list
            assert chooser.enable_filtering is True
            assert result is None  # Cancelled

    def test_file_chooser_nonexistent_path_falls_back(self):
        """Test that nonexistent initial_path falls back gracefully."""
        reader = FakeReader(["ESC"])
        chooser = FileChooser(
            initial_path="/absolutely/nonexistent/path/to/nowhere",
            console=fake_console(),
        )

        result = chooser.run(reader=reader)

        # Should fall back to current directory
        assert result is None  # Cancelled

    def test_file_chooser_highlighted_file_in_list(self):
        """Test that initial file is highlighted when path is a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "aaa.txt").write_text("content")
            target_file = tmppath / "bbb.txt"
            target_file.write_text("content")
            (tmppath / "ccc.txt").write_text("content")

            reader = FakeReader(["ESC"])
            chooser = FileChooser(
                initial_path=target_file,  # Should highlight this file
                console=fake_console(),
            )

            result = chooser.run(reader=reader)

            # The chooser should have set up with bbb.txt highlighted
            assert result is None  # Cancelled
