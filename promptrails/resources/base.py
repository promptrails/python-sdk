from __future__ import annotations

from typing import Any, Dict

from .._async_http import AsyncHTTPClient
from .._http import HTTPClient


class BaseResource:
    """Base class for sync resource access."""

    def __init__(self, http: HTTPClient):
        self._http = http

    def _unwrap(self, body: Dict[str, Any]) -> Any:
        return body.get("data", body)


class AsyncBaseResource:
    """Base class for async resource access."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    def _unwrap(self, body: Dict[str, Any]) -> Any:
        return body.get("data", body)
