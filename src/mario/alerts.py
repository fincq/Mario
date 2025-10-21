import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

ALERT_URL = "https://raw.githubusercontent.com/fincq/Mario/main/.well-known/mario-alert.json"
CACHE_PATH = Path.home() / ".mario" / "alert_cache.json"
CACHE_TTL_SECONDS = 3600


def _read_cache() -> Optional[dict]:
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf8"))
    except (json.JSONDecodeError, OSError):
        return None
    timestamp = data.get("cached_at")
    if not isinstance(timestamp, (int, float)):
        return None
    if time.time() - float(timestamp) > CACHE_TTL_SECONDS:
        return None
    return data.get("payload")


def _write_cache(payload: dict) -> None:
    try:
        CACHE_PATH.parent.mkdir(exist_ok=True)
        CACHE_PATH.write_text(json.dumps({"cached_at": time.time(), "payload": payload}), encoding="utf8")
    except OSError:
        return


def _fetch_remote_payload() -> Optional[dict]:
    request = urllib.request.Request(ALERT_URL, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            data = json.loads(response.read().decode("utf8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError):
        return None
    if isinstance(data, dict):
        _write_cache(data)
        return data
    return None


def fetch_global_warning() -> Optional[str]:
    payload = _fetch_remote_payload()
    if payload is None:
        payload = _read_cache()
    if not isinstance(payload, dict):
        return None
    active = payload.get("active")
    message = payload.get("message")
    owner = payload.get("owner")
    if active is True and isinstance(message, str) and owner == "fincq":
        return message.strip()
    return None
