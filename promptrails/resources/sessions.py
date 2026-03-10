from __future__ import annotations

from typing import Any, Dict

from ..pagination import PaginatedResponse
from ..types import SessionSummary
from .base import AsyncBaseResource, BaseResource


class SessionsResource(BaseResource):
    def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[SessionSummary]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        body = self._http.get("/api/v1/sessions", params=params)
        return PaginatedResponse.from_response(body, SessionSummary.from_dict)

    def get(self, session_id: str) -> SessionSummary:
        body = self._http.get(f"/api/v1/sessions/{session_id}")
        return SessionSummary.from_dict(self._unwrap(body))


class AsyncSessionsResource(AsyncBaseResource):
    async def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[SessionSummary]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        body = await self._http.get("/api/v1/sessions", params=params)
        return PaginatedResponse.from_response(body, SessionSummary.from_dict)

    async def get(self, session_id: str) -> SessionSummary:
        body = await self._http.get(f"/api/v1/sessions/{session_id}")
        return SessionSummary.from_dict(self._unwrap(body))
