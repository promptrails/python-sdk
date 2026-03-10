from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import DashboardMetrics
from .base import AsyncBaseResource, BaseResource


class DashboardResource(BaseResource):
    def get_metrics(self, *, days: Optional[int] = None) -> DashboardMetrics:
        params: Dict[str, Any] = {}
        if days is not None:
            params["days"] = days
        body = self._http.get("/api/v1/dashboard/metrics", params=params)
        return DashboardMetrics.from_dict(self._unwrap(body))


class AsyncDashboardResource(AsyncBaseResource):
    async def get_metrics(self, *, days: Optional[int] = None) -> DashboardMetrics:
        params: Dict[str, Any] = {}
        if days is not None:
            params["days"] = days
        body = await self._http.get("/api/v1/dashboard/metrics", params=params)
        return DashboardMetrics.from_dict(self._unwrap(body))
