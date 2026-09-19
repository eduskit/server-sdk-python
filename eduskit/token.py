from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict

from .errors import EduskitError


def sign_hs256(app_id: str, app_secret: str, subject: str, issuer: str,
               audience: str, expires_in: int, claims: Dict[str, Any],
               source: str) -> tuple[str, int]:
    if not app_id or not app_secret or not subject:
        raise _error("app_id, app_secret and subject are required", source)
    if not isinstance(expires_in, int) or expires_in < 60 or expires_in > 604800:
        raise _error("expiresIn must be an integer between 60 and 604800", source)
    issued_at = int(time.time())
    expires_at = issued_at + expires_in
    header = _encode({"alg": "HS256", "typ": "JWT"})
    payload = _encode({**claims, "iss": issuer, "aud": audience,
                       "sub": subject, "iat": issued_at, "exp": expires_at})
    content = f"{header}.{payload}"
    signature = _b64(hmac.new(app_secret.encode(), content.encode(), hashlib.sha256).digest())
    return f"{content}.{signature}", expires_at


def iso_time(seconds: int) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _encode(value: Any) -> str:
    return _b64(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode())


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _error(message: str, source: str) -> EduskitError:
    return EduskitError(message, error_code="SDK_TOKEN_INPUT_INVALID", source=source)
