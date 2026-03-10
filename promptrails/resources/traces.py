from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import Trace
from .base import AsyncBaseResource, BaseResource


class TracesResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        trace_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> PaginatedResponse[Trace]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if trace_id:
            params["trace_id"] = trace_id
        if kind:
            params["kind"] = kind
        body = self._http.get("/api/v1/traces", params=params)
        return PaginatedResponse.from_response(body, Trace.from_dict)

    def get_by_trace_id(self, trace_id: str) -> List[Trace]:
        body = self._http.get(f"/api/v1/traces/{trace_id}")
        data = self._unwrap(body)
        return [
            Trace.from_dict(t) for t in (data if isinstance(data, list) else [data] if data else [])
        ]


class AsyncTracesResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        trace_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> PaginatedResponse[Trace]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if trace_id:
            params["trace_id"] = trace_id
        if kind:
            params["kind"] = kind
        body = await self._http.get("/api/v1/traces", params=params)
        return PaginatedResponse.from_response(body, Trace.from_dict)

    async def get_by_trace_id(self, trace_id: str) -> List[Trace]:
        body = await self._http.get(f"/api/v1/traces/{trace_id}")
        data = self._unwrap(body)
        return [
            Trace.from_dict(t) for t in (data if isinstance(data, list) else [data] if data else [])
        ]
