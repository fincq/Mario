"""Configuration helpers for Mario."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

DEFAULT_CONFIG_PATH = Path.home() / ".mario" / "config.json"


@dataclass
class MarioConfig:
    """High level configuration for the Mario client."""

    base_url: str = "https://kolin.tassomai.com/api"
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://app.tassomai.com",
            "Referer": "https://app.tassomai.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
    )
    turnstile_mode: bool = True

    def url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def save(self, path: Path | None = None) -> None:
        path = path or DEFAULT_CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf8") as handle:
            json.dump(
                {
                    "base_url": self.base_url,
                    "default_headers": self.default_headers,
                    "turnstile_mode": self.turnstile_mode,
                },
                handle,
                indent=2,
            )

    @classmethod
    def load(cls, path: Path | None = None) -> "MarioConfig":
        path = path or DEFAULT_CONFIG_PATH
        if not path or not path.exists():
            return cls()
        with path.open("r", encoding="utf8") as handle:
            data = json.load(handle)
        base_url = data.get("base_url", cls().base_url)
        headers = {**cls().default_headers, **data.get("default_headers", {})}
        turnstile_mode = bool(data.get("turnstile_mode", True))
        return cls(base_url=base_url, default_headers=headers, turnstile_mode=turnstile_mode)


def resolve_config(path: str | os.PathLike[str] | None = None) -> MarioConfig:
    config_path = Path(path) if path else None
    return MarioConfig.load(config_path)
