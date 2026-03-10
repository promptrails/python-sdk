from __future__ import annotations

from typing import Any, Dict, Optional


class PromptRailsError(Exception):
    """Base exception for all PromptRails SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class ValidationError(PromptRailsError):
    """Raised on 400 Bad Request."""

    pass


class UnauthorizedError(PromptRailsError):
    """Raised on 401 Unauthorized."""

    pass


class ForbiddenError(PromptRailsError):
    """Raised on 403 Forbidden."""

    pass


class NotFoundError(PromptRailsError):
    """Raised on 404 Not Found."""

    pass


class RateLimitError(PromptRailsError):
    """Raised on 429 Too Many Requests."""

    pass


class ServerError(PromptRailsError):
    """Raised on 5xx Server Error."""

    pass


_STATUS_MAP = {
    400: ValidationError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: Dict[str, Any]) -> None:
    if 200 <= status_code < 300:
        return
    error_data = body.get("error", {})
    if isinstance(error_data, str):
        message = error_data
        code = None
        details = {}
    else:
        message = error_data.get("message", body.get("message", "Unknown error"))
        code = error_data.get("code")
        details = error_data.get("details", {})
    exc_cls = _STATUS_MAP.get(status_code, ServerError)
    raise exc_cls(
        message=message,
        status_code=status_code,
        code=code,
        details=details,
    )
