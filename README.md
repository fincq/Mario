# Mario

Mario is a faithful port of the original **Solvuria – Enhance your learning**
script.  It reproduces the familiar terminal flow while upgrading the internals
to work against the latest Tassomai endpoints.

## Features

- Friendly, text-based command line interface
- Solvuria-style timing profiles (Normal, Fast, or custom)
- Automatic token refresh and last-login updates
- Built-in captcha fetch handling when `turnstile_mode` is enabled
- Human-readable debugging messages when the Tassomai API responds unexpectedly

## Installation

```bash
pip install --editable .
```

## Usage

```bash
python -m mario
```

The CLI mirrors the original workflow:

1. Prompts for your Tassomai credentials.
2. Fetches available subjects and lets you pick one.
3. Offers Solvuria's Normal, Fast, or custom timing settings.
4. Repeatedly requests "normal" quizzes and answers each question using the
   Solvuria scoring heuristic.

Run `python -m mario --help` for the small set of command line flags (subject
preselection, single-run mode, and logging level).

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
