#!/usr/bin/env python3
"""Test script to demonstrate the new height and max_height behavior."""

from get_rich import Chooser

def test_height_absolute():
    """Test that height is interpreted as absolute height (including borders)."""
    print("\n=== Test 1: height=10 with 3 choices (should pad with blank rows) ===")
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Absolute Height Test",
        height=10,  # Absolute height including borders
        width=40,
    )
    value, index = chooser.run()
    print(f"Selected: {value} (index {index})" if value else "Cancelled")


def test_max_height():
    """Test that max_height constrains but doesn't pad."""
    print("\n=== Test 2: max_height=8 with 3 choices (no padding) ===")
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3"],
        title_text="Max Height Test",
        max_height=8,  # Maximum height constraint
        width=40,
    )
    value, index = chooser.run()
    print(f"Selected: {value} (index {index})" if value else "Cancelled")


def test_many_items_with_height():
    """Test height with many items (should scroll)."""
    print("\n=== Test 3: height=10 with 20 choices (should scroll) ===")
    chooser = Chooser(
        choices=[f"Item {i+1}" for i in range(20)],
        title_text="Scrolling Test",
        height=10,
        width=40,
    )
    value, index = chooser.run()
    print(f"Selected: {value} (index {index})" if value else "Cancelled")


def test_no_height_specified():
    """Test default behavior when neither height nor max_height specified."""
    print("\n=== Test 4: No height specified (should use console height) ===")
    chooser = Chooser(
        choices=[f"Item {i+1}" for i in range(10)],
        title_text="Default Height Test",
        width=40,
    )
    value, index = chooser.run()
    print(f"Selected: {value} (index {index})" if value else "Cancelled")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HEIGHT BEHAVIOR TEST SUITE")
    print("="*60)
    print("\nNew behavior:")
    print("- height: Absolute height including borders, pads with blanks")
    print("- max_height: Maximum constraint, no padding")
    print("- Default: Uses console height as max_height")
    print("="*60)
    
    test_height_absolute()
    test_max_height()
    test_many_items_with_height()
    test_no_height_specified()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")
