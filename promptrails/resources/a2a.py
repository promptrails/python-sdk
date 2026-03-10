from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import A2AAgentCard, A2ATask
from .base import AsyncBaseResource, BaseResource


class A2AResource(BaseResource):
    def get_agent_card(self, agent_id: str) -> A2AAgentCard:
        body = self._http.get(f"/a2a/agents/{agent_id}/agent-card.json")
        return A2AAgentCard.from_dict(body)

    def send_message(
        self,
        agent_id: str,
        message: str,
        *,
        blocking: bool = True,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None,
    ) -> A2ATask:
        params: Dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            },
        }
        if task_id:
            params["task_id"] = task_id
        if context_id:
            params["context_id"] = context_id
        if not blocking:
            params.setdefault("configuration", {})
            params["configuration"]["blocking"] = False

        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": params,
            "id": 1,
        }
        body = self._http.post(f"/a2a/agents/{agent_id}", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)

    def get_task(self, task_id: str) -> A2ATask:
        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"id": task_id},
            "id": 1,
        }
        # We need the agent_id for the URL but tasks/get only needs task_id in params.
        # The A2A endpoint expects POST to /a2a/agents/{agentId} but for task operations
        # we use a convenience wrapper that the server routes appropriately.
        body = self._http.post("/a2a/tasks/get", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)

    def list_tasks(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        context_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[A2ATask]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if context_id:
            params["context_id"] = context_id
        if status:
            params["status"] = status
        body = self._http.get("/api/v1/a2a/tasks", params=params)
        return PaginatedResponse.from_response(body, A2ATask.from_dict)

    def cancel_task(self, task_id: str) -> A2ATask:
        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tasks/cancel",
            "params": {"id": task_id},
            "id": 1,
        }
        body = self._http.post("/a2a/tasks/cancel", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)


class AsyncA2AResource(AsyncBaseResource):
    async def get_agent_card(self, agent_id: str) -> A2AAgentCard:
        body = await self._http.get(f"/a2a/agents/{agent_id}/agent-card.json")
        return A2AAgentCard.from_dict(body)

    async def send_message(
        self,
        agent_id: str,
        message: str,
        *,
        blocking: bool = True,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None,
    ) -> A2ATask:
        params: Dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            },
        }
        if task_id:
            params["task_id"] = task_id
        if context_id:
            params["context_id"] = context_id
        if not blocking:
            params.setdefault("configuration", {})
            params["configuration"]["blocking"] = False

        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": params,
            "id": 1,
        }
        body = await self._http.post(f"/a2a/agents/{agent_id}", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)

    async def get_task(self, task_id: str) -> A2ATask:
        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"id": task_id},
            "id": 1,
        }
        body = await self._http.post("/a2a/tasks/get", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)

    async def list_tasks(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        context_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[A2ATask]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if context_id:
            params["context_id"] = context_id
        if status:
            params["status"] = status
        body = await self._http.get("/api/v1/a2a/tasks", params=params)
        return PaginatedResponse.from_response(body, A2ATask.from_dict)

    async def cancel_task(self, task_id: str) -> A2ATask:
        rpc_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tasks/cancel",
            "params": {"id": task_id},
            "id": 1,
        }
        body = await self._http.post("/a2a/tasks/cancel", json=rpc_body)
        result = body.get("result", body)
        return A2ATask.from_dict(result)
