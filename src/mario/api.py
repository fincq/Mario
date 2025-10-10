"""HTTP client that mirrors the behaviour of the Solvuria script."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Iterable, Mapping, MutableMapping, Optional

from .config import MarioConfig
from .session import SimpleSession
from .utils import (
    ApiResponseError,
    AuthenticationError,
    generate_content_identifier,
    json_preview,
    random_user_agent,
)

LOGGER = logging.getLogger(__name__)

class TassomaiClient:
    """High level client used by the CLI."""

    CAPABILITIES = {
        "cordovaPlatform": None,
        "image": True,
        "isMobile": False,
        "mathjax": True,
        "wondeReady": True,
    }

    def __init__(
        self,
        config: MarioConfig,
        session: Optional[SimpleSession] = None,
        *,
        user_agent: Optional[str] = None,
    ) -> None:
        self.config = config
        self.session = session or SimpleSession()
        self.session.headers.update(config.default_headers)
        self.session.headers["User-Agent"] = user_agent or random_user_agent()
        self.user_identifier: Optional[str] = None
        self.access_token: Optional[str] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _url(self, path: str) -> str:
        return self.config.url(path)

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        expected_status: Iterable[int] = (200, 201, 204),
        json_payload: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> MutableMapping[str, Any]:
        url = self._url(endpoint)
        LOGGER.debug("%s %s", method, url)
        response = self.session.request(
            method,
            url,
            json=json_payload,
            params=params,
            timeout=30,
            headers=headers,
        )
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
        user_message = payload.get("user_message") if isinstance(payload, Mapping) else None
        if user_message:
            LOGGER.info("Server message: %s", user_message)
        return payload  # type: ignore[return-value]

    def _auth_headers(self, accept_version: bool = False) -> Mapping[str, str]:
        headers = {}
        if self.access_token:
            headers["Authorization"] = self.access_token
        if accept_version:
            headers["Accept"] = "application/json; version=1.20"
        return headers

    def _now_millis(self) -> int:
        return int(time.time_ns() // 1_000_000)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def authenticate(self, email: str, password: str) -> None:
        payload = {
            "capabilities": self.CAPABILITIES,
            "email": email,
            "password": password,
        }
        response = self._request("POST", "/user/login/", json_payload=payload)
        if not isinstance(response, Mapping):
            raise AuthenticationError("Unexpected login response")
        token = response.get("token")
        user = response.get("user") or {}
        if not token:
            raise AuthenticationError("Login succeeded but no token returned")
        self.access_token = f"Bearer {token}"
        self.session.headers["Authorization"] = self.access_token
        self.user_identifier = str(user.get("id") or "")

    def refresh_token(self) -> None:
        if not self.access_token:
            raise AuthenticationError("No token available to refresh")
        token_value = self.access_token.split(" ", 1)[-1]
        response = self._request(
            "POST",
            "/user/token-refresh/",
            json_payload={"token": token_value},
            headers=self._auth_headers(accept_version=True),
        )
        if not isinstance(response, Mapping):
            raise AuthenticationError("Token refresh returned unexpected payload")
        if "user_message" in response and "token" not in response:
            return
        new_token = response.get("token")
        if not new_token:
            raise AuthenticationError("Token refresh failed")
        if new_token != token_value:
            self.access_token = f"Bearer {new_token}"
            self.session.headers["Authorization"] = self.access_token

    def update_last_login(self) -> None:
        if not self.access_token:
            raise AuthenticationError("Not authenticated")
        from datetime import datetime

        payload = {"lastLogin": datetime.now().isoformat()}
        url = "/user/extra/"
        response = self.session.request(
            "POST",
            self._url(url),
            json=payload,
            headers=self._auth_headers(accept_version=True),
        )
        if response.status_code not in (200, 201, 204, 405):
            preview = json_preview(response.content)
            raise ApiResponseError(
                f"Unexpected status updating last login: {response.status_code} {preview}"
            )

    def get_subjects(self) -> Iterable[Mapping[str, Any]]:
        payload = self._request(
            "GET",
            "/user/extra/",
            headers=self._auth_headers(),
        )
        if not isinstance(payload, Mapping):
            return []
        extra = payload.get("extra")
        if isinstance(extra, Mapping):
            disciplines = extra.get("currentDisciplines")
            if isinstance(disciplines, list):
                return disciplines
        return []

    def get_quizzes(self, subject_id: str) -> Iterable[Mapping[str, Any]]:
        params = {"capabilities": json.dumps(self.CAPABILITIES, separators=(",", ":"))}
        endpoint = f"/quiz/next/{subject_id}/"
        payload = self._request("GET", endpoint, params=params, headers=self._auth_headers())
        if isinstance(payload, Mapping):
            if "user_message" in payload:
                LOGGER.info("API message: %s", payload.get("user_message"))
                return []
            if "quizzes" in payload and isinstance(payload["quizzes"], list):
                return payload["quizzes"]
            data = payload.get("data")
            if isinstance(data, Mapping) and isinstance(data.get("quizzes"), list):
                return data.get("quizzes", [])
            if isinstance(data, list):
                return data
        if isinstance(payload, list):
            return payload
        return []

    def fetch_quiz(self, course_id: str, playlist_id: str) -> Mapping[str, Any]:
        payload = {
            "capabilities": self.CAPABILITIES,
            "course": course_id,
            "playlist": playlist_id,
            "requestTime": self._now_millis(),
            "was_recommended": True,
        }
        response = self._request("POST", "/quiz/", json_payload=payload, headers=self._auth_headers())
        if isinstance(response, Mapping):
            return response
        raise ApiResponseError("Quiz response had unexpected format")

    def bypass_captcha(self, quiz_data: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.config.turnstile_mode:
            return quiz_data
        if not quiz_data or not quiz_data.get("turnstile_mode"):
            return quiz_data
        quiz_id = quiz_data.get("quiz_id")
        if not quiz_id:
            return quiz_data
        try:
            response = self._request(
                "POST",
                f"/quiz/fetch/{quiz_id}",
                headers=self._auth_headers(accept_version=True),
            )
        except ApiResponseError as exc:
            LOGGER.warning("Captcha bypass failed: %s", exc)
            return quiz_data
        if isinstance(response, Mapping):
            LOGGER.info("Captcha bypass succeeded for quiz %s", quiz_id)
            return response
        return quiz_data

    def post_answer(
        self,
        *,
        answer_id: str,
        asking_id: str,
    ) -> bool:
        if not self.user_identifier or not self.access_token:
            raise AuthenticationError("User identifier missing")
        content_id = generate_content_identifier(self.user_identifier, answer_id, asking_id)
        payload = {
            "answer_id": answer_id,
            "content_id": content_id,
            "requestTime": self._now_millis(),
        }
        endpoint = f"/answer/{asking_id}/"
        response = self.session.request(
            "POST",
            self._url(endpoint),
            json=payload,
            headers=self._auth_headers(),
            timeout=30,
        )
        if response.status_code != 200:
            preview = json_preview(response.content)
            LOGGER.warning(
                "Answer submission failed with %s: %s", response.status_code, preview
            )
            return False
        return True
