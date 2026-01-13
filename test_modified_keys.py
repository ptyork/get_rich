#!/usr/bin/env python3
"""Test script to verify modified keys (shift+arrow, etc.) don't exit the chooser."""

from get_rich import Chooser

def test_modified_keys():
    """
    Test that modified keys (like Shift+Arrow) don't cause premature exit.
    
    Instructions:
    1. Run this script
    2. Try pressing Shift+Up, Shift+Down, Ctrl+Arrow, Alt+Arrow
    3. The chooser should stay active and ignore these keys
    4. Press ESC to exit normally
    5. If it exits immediately on modified keys, the bug is present
    """
    print("\n🔍 Testing modified key handling...")
    print("Try pressing: Shift+Arrow, Ctrl+Arrow, Alt+Arrow, etc.")
    print("The chooser should ignore these and stay active.")
    print("Press ESC to exit normally.\n")
    
    chooser = Chooser(
        choices=["Option 1", "Option 2", "Option 3", "Option 4"],
        title_text="Modified Key Test",
        header_text="Try Shift+Arrow keys - they should be ignored",
    )
    
    value, index = chooser.run()
    
    if value is not None:
        print(f"✅ Selected: {value} (index {index})")
    else:
        print("✅ Cancelled with ESC (as expected)")

if __name__ == "__main__":
    test_modified_keys()
