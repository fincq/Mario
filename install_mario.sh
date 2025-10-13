#!/bin/bash

clear
echo "================================"
echo "        Mario Setup"
echo "================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo
    echo "Please install Python 3:"
    echo "Visit https://python.org"
    echo "Download Python 3.9 or newer"
    echo "Or install via Homebrew: brew install python"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

python_version=$(python3 --version)
echo "$python_version found"
echo

echo "Installing Mario..."
if python3 -m pip install --editable .; then
    echo
    echo "================================"
    echo "   Installation Complete"
    echo "================================"
    echo
    echo "Run Mario with:"
    echo "  mario"
    echo "or"
    echo "  python3 -m mario"
    echo
    echo -n "Press Enter to start Mario now (or Ctrl+C to exit)..."
    read
    echo
    python3 -m mario
else
    echo
    echo "Installation failed"
    echo
    echo "Try: python3 -m pip install --user --editable ."
    echo "Make sure you are in the Mario project folder"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

read -p "Press Enter to exit..."