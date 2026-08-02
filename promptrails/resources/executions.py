from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Iterator, Optional

from .._sse import StreamEvent, aiter_sse, iter_sse
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

    def tree(self, execution_id: str) -> AgentExecution:
        """Fetch the execution with its full ``children`` tree populated."""
        body = self._http.get(f"/api/v1/executions/{execution_id}/tree")
        return AgentExecution.from_dict(self._unwrap(body))

    def cancel(self, execution_id: str) -> AgentExecution:
        """Request cooperative cancellation of a running execution."""
        body = self._http.post(f"/api/v1/executions/{execution_id}/cancel", json={})
        return AgentExecution.from_dict(self._unwrap(body))

    def approval_inbox(
        self, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentExecution]:
        """List executions parked at ``waiting_approval``."""
        body = self._http.get(
            "/api/v1/executions/approval-inbox", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, AgentExecution.from_dict)

    def approve(self, execution_id: str, *, reason: Optional[str] = None) -> AgentExecution:
        """Approve a run parked at ``waiting_approval`` and resume it."""
        payload: Dict[str, Any] = {}
        if reason is not None:
            payload["reason"] = reason
        body = self._http.post(f"/api/v1/executions/{execution_id}/approve", json=payload)
        return AgentExecution.from_dict(self._unwrap(body))

    def deny(self, execution_id: str, *, reason: Optional[str] = None) -> AgentExecution:
        """Deny a run parked at ``waiting_approval`` and resume with a denial."""
        payload: Dict[str, Any] = {}
        if reason is not None:
            payload["reason"] = reason
        body = self._http.post(f"/api/v1/executions/{execution_id}/deny", json=payload)
        return AgentExecution.from_dict(self._unwrap(body))

    def stream(self, execution_id: str) -> Iterator[StreamEvent]:
        """Subscribe to the live SSE stream for an execution.

        Useful when the execution was started outside a chat (e.g.
        ``agents.execute``) and the caller wants progressive updates.
        """
        with self._http.stream(
            "GET",
            f"/api/v1/executions/{execution_id}/stream",
        ) as response:
            response.raise_for_status()
            yield from iter_sse(response)


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

    async def tree(self, execution_id: str) -> AgentExecution:
        """Fetch the execution with its full ``children`` tree populated."""
        body = await self._http.get(f"/api/v1/executions/{execution_id}/tree")
        return AgentExecution.from_dict(self._unwrap(body))

    async def cancel(self, execution_id: str) -> AgentExecution:
        """Request cooperative cancellation of a running execution."""
        body = await self._http.post(f"/api/v1/executions/{execution_id}/cancel", json={})
        return AgentExecution.from_dict(self._unwrap(body))

    async def approval_inbox(
        self, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentExecution]:
        """List executions parked at ``waiting_approval``."""
        body = await self._http.get(
            "/api/v1/executions/approval-inbox", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, AgentExecution.from_dict)

    async def approve(self, execution_id: str, *, reason: Optional[str] = None) -> AgentExecution:
        """Approve a run parked at ``waiting_approval`` and resume it."""
        payload: Dict[str, Any] = {}
        if reason is not None:
            payload["reason"] = reason
        body = await self._http.post(f"/api/v1/executions/{execution_id}/approve", json=payload)
        return AgentExecution.from_dict(self._unwrap(body))

    async def deny(self, execution_id: str, *, reason: Optional[str] = None) -> AgentExecution:
        """Deny a run parked at ``waiting_approval`` and resume with a denial."""
        payload: Dict[str, Any] = {}
        if reason is not None:
            payload["reason"] = reason
        body = await self._http.post(f"/api/v1/executions/{execution_id}/deny", json=payload)
        return AgentExecution.from_dict(self._unwrap(body))

    async def stream(self, execution_id: str) -> AsyncIterator[StreamEvent]:
        """Async variant of :meth:`ExecutionsResource.stream`."""
        async with self._http.stream(
            "GET",
            f"/api/v1/executions/{execution_id}/stream",
        ) as response:
            response.raise_for_status()
            async for event in aiter_sse(response):
                yield event
