from __future__ import annotations

from typing import Optional


class EduskitError(Exception):
    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        error_code: Optional[str] = None,
        trace_id: Optional[str] = None,
        path: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_code = error_code
        self.trace_id = trace_id
        self.path = path
        self.source = source
