from __future__ import annotations

from typing import Any, Dict, Optional

from .classroom import ClassroomClient
from .errors import EduskitError
from .http import Fetcher, HttpTransport
from .whiteboard import WhiteboardClient

__all__ = [
    "Eduskit",
    "EduskitError",
    "ClassroomClient",
    "WhiteboardClient",
]


class Eduskit:
    def __init__(
        self,
        *,
        client: Optional[Dict[str, Any]] = None,
        whiteboard_client: Optional[Dict[str, Any]] = None,
        timeout_ms: int = 10_000,
        lang: str = "zh-CN",
        fetch: Optional[Fetcher] = None,
    ) -> None:
        self._client: Optional[ClassroomClient] = None
        self._whiteboard: Optional[WhiteboardClient] = None
        if client:
            self._client = ClassroomClient(
                HttpTransport(
                    base_url=client["base_url"],
                    app_key=client["app_key"],
                    app_secret=client["app_secret"],
                    timeout_ms=timeout_ms,
                    lang=lang,
                    source="classroom",
                    fetch=fetch,
                ),
                app_id=client["app_id"],
                app_secret=client["app_secret"],
            )
        if whiteboard_client:
            self._whiteboard = WhiteboardClient(
                HttpTransport(
                    base_url=whiteboard_client["base_url"],
                    app_key=whiteboard_client["app_key"],
                    app_secret=whiteboard_client["app_secret"],
                    timeout_ms=timeout_ms,
                    lang=lang,
                    source="whiteboard",
                    fetch=fetch,
                ),
                app_id=whiteboard_client["app_id"],
                app_secret=whiteboard_client["app_secret"],
            )

    @property
    def client(self) -> ClassroomClient:
        if self._client is None:
            raise EduskitError(
                "classroom client is not configured",
                error_code="SDK_CLIENT_NOT_CONFIGURED",
                source="classroom",
            )
        return self._client

    @property
    def whiteboard_client(self) -> WhiteboardClient:
        if self._whiteboard is None:
            raise EduskitError(
                "whiteboard client is not configured",
                error_code="SDK_CLIENT_NOT_CONFIGURED",
                source="whiteboard",
            )
        return self._whiteboard
