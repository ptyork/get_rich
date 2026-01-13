#!/usr/bin/env python3
"""Test script to verify height calculation is accurate for FileChooser."""

from get_rich import FileChooser, FilterChooser, Chooser

def test_chooser_height():
    """Test basic chooser height calculation."""
    print("\n=== Basic Chooser (3 choices, height=10, bordered) ===")
    chooser = Chooser(
        choices=["A", "B", "C"],
        title_text="Test",
        height=10,
        width=40,
    )
    # Should have exactly 10 rows total including borders
    print(f"Height: {chooser.height}")
    print(f"Has border: {chooser.styles.show_border}")
    print(f"Has title: {chooser.title_text is not None}")
    print(f"Visible count: {chooser._visible_count()}")
    print("Expected: 10 total - 2 (border) - 1 (footer) = 7 visible item rows")
    
def test_filter_chooser_with_filter():
    """Test FilterChooser with filtering enabled."""
    print("\n=== FilterChooser with filtering (3 choices, height=10, bordered) ===")
    chooser = FilterChooser(
        choices=["A", "B", "C"],
        title_text="Test",
        height=10,
        width=40,
        disable_filtering=False,
    )
    print(f"Height: {chooser.height}")
    print(f"Has border: {chooser.styles.show_border}")
    print(f"Has title: {chooser.title_text is not None}")
    print(f"Filtering disabled: {chooser.disable_filtering}")
    print(f"Header rows: {chooser._count_header_rows()}")
    print(f"Visible count: {chooser._visible_count()}")
    print("Expected: 10 total - 2 (border) - 1 (filter row) - 1 (footer) = 6 visible item rows")

def test_filter_chooser_without_filter():
    """Test FilterChooser with filtering disabled (like FileChooser sometimes does)."""
    print("\n=== FilterChooser without filtering (3 choices, height=10, bordered) ===")
    chooser = FilterChooser(
        choices=["A", "B", "C"],
        title_text="Test",
        height=10,
        width=40,
        disable_filtering=True,
    )
    print(f"Height: {chooser.height}")
    print(f"Has border: {chooser.styles.show_border}")
    print(f"Has title: {chooser.title_text is not None}")
    print(f"Filtering disabled: {chooser.disable_filtering}")
    print(f"Header rows: {chooser._count_header_rows()}")
    print(f"Visible count: {chooser._visible_count()}")
    print("Expected: 10 total - 2 (border) - 1 (footer) = 7 visible item rows (same as Chooser)")

def test_file_chooser():
    """Test FileChooser height calculation."""
    print("\n=== FileChooser (height=10, bordered, filtering varies) ===")
    chooser = FileChooser(
        initial_path=".",
        title_text="Test",
        height=10,
        width=40,
    )
    print(f"Height: {chooser.height}")
    print(f"Has border: {chooser.styles.show_border}")
    print(f"Has title: {chooser.title_text is not None}")
    print(f"Filtering disabled: {chooser.disable_filtering}")
    print(f"Header rows: {chooser._count_header_rows()}")
    print(f"Visible count: {chooser._visible_count()}")
    print("Expected: Same as FilterChooser - varies based on whether filtering is disabled")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HEIGHT CALCULATION ACCURACY TEST")
    print("="*70)
    
    test_chooser_height()
    test_filter_chooser_with_filter()
    test_filter_chooser_without_filter()
    test_file_chooser()
    
    print("\n" + "="*70)
    print("All calculations displayed!")
    print("="*70 + "\n")
