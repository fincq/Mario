# Mario

Mario is a modern automation client for the Tassomai educational platform.
It provides intelligent quiz completion with realistic human-like timing and
behavior patterns while working with the latest Tassomai API endpoints (v1.23).

## Quick Start

### Easy Installation (Recommended)

**Windows Users:**
1. Download and extract Mario
2. Double-click `install_mario.bat`
3. Follow the prompts - Mario installs and runs automatically!

**Mac/Linux Users:**
1. Download and extract Mario  
2. Double-click `install_mario.sh` (or run `bash install_mario.sh` in Terminal)
3. Follow the prompts - Mario installs and runs automatically!

### Manual Installation

```bash
pip install --editable .
```

## Features

- **Human-like timing** - Realistic delays (1.5-4.0s) that look natural
- **User-controlled accuracy** - Choose your accuracy percentage (1-100%)
- **Professional error messages** with helpful troubleshooting
- **Cross-platform installation** - Easy setup scripts for Windows, Mac, and Linux
- **Modern Tassomai API v1.23** compatibility with updated headers
- **Automatic token refresh** and authentication handling
- **Built-in captcha bypass** for protected quizzes
- **Clean interface** with progress indicators

## Usage

**After installation (using the .bat or .sh scripts), simply run:**

```bash
python -m mario
```

**Command line options:**

```bash
# Run single quiz and exit
python -m mario --once

# Auto-select a specific subject
python -m mario --subject SCIENCE

# Enable debug logging
python -m mario --log-level DEBUG
```

### How Mario Works

1. **Authentication**: Enter your Tassomai email and password
2. **Subject Selection**: Choose from available subjects (auto-detects if only one)
3. **Timing Profile**: Select Human-like, Fast, or Custom timing settings
4. **Accuracy Selection**: Choose your desired accuracy percentage (1-100%)
5. **Automated Quiz Completion**: Mario continuously fetches and completes quizzes
6. **Stop Anytime**: Use Ctrl+C to stop after current operation

### Recommended Settings

- **Timing**: Human-like (1.5-4.0s delays for realistic behavior)
- **Accuracy**: 75-85% (natural progression without being suspicious)
- **Usage**: Don't run 24/7 - take breaks like a real student would

### Command Line Options

- `--once` - Run a single quiz and exit
- `--subject ID` - Auto-select specific subject by ID
- `--config PATH` - Use custom configuration file
- `--log-level LEVEL` - Set logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Configuration

Mario looks for configuration at `~/.mario/config.json`.  A minimal example is
shown below:

```json
{
  "default_headers": {
    "User-Agent": "Mozilla/5.0"
  },
  "turnstile_mode": true
}
```

Custom headers are merged with Mario's defaults, making it easy to experiment
with alternative `User-Agent` values.  Adjust `turnstile_mode` if you need to
disable the captcha fetch helper.

## Troubleshooting

### "Python not found" or "pip not recognized"
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal/command prompt

### Installation fails
- Try running the installation script as administrator (Windows)
- Use `python3` instead of `python` on Mac/Linux
- Check that you're in the correct Mario folder

### Authentication fails
- Double-check your Tassomai email and password
- Make sure you can log in to Tassomai normally in a web browser
- Wait a few minutes if you get rate limiting errors

## Credits

Mario is based on the Solvuria framework, with enhancements for the current Tassomai API (v1.23). The core automation concepts and approach were derived from the original Solvuria project.

## Release Notes

### v1.2.0 - User Experience Update
- **Human-like timing** - Realistic 1.5-4.0s delays instead of suspicious fast timing
- **Separate accuracy selection** (1-100%) for user control
- **Easy installation scripts** - Double-click .bat (Windows) or .sh (Mac/Linux) files
- **Improved error messages** with troubleshooting tips
- **Professional interface** with better progress indicators
- **Enhanced password input** with asterisk display on Windows

### v1.0.0 - Initial Release
- Updated for Tassomai API v1.23 compatibility
- Modern authentication and error handling
