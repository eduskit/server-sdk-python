from __future__ import annotations

import json
import uuid
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import EduskitError

Fetcher = Callable[[str, str, Dict[str, str], Optional[bytes], int], Tuple[int, Dict[str, str], bytes]]


def _default_fetch(
    url: str,
    method: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout_ms: int,
) -> tuple[int, dict[str, str], bytes]:
    request = Request(url, data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=timeout_ms / 1000) as response:
            return response.status, dict(response.headers.items()), response.read()
    except HTTPError as error:
        return error.code, dict(error.headers.items()), error.read()


class HttpTransport:
    def __init__(
        self,
        *,
        base_url: str,
        app_key: str,
        app_secret: str,
        timeout_ms: int = 10_000,
        lang: str = "zh-CN",
        source: str,
        fetch: Optional[Fetcher] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_key = app_key
        self.app_secret = app_secret
        self.timeout_ms = timeout_ms
        self.lang = lang
        self.source = source
        self.fetch = fetch or _default_fetch
        self.last_trace_id = ""

    def request(self, method: str, path: str, body: Optional[Any] = None) -> Any:
        trace_id = uuid.uuid4().hex[:16]
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-app-key": self.app_key,
            "x-app-secret": self.app_secret,
            "x-lang": self.lang,
            "x-trace-id": trace_id,
        }
        try:
            status, response_headers, raw = self.fetch(
                f"{self.base_url}{path}",
                method,
                headers,
                payload,
                self.timeout_ms,
            )
        except URLError as error:
            raise EduskitError(
                str(error.reason),
                error_code="SDK_NETWORK_ERROR",
                path=path,
                source=self.source,
                trace_id=trace_id,
            ) from error

        text = raw.decode("utf-8") if raw else ""
        data: dict[str, Any] = {}
        if text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as error:
                raise EduskitError(
                    text or f"invalid json (HTTP {status})",
                    status=status,
                    error_code="SDK_INVALID_JSON",
                    path=path,
                    source=self.source,
                    trace_id=trace_id,
                ) from error
            if isinstance(parsed, dict):
                data = parsed
            else:
                data = {"data": parsed}

        header_trace = ""
        for key, value in response_headers.items():
            if key.lower() == "x-trace-id":
                header_trace = value
                break
        self.last_trace_id = str(data.get("traceId") or header_trace or trace_id)

        code = data.get("code")
        if status >= 400 or (code is not None and code != 0):
            raise EduskitError(
                str(data.get("message") or f"HTTP {status}"),
                status=status,
                error_code=str(data.get("errorCode") or f"HTTP_{status}"),
                path=str(data.get("path") or path),
                source=self.source,
                trace_id=self.last_trace_id,
            )
        if "data" in data:
            return data["data"]
        return data
