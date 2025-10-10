"""Configuration helpers for Mario."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, MutableMapping

DEFAULT_CONFIG_PATH = Path.home() / ".mario" / "config.json"


@dataclass
class EndpointConfig:
    """Configuration container for Tassomai endpoints."""

    base_url: str = "https://app.tassomai.com/api/v2"
    login: str = "/auth/login/"
    refresh: str = "/auth/token/refresh/"
    last_login: str = "/user/last-login/"
    subjects: str = "/user/subjects/"
    next_quiz: str = "/quiz/next/"
    fetch_quiz: str = "/quiz/fetch/"
    answer: str = "/quiz/answer/"

    def full_url(self, endpoint: str) -> str:
        endpoint = getattr(self, endpoint)
        return f"{self.base_url}{endpoint}" if endpoint.startswith("/") else endpoint


@dataclass
class MarioConfig:
    """High level configuration for the Mario client."""

    endpoints: EndpointConfig = field(default_factory=EndpointConfig)
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mario/0.1 (https://github.com/)",
        }
    )
    turnstile_mode: bool = False
    captcha_bypass: bool = True

    @classmethod
    def load(cls, path: Path | None = None) -> "MarioConfig":
        """Load configuration from *path* if it exists."""

        path = path or DEFAULT_CONFIG_PATH
        if not path.exists():
            return cls()

        with path.open("r", encoding="utf8") as handle:
            data: MutableMapping[str, Any] = json.load(handle)

        endpoints = EndpointConfig(**data.get("endpoints", {}))
        headers = data.get("default_headers") or {}
        turnstile_mode = bool(data.get("turnstile_mode", False))
        captcha_bypass = bool(data.get("captcha_bypass", True))

        return cls(
            endpoints=endpoints,
            default_headers={**cls().default_headers, **headers},
            turnstile_mode=turnstile_mode,
            captcha_bypass=captcha_bypass,
        )

    def save(self, path: Path | None = None) -> None:
        path = path or DEFAULT_CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf8") as handle:
            json.dump(
                {
                    "endpoints": self.endpoints.__dict__,
                    "default_headers": self.default_headers,
                    "turnstile_mode": self.turnstile_mode,
                    "captcha_bypass": self.captcha_bypass,
                },
                handle,
                indent=2,
            )


def resolve_config(path: str | os.PathLike[str] | None = None) -> MarioConfig:
    """Return the active configuration, optionally loaded from *path*."""

    config_path = Path(path) if path else None
    return MarioConfig.load(config_path)
