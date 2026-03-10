from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import AgentExecution
from .base import AsyncBaseResource, BaseResource


class ExecutionsResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AgentExecution]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if session_id:
            params["session_id"] = session_id
        if status:
            params["status"] = status
        body = self._http.get("/api/v1/executions", params=params)
        return PaginatedResponse.from_response(body, AgentExecution.from_dict)

    def get(self, execution_id: str) -> AgentExecution:
        body = self._http.get(f"/api/v1/executions/{execution_id}")
        return AgentExecution.from_dict(self._unwrap(body))


class AsyncExecutionsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AgentExecution]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if session_id:
            params["session_id"] = session_id
        if status:
            params["status"] = status
        body = await self._http.get("/api/v1/executions", params=params)
        return PaginatedResponse.from_response(body, AgentExecution.from_dict)

    async def get(self, execution_id: str) -> AgentExecution:
        body = await self._http.get(f"/api/v1/executions/{execution_id}")
        return AgentExecution.from_dict(self._unwrap(body))
