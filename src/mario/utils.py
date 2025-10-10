"""Utility functions used by Mario."""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable, Mapping, MutableMapping, Sequence


class MarioError(RuntimeError):
    """Base exception."""


class AuthenticationError(MarioError):
    """Raised when authentication fails."""


class ApiResponseError(MarioError):
    """Raised when the API returns an unexpected response."""


@dataclass
class Subject:
    id: str
    name: str


@dataclass
class QuizChoice:
    id: str
    text: str
    is_correct: bool


@dataclass
class QuizQuestion:
    id: str
    prompt: str
    choices: Sequence[QuizChoice]


@dataclass
class Quiz:
    id: str
    course_id: str
    playlist_id: str
    questions: Sequence[QuizQuestion]


def masked_input(prompt: str) -> str:
    try:
        from getpass import getpass
    except ImportError:  # pragma: no cover - Python always ships getpass
        return input(prompt)
    return getpass(prompt)


def random_user_agent() -> str:
    token = secrets.token_hex(8)
    return f"Mario/{token}"


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


def flatten_questions(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, Sequence):
        return []
    for question in questions:
        if not isinstance(question, Mapping):
            continue
        yield question


def generate_content_identifier(user_identifier: str, answer_id: str, question_id: str) -> str:
    material = f"{user_identifier}:{answer_id}:{question_id}".encode("utf8")
    return sha256(material).hexdigest()


def extract_choices(question: Mapping[str, Any]) -> Sequence[QuizChoice]:
    answers = question.get("answers") or []
    result = []
    for answer in answers:
        if not isinstance(answer, Mapping):
            continue
        result.append(
            QuizChoice(
                id=str(answer.get("id")),
                text=str(answer.get("text", "")),
                is_correct=bool(answer.get("isCorrect")),
            )
        )
    return result


def build_question(question: Mapping[str, Any]) -> QuizQuestion:
    choices = extract_choices(question)
    return QuizQuestion(
        id=str(question.get("id")),
        prompt=str(question.get("prompt", "")),
        choices=choices,
    )


def build_quiz(payload: Mapping[str, Any]) -> Quiz:
    meta = payload.get("meta", {})
    return Quiz(
        id=str(payload.get("id")),
        course_id=str(meta.get("courseId", "")),
        playlist_id=str(meta.get("playlistId", "")),
        questions=[build_question(q) for q in flatten_questions(payload)],
    )
