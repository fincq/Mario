# Mario

Credits to Solvuria for

Mario is a modern automation client for the Tassomai educational platform.
It provides intelligent quiz completion with realistic human-like timing and
behavior patterns while working with the latest Tassomai API endpoints (v1.23).

## Credits

Mario is based on the Solvuria framework, with significant modernization and enhancements for the current Tassomai API (v1.23). 
The core automation concepts and approach were derived from the original Solvuria project. (https://github.com/corey-truscott/Solvuria)

## Features

- Clean ASCII art interface with minimal design
- Modern Tassomai API v1.23 compatibility with updated headers
- Configurable timing profiles (Normal, Fast, or custom)  
- Automatic token refresh and authentication handling
- Built-in captcha bypass for protected quizzes
- Graceful shutdown handling (Ctrl+C support)
- Spinning loading indicators for better UX
- Continuous operation until manually stopped
- Human-readable error messages and debugging

## Installation

```bash
pip install --editable .
```

## Usage

```bash
# Install in development mode
pip install --editable .

# Run Mario
python -m mario

# Alternative: use console script after installation
mario

# Run single quiz and exit
python -m mario --once

# Auto-select a specific subject
python -m mario --subject SCIENCE

# Enable debug logging
python -m mario --log-level DEBUG
```

### Workflow

1. **Authentication**: Enter your Tassomai email and password
2. **Subject Selection**: Choose from available subjects (auto-detects if only one)
3. **Timing Profile**: Select Normal, Fast, or Custom timing settings
4. **Automated Quiz Completion**: Mario continuously fetches and completes quizzes
5. **Graceful Shutdown**: Use Ctrl+C to stop after current operation

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

## Release Notes

### v1.0.0 - Stable Release

**New Features:**
- Complete rebranding from Solvuria to Mario
- Modern ASCII art interface with clean, minimal design  
- Updated for Tassomai API v1.23 compatibility
- Added graceful shutdown handling (Ctrl+C support)
- Implemented spinning loading indicators
- Removed dependency on external notification systems

**Technical Improvements:**
- Fixed JSON serialization bug in session handling
- Updated API headers for modern Tassomai authentication
- Simplified codebase by removing complex weekly tracking
- Enhanced error handling and user feedback
- Improved timing profiles for realistic behavior

**Breaking Changes:**
- Removed weekly goal tracking and desktop notifications
- Simplified command line interface
- Updated configuration format

This release focuses on reliability and simplicity, providing a stable automation tool without unnecessary complexity.
