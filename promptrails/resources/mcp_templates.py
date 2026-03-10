from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import MCPTemplate, MCPTool
from .base import AsyncBaseResource, BaseResource


class MCPTemplatesResource(BaseResource):
    """MCP template marketplace operations."""

    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[MCPTemplate]:
        """List MCP templates."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if category:
            params["category"] = category
        if type:
            params["type"] = type
        if search:
            params["search"] = search
        if is_active is not None:
            params["is_active"] = is_active
        body = self._http.get("/api/v1/mcp-templates", params=params)
        return PaginatedResponse.from_response(body, MCPTemplate.from_dict)

    def get(self, template_id: str) -> MCPTemplate:
        """Get an MCP template by ID."""
        body = self._http.get(f"/api/v1/mcp-templates/{template_id}")
        return MCPTemplate.from_dict(self._unwrap(body))

    def get_by_slug(self, slug: str) -> MCPTemplate:
        """Get an MCP template by slug."""
        body = self._http.get(f"/api/v1/mcp-templates/slug/{slug}")
        return MCPTemplate.from_dict(self._unwrap(body))

    def install(
        self,
        slug: str,
        *,
        name: str,
        parameters: Optional[Dict[str, str]] = None,
    ) -> MCPTool:
        """Install an MCP template, creating an MCP tool."""
        payload: Dict[str, Any] = {"name": name}
        if parameters is not None:
            payload["parameters"] = parameters
        body = self._http.post(f"/api/v1/mcp-templates/slug/{slug}/install", json=payload)
        return MCPTool.from_dict(self._unwrap(body))


class AsyncMCPTemplatesResource(AsyncBaseResource):
    """Async MCP template marketplace operations."""

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[MCPTemplate]:
        """List MCP templates."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if category:
            params["category"] = category
        if type:
            params["type"] = type
        if search:
            params["search"] = search
        if is_active is not None:
            params["is_active"] = is_active
        body = await self._http.get("/api/v1/mcp-templates", params=params)
        return PaginatedResponse.from_response(body, MCPTemplate.from_dict)

    async def get(self, template_id: str) -> MCPTemplate:
        """Get an MCP template by ID."""
        body = await self._http.get(f"/api/v1/mcp-templates/{template_id}")
        return MCPTemplate.from_dict(self._unwrap(body))

    async def get_by_slug(self, slug: str) -> MCPTemplate:
        """Get an MCP template by slug."""
        body = await self._http.get(f"/api/v1/mcp-templates/slug/{slug}")
        return MCPTemplate.from_dict(self._unwrap(body))

    async def install(
        self,
        slug: str,
        *,
        name: str,
        parameters: Optional[Dict[str, str]] = None,
    ) -> MCPTool:
        """Install an MCP template, creating an MCP tool."""
        payload: Dict[str, Any] = {"name": name}
        if parameters is not None:
            payload["parameters"] = parameters
        body = await self._http.post(f"/api/v1/mcp-templates/slug/{slug}/install", json=payload)
        return MCPTool.from_dict(self._unwrap(body))
