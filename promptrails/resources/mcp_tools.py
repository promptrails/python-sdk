from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import MCPCallToolResult, MCPDiscoverResult, MCPTool
from .base import AsyncBaseResource, BaseResource


class MCPToolsResource(BaseResource):
    def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[MCPTool]:
        body = self._http.get("/api/v1/mcp-tools", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, MCPTool.from_dict)

    def get(self, tool_id: str) -> MCPTool:
        body = self._http.get(f"/api/v1/mcp-tools/{tool_id}")
        return MCPTool.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        type: str,
        config: Optional[Dict[str, Any]] = None,
        schema: Optional[Dict[str, Any]] = None,
        credential_id: Optional[str] = None,
        template_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> MCPTool:
        payload: Dict[str, Any] = {"name": name, "type": type}
        if config is not None:
            payload["config"] = config
        if schema is not None:
            payload["schema"] = schema
        if credential_id is not None:
            payload["credential_id"] = credential_id
        if template_id is not None:
            payload["template_id"] = template_id
        if status is not None:
            payload["status"] = status
        body = self._http.post("/api/v1/mcp-tools", json=payload)
        return MCPTool.from_dict(self._unwrap(body))

    def update(self, tool_id: str, **kwargs) -> MCPTool:
        body = self._http.patch(f"/api/v1/mcp-tools/{tool_id}", json=kwargs)
        return MCPTool.from_dict(self._unwrap(body))

    def delete(self, tool_id: str) -> None:
        self._http.delete(f"/api/v1/mcp-tools/{tool_id}")

    def discover_tools(self, tool_id: str) -> MCPDiscoverResult:
        """Discover available sub-tools for an MCP tool."""
        body = self._http.post(f"/api/v1/mcp-tools/{tool_id}/discover")
        return MCPDiscoverResult.from_dict(self._unwrap(body))

    def call_tool(
        self,
        tool_id: str,
        *,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> MCPCallToolResult:
        """Execute a tool call with the provided arguments."""
        payload: Dict[str, Any] = {"tool_name": tool_name}
        if arguments is not None:
            payload["arguments"] = arguments
        body = self._http.post(f"/api/v1/mcp-tools/{tool_id}/call", json=payload)
        return MCPCallToolResult.from_dict(self._unwrap(body))


class AsyncMCPToolsResource(AsyncBaseResource):
    async def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[MCPTool]:
        body = await self._http.get("/api/v1/mcp-tools", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, MCPTool.from_dict)

    async def get(self, tool_id: str) -> MCPTool:
        body = await self._http.get(f"/api/v1/mcp-tools/{tool_id}")
        return MCPTool.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        type: str,
        config: Optional[Dict[str, Any]] = None,
        schema: Optional[Dict[str, Any]] = None,
        credential_id: Optional[str] = None,
        template_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> MCPTool:
        payload: Dict[str, Any] = {"name": name, "type": type}
        if config is not None:
            payload["config"] = config
        if schema is not None:
            payload["schema"] = schema
        if credential_id is not None:
            payload["credential_id"] = credential_id
        if template_id is not None:
            payload["template_id"] = template_id
        if status is not None:
            payload["status"] = status
        body = await self._http.post("/api/v1/mcp-tools", json=payload)
        return MCPTool.from_dict(self._unwrap(body))

    async def update(self, tool_id: str, **kwargs) -> MCPTool:
        body = await self._http.patch(f"/api/v1/mcp-tools/{tool_id}", json=kwargs)
        return MCPTool.from_dict(self._unwrap(body))

    async def delete(self, tool_id: str) -> None:
        await self._http.delete(f"/api/v1/mcp-tools/{tool_id}")

    async def discover_tools(self, tool_id: str) -> MCPDiscoverResult:
        """Discover available sub-tools for an MCP tool."""
        body = await self._http.post(f"/api/v1/mcp-tools/{tool_id}/discover")
        return MCPDiscoverResult.from_dict(self._unwrap(body))

    async def call_tool(
        self,
        tool_id: str,
        *,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> MCPCallToolResult:
        """Execute a tool call with the provided arguments."""
        payload: Dict[str, Any] = {"tool_name": tool_name}
        if arguments is not None:
            payload["arguments"] = arguments
        body = await self._http.post(f"/api/v1/mcp-tools/{tool_id}/call", json=payload)
        return MCPCallToolResult.from_dict(self._unwrap(body))
