"""HTTP client for the modern Tassomai API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional, Sequence

from .config import MarioConfig
from .session import SimpleSession
from .utils import (
    ApiResponseError,
    AuthenticationError,
    Quiz,
    Subject,
    build_quiz,
    generate_content_identifier,
    json_preview,
)

LOGGER = logging.getLogger(__name__)


@dataclass
class AuthenticationPayload:
    email: str
    password: str
    device: str = "mario"


class TassomaiClient:
    """High level client used by the CLI."""

    def __init__(self, config: MarioConfig, session: Optional[SimpleSession] = None) -> None:
        self.config = config
        self.session = session or SimpleSession()
        self.session.headers.update(config.default_headers)
        self.user_identifier: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token_value: Optional[str] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _url(self, endpoint: str) -> str:
        return self.config.endpoints.full_url(endpoint)

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        expected_status: Sequence[int] = (200, 201, 204),
        json_payload: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        url = self._url(endpoint)
        LOGGER.debug("%s %s", method, url)
        response = self.session.request(method, url, json=json_payload, params=params, timeout=30)
        if response.status_code not in expected_status:
            preview = json_preview(response.content)
            raise ApiResponseError(
                f"Unexpected response {response.status_code} for {url}: {preview}"
            )
        if response.status_code == 204:
            return {}
        try:
            payload = response.json()
        except ValueError:
            preview = json_preview(response.content)
            raise ApiResponseError(f"Failed to decode JSON from {url}: {preview}")
        user_message = payload.get("user_message")
        if user_message:
            LOGGER.info("Server message: %s", user_message)
        return payload

    def _authorised_request(self, *args: Any, **kwargs: Any) -> MutableMapping[str, Any]:
        if not self.access_token:
            raise AuthenticationError("No access token present")
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        return self._request(*args, **kwargs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def authenticate(self, email: str, password: str) -> None:
        payload = AuthenticationPayload(email=email, password=password)
        response = self._request(
            "POST",
            "login",
            json_payload=payload.__dict__,
        )
        data = response.get("data") or response
        tokens = data.get("tokens") or {}
        self.access_token = tokens.get("access") or tokens.get("token")
        self.refresh_token_value = tokens.get("refresh")
        user = data.get("user") or {}
        self.user_identifier = str(user.get("id") or user.get("identifier") or "")
        if not self.access_token:
            raise AuthenticationError("Login succeeded but no token returned")

    def refresh_token(self) -> None:
        if not self.refresh_token_value:
            raise AuthenticationError("No refresh token available")
        response = self._request(
            "POST",
            "refresh",
            json_payload={"refresh": self.refresh_token_value},
        )
        token = response.get("access") or response.get("token")
        if not token:
            raise AuthenticationError("Token refresh failed")
        self.access_token = token

    def update_last_login(self) -> None:
        try:
            self._authorised_request("POST", "last_login")
        except ApiResponseError as exc:
            LOGGER.warning("Unable to update last login: %s", exc)

    def get_subjects(self) -> Sequence[Subject]:
        payload = self._authorised_request("GET", "subjects")
        disciplines = payload.get("subjects") or payload.get("data") or []
        subjects = []
        for entry in disciplines:
            if not isinstance(entry, Mapping):
                continue
            subjects.append(Subject(id=str(entry.get("id")), name=str(entry.get("name", ""))))
        return subjects

    def get_next_quiz(self, subject_id: str) -> Optional[Mapping[str, Any]]:
        payload = self._authorised_request(
            "GET",
            "next_quiz",
            params={"subjectId": subject_id},
        )
        quizzes = payload.get("quizzes") or payload.get("data")
        if isinstance(quizzes, Sequence):
            return quizzes[0] if quizzes else None
        if isinstance(quizzes, Mapping):
            return quizzes
        return payload.get("quiz")

    def fetch_quiz(self, course_id: str, playlist_id: str) -> Quiz:
        payload = self._authorised_request(
            "POST",
            "fetch_quiz",
            json_payload={"courseId": course_id, "playlistId": playlist_id},
        )
        quiz_payload = payload.get("quiz") or payload
        return build_quiz(quiz_payload)

    def bypass_captcha(self, quiz_id: str) -> None:
        if not self.config.captcha_bypass:
            return
        try:
            self._authorised_request(
                "POST",
                "fetch_quiz",
                json_payload={"quizId": quiz_id, "turnstile": self.config.turnstile_mode},
            )
        except ApiResponseError as exc:
            LOGGER.warning("Captcha bypass failed: %s", exc)

    def post_answer(
        self,
        *,
        answer_id: str,
        question_id: str,
        quiz_id: str,
        is_correct: bool,
    ) -> None:
        if not self.user_identifier:
            raise AuthenticationError("User identifier missing")
        content_id = generate_content_identifier(self.user_identifier, answer_id, question_id)
        payload = {
            "answerId": answer_id,
            "questionId": question_id,
            "quizId": quiz_id,
            "contentId": content_id,
            "isCorrect": is_correct,
        }
        self._authorised_request("POST", "answer", json_payload=payload)
