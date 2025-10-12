#!/usr/bin/env python3
"""Test script to analyze Tassomai API responses without credentials."""

import json
from src.mario.api import TassomaiClient
from src.mario.config import resolve_config

def test_api_structure():
    """Test what the API expects and returns."""
    config = resolve_config()
    client = TassomaiClient(config)
    
    # Try to see what happens with empty/invalid credentials
    try:
        client.authenticate("", "")
    except Exception as e:
        print(f"Empty credentials error: {e}")
    
    try:
        client.authenticate("test@example.com", "wrongpassword")
    except Exception as e:
        print(f"Wrong credentials error: {e}")

if __name__ == "__main__":
    test_api_structure()