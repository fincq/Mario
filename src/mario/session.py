"""A very small HTTP session abstraction using urllib."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional


@dataclass
class SimpleResponse:
    status_code: int
    headers: Mapping[str, str]
    content: bytes

    def json(self) -> MutableMapping[str, Any]:
        return json.loads(self.content.decode("utf8"))


class SimpleSession:
    def __init__(self) -> None:
        self.headers: Dict[str, str] = {}

    def request(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: float = 30.0,
    ) -> SimpleResponse:
        if params:
            query = urllib.parse.urlencode({k: str(v) for k, v in params.items()})
            url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        data: Optional[bytes] = None
        headers = dict(self.headers)
        if json is not None:
            data = json.dumps(json).encode("utf8")
            headers.setdefault("Content-Type", "application/json")
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return SimpleResponse(
                    status_code=response.getcode(),
                    headers=dict(response.headers.items()),
                    content=response.read(),
                )
        except urllib.error.HTTPError as exc:
            return SimpleResponse(
                status_code=exc.code,
                headers=dict(exc.headers.items()) if exc.headers else {},
                content=exc.read() if exc.fp else b"",
            )
