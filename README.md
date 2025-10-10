# Mario

Mario is a modernised reimplementation of the original **Solvuria** Tassomai
automation script.  It keeps the ergonomic, quiz-first workflow of Solvuria
while swapping in a configurable HTTP client that understands the newer
Tassomai API surface.

## Features

- Friendly, text-based command line interface
- Modular timing profiles (Normal, Fast, Stealth, or custom)
- Robust JSON decoding with helpful error previews
- Configurable endpoints and headers stored in `~/.mario/config.json`
- Automatic token refresh, last-login updates, and optional captcha bypass hooks

## Installation

```bash
pip install --editable .
```

## Usage

```bash
python -m mario
```

The CLI will prompt for your Tassomai credentials, subject selection, and
timing profile.  Use `--help` to discover advanced options such as
`--profile fast`, `--subject <id>`, or `--once` to complete just a single quiz.

## Configuration

Mario looks for configuration at `~/.mario/config.json`.  A minimal example is
shown below:

```json
{
  "endpoints": {
    "base_url": "https://app.tassomai.com/api/v2"
  },
  "default_headers": {
    "User-Agent": "Mario/0.1"
  },
  "captcha_bypass": true,
  "turnstile_mode": false
}
```

Override the endpoints if Tassomai changes their routing.  The script defaults
to JSON-based responses and will surface preview snippets for debugging if the
server replies unexpectedly.
