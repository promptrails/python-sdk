from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import FlowTemplate
from .base import AsyncBaseResource, BaseResource


class TemplatesResource(BaseResource):
    """Flow template operations."""

    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> PaginatedResponse[FlowTemplate]:
        """List flow templates."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        body = self._http.get("/api/v1/templates", params=params)
        return PaginatedResponse.from_response(body, FlowTemplate.from_dict)

    def get(self, template_id: str) -> FlowTemplate:
        """Get a flow template by ID."""
        body = self._http.get(f"/api/v1/templates/{template_id}")
        return FlowTemplate.from_dict(self._unwrap(body))


class AsyncTemplatesResource(AsyncBaseResource):
    """Async flow template operations."""

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> PaginatedResponse[FlowTemplate]:
        """List flow templates."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        body = await self._http.get("/api/v1/templates", params=params)
        return PaginatedResponse.from_response(body, FlowTemplate.from_dict)

    async def get(self, template_id: str) -> FlowTemplate:
        """Get a flow template by ID."""
        body = await self._http.get(f"/api/v1/templates/{template_id}")
        return FlowTemplate.from_dict(self._unwrap(body))
