from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import CostSummary
from .base import AsyncBaseResource, BaseResource


class CostsResource(BaseResource):
    def get_summary(
        self, *, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> CostSummary:
        params: Dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        body = self._http.get("/api/v1/costs/summary", params=params)
        return CostSummary.from_dict(self._unwrap(body))

    def get_agent_summary(
        self, agent_id: str, *, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> CostSummary:
        params: Dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        body = self._http.get(f"/api/v1/costs/agents/{agent_id}", params=params)
        return CostSummary.from_dict(self._unwrap(body))


class AsyncCostsResource(AsyncBaseResource):
    async def get_summary(
        self, *, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> CostSummary:
        params: Dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        body = await self._http.get("/api/v1/costs/summary", params=params)
        return CostSummary.from_dict(self._unwrap(body))

    async def get_agent_summary(
        self, agent_id: str, *, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> CostSummary:
        params: Dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        body = await self._http.get(f"/api/v1/costs/agents/{agent_id}", params=params)
        return CostSummary.from_dict(self._unwrap(body))
