from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import Trace, TraceSummary
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

    def get_summary(self, **filters: Any) -> TraceSummary:
        """Aggregate statistics over a filtered set of traces.

        Accepts the same filters as ``list`` plus ``date_from`` / ``date_to``,
        ``status``, ``level``, ``model_name``, ``agent_id``, ``session_id``,
        ``execution_id`` and similar query parameters.
        """
        params = {k: v for k, v in filters.items() if v is not None}
        body = self._http.get("/api/v1/traces/summary", params=params)
        return TraceSummary.from_dict(self._unwrap(body))

    def pii_report(self, **filters: Any) -> Dict[str, Any]:
        """PII-masking report over a filtered set of traces."""
        params = {k: v for k, v in filters.items() if v is not None}
        body = self._http.get("/api/v1/traces/pii-report", params=params)
        return self._unwrap(body)

    def ingest(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest up to 1000 raw spans in one request."""
        body = self._http.post("/api/v1/traces/ingest", json={"spans": spans})
        return self._unwrap(body)


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

    async def get_summary(self, **filters: Any) -> TraceSummary:
        """Async variant of :meth:`TracesResource.get_summary`."""
        params = {k: v for k, v in filters.items() if v is not None}
        body = await self._http.get("/api/v1/traces/summary", params=params)
        return TraceSummary.from_dict(self._unwrap(body))

    async def pii_report(self, **filters: Any) -> Dict[str, Any]:
        """Async variant of :meth:`TracesResource.pii_report`."""
        params = {k: v for k, v in filters.items() if v is not None}
        body = await self._http.get("/api/v1/traces/pii-report", params=params)
        return self._unwrap(body)

    async def ingest(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest up to 1000 raw spans in one request."""
        body = await self._http.post("/api/v1/traces/ingest", json={"spans": spans})
        return self._unwrap(body)
