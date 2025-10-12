#!/usr/bin/env python3
"""Test Mario's input handling without real credentials."""

import sys
from io import StringIO
from src.mario.cli import prompt_email
from src.mario.utils import masked_input

def test_input_handling():
    """Test how Mario handles input prompts."""
    print("Testing email prompt:")
    try:
        # Simulate user input
        old_stdin = sys.stdin
        sys.stdin = StringIO("test@example.com\n")
        email = prompt_email()
        print(f"Email captured: {email}")
        sys.stdin = old_stdin
    except Exception as e:
        print(f"Email prompt error: {e}")
        sys.stdin = old_stdin
    
    print("\nTesting password prompt:")
    try:
        # For password, we can't easily simulate without actual terminal
        print("Password prompt uses masked input (needs real terminal)")
    except Exception as e:
        print(f"Password prompt error: {e}")

if __name__ == "__main__":
    test_input_handling()