"""Utility functions used by Mario."""

from __future__ import annotations

import json
import random
import secrets
from hashlib import sha256
from typing import Any, MutableMapping, Sequence


class MarioError(RuntimeError):
    """Base exception."""


class AuthenticationError(MarioError):
    """Raised when authentication fails."""


class ApiResponseError(MarioError):
    """Raised when the API returns an unexpected response."""


def masked_input(prompt: str) -> str:
    try:
        from getpass import getpass
    except ImportError:  # pragma: no cover - Python always ships getpass
        return input(prompt)
    return getpass(prompt)


def random_user_agent() -> str:
    return secrets.choice(
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; rv:132.0) Gecko/20100101 Firefox/132.0",
        ]
    )


def json_preview(data: bytes, limit: int = 200) -> str:
    if not data:
        return "<empty>"
    snippet = data[:limit].decode("utf8", errors="replace")
    return snippet + ("..." if len(data) > limit else "")


def safe_json_loads(data: bytes) -> MutableMapping[str, Any]:
    try:
        return json.loads(data.decode("utf8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
        raise ApiResponseError(f"Unable to parse JSON: {exc}") from exc


def generate_content_identifier(user_identifier: str, answer_id: str, asking_id: str) -> str:
    material = f"{asking_id}{answer_id}{user_identifier}".encode("utf8")
    return sha256(material).hexdigest()


def determine_answer(answer_ids: Sequence[str], percent_correct: int) -> tuple[str, bool]:
    """Select an answer, emulating Solvuria's behaviour."""

    answers = list(answer_ids)

    def is_correct(answer: str) -> bool:
        try:
            computed = int(answer, 16) * 8779302863457884 % 9007199254740991
            return not int(str(int(computed))[-1])
        except (ValueError, OverflowError):
            return False

    percent_correct = max(0, min(100, int(percent_correct)))
    roll = secrets.randbelow(100)

    if roll >= percent_correct:
        wrong_candidates = [candidate for candidate in answers if not is_correct(candidate)]
        if wrong_candidates:
            return secrets.choice(wrong_candidates), False

    for candidate in answers:
        if is_correct(candidate):
            return candidate, True

    return secrets.choice(answers), False


def jitter(value_range: tuple[float, float]) -> float:
    lower, upper = value_range
    if lower > upper:
        lower, upper = upper, lower
    return random.uniform(lower, upper)
