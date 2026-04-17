from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..agent_config import AgentConfig
from ..pagination import PaginatedResponse
from ..types import Agent, AgentMemory, AgentVersion, ExecutionResult, Guardrail
from .base import AsyncBaseResource, BaseResource


class AgentsResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        type: Optional[str] = None,
        name: Optional[str] = None,
    ) -> PaginatedResponse[Agent]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        body = self._http.get("/api/v1/agents", params=params)
        return PaginatedResponse.from_response(body, Agent.from_dict)

    def get(self, agent_id: str) -> Agent:
        body = self._http.get(f"/api/v1/agents/{agent_id}")
        return Agent.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        type: str,
        description: str = "",
        template_id: Optional[str] = None,
    ) -> Agent:
        payload: Dict[str, Any] = {"name": name, "type": type, "description": description}
        if template_id is not None:
            payload["template_id"] = template_id
        body = self._http.post("/api/v1/agents", json=payload)
        return Agent.from_dict(self._unwrap(body))

    def update(self, agent_id: str, **kwargs) -> Agent:
        body = self._http.patch(f"/api/v1/agents/{agent_id}", json=kwargs)
        return Agent.from_dict(self._unwrap(body))

    def delete(self, agent_id: str) -> None:
        self._http.delete(f"/api/v1/agents/{agent_id}")

    def execute(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        session_id: Optional[str] = None,
        version_id: Optional[str] = None,
        sync: Optional[bool] = None,
    ) -> ExecutionResult:
        payload: Dict[str, Any] = {"input": input}
        if session_id:
            payload["session_id"] = session_id
        if version_id is not None:
            payload["version_id"] = version_id
        if sync is not None:
            payload["sync"] = sync
        body = self._http.post(f"/api/v1/agents/{agent_id}/execute", json=payload)
        return ExecutionResult.from_dict(self._unwrap(body))

    def list_versions(self, agent_id: str) -> List[AgentVersion]:
        body = self._http.get(f"/api/v1/agents/{agent_id}/versions")
        data = self._unwrap(body)
        if isinstance(data, list):
            return [AgentVersion.from_dict(v) for v in data]
        return [AgentVersion.from_dict(v) for v in data] if data else []

    def create_version(
        self,
        agent_id: str,
        *,
        version: str,
        config: AgentConfig,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> AgentVersion:
        payload: Dict[str, Any] = {
            "version": version,
            "set_current": set_current,
            "config": config.to_dict(),
        }
        if input_schema is not None:
            payload["input_schema"] = input_schema
        if output_schema is not None:
            payload["output_schema"] = output_schema
        if message is not None:
            payload["message"] = message
        body = self._http.post(f"/api/v1/agents/{agent_id}/versions", json=payload)
        return AgentVersion.from_dict(self._unwrap(body))

    def promote_version(self, agent_id: str, version_id: str) -> Dict[str, Any]:
        body = self._http.put(f"/api/v1/agents/{agent_id}/versions/{version_id}/promote", json={})
        return self._unwrap(body)

    def preview(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = self._http.post(f"/api/v1/agents/{agent_id}/preview", json=payload)
        return self._unwrap(body)

    def list_guardrails(self, agent_id: str) -> List[Guardrail]:
        body = self._http.get(f"/api/v1/agents/{agent_id}/guardrails")
        data = self._unwrap(body)
        return [Guardrail.from_dict(g) for g in (data if isinstance(data, list) else [])]

    def create_guardrail(
        self,
        agent_id: str,
        *,
        type: str,
        scanner_type: str,
        action: str = "block",
        config: Optional[Dict[str, Any]] = None,
    ) -> Guardrail:
        payload: Dict[str, Any] = {"type": type, "scanner_type": scanner_type, "action": action}
        if config is not None:
            payload["config"] = config
        body = self._http.post(f"/api/v1/agents/{agent_id}/guardrails", json=payload)
        return Guardrail.from_dict(self._unwrap(body))

    def list_memories(
        self, agent_id: str, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentMemory]:
        body = self._http.get(
            f"/api/v1/agents/{agent_id}/memories", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, AgentMemory.from_dict)

    def create_memory(
        self,
        agent_id: str,
        *,
        content: str,
        memory_type: str,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chat_session_id: Optional[str] = None,
    ) -> AgentMemory:
        payload: Dict[str, Any] = {"content": content, "memory_type": memory_type}
        if importance is not None:
            payload["importance"] = importance
        if metadata is not None:
            payload["metadata"] = metadata
        if chat_session_id is not None:
            payload["chat_session_id"] = chat_session_id
        body = self._http.post(f"/api/v1/agents/{agent_id}/memories", json=payload)
        return AgentMemory.from_dict(self._unwrap(body))

    def search_memories(
        self,
        agent_id: str,
        *,
        query: str,
        threshold: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[AgentMemory]:
        payload: Dict[str, Any] = {"query": query}
        if threshold is not None:
            payload["threshold"] = threshold
        if limit is not None:
            payload["limit"] = limit
        body = self._http.post(f"/api/v1/agents/{agent_id}/memories/search", json=payload)
        data = self._unwrap(body)
        return [AgentMemory.from_dict(m) for m in (data if isinstance(data, list) else [])]

    def delete_all_memories(self, agent_id: str) -> None:
        self._http.delete(f"/api/v1/agents/{agent_id}/memories")


class AsyncAgentsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        type: Optional[str] = None,
        name: Optional[str] = None,
    ) -> PaginatedResponse[Agent]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        body = await self._http.get("/api/v1/agents", params=params)
        return PaginatedResponse.from_response(body, Agent.from_dict)

    async def get(self, agent_id: str) -> Agent:
        body = await self._http.get(f"/api/v1/agents/{agent_id}")
        return Agent.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        type: str,
        description: str = "",
        template_id: Optional[str] = None,
    ) -> Agent:
        payload: Dict[str, Any] = {"name": name, "type": type, "description": description}
        if template_id is not None:
            payload["template_id"] = template_id
        body = await self._http.post("/api/v1/agents", json=payload)
        return Agent.from_dict(self._unwrap(body))

    async def update(self, agent_id: str, **kwargs) -> Agent:
        body = await self._http.patch(f"/api/v1/agents/{agent_id}", json=kwargs)
        return Agent.from_dict(self._unwrap(body))

    async def delete(self, agent_id: str) -> None:
        await self._http.delete(f"/api/v1/agents/{agent_id}")

    async def execute(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        session_id: Optional[str] = None,
        version_id: Optional[str] = None,
        sync: Optional[bool] = None,
    ) -> ExecutionResult:
        payload: Dict[str, Any] = {"input": input}
        if session_id:
            payload["session_id"] = session_id
        if version_id is not None:
            payload["version_id"] = version_id
        if sync is not None:
            payload["sync"] = sync
        body = await self._http.post(f"/api/v1/agents/{agent_id}/execute", json=payload)
        return ExecutionResult.from_dict(self._unwrap(body))

    async def list_versions(self, agent_id: str) -> List[AgentVersion]:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/versions")
        data = self._unwrap(body)
        return [AgentVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    async def create_version(
        self,
        agent_id: str,
        *,
        version: str,
        config: AgentConfig,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> AgentVersion:
        payload: Dict[str, Any] = {
            "version": version,
            "set_current": set_current,
            "config": config.to_dict(),
        }
        if input_schema is not None:
            payload["input_schema"] = input_schema
        if output_schema is not None:
            payload["output_schema"] = output_schema
        if message is not None:
            payload["message"] = message
        body = await self._http.post(f"/api/v1/agents/{agent_id}/versions", json=payload)
        return AgentVersion.from_dict(self._unwrap(body))

    async def promote_version(self, agent_id: str, version_id: str) -> Dict[str, Any]:
        body = await self._http.put(
            f"/api/v1/agents/{agent_id}/versions/{version_id}/promote", json={}
        )
        return self._unwrap(body)

    async def preview(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = await self._http.post(f"/api/v1/agents/{agent_id}/preview", json=payload)
        return self._unwrap(body)

    async def list_guardrails(self, agent_id: str) -> List[Guardrail]:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/guardrails")
        data = self._unwrap(body)
        return [Guardrail.from_dict(g) for g in (data if isinstance(data, list) else [])]

    async def create_guardrail(
        self,
        agent_id: str,
        *,
        type: str,
        scanner_type: str,
        action: str = "block",
        config: Optional[Dict[str, Any]] = None,
    ) -> Guardrail:
        payload: Dict[str, Any] = {"type": type, "scanner_type": scanner_type, "action": action}
        if config is not None:
            payload["config"] = config
        body = await self._http.post(f"/api/v1/agents/{agent_id}/guardrails", json=payload)
        return Guardrail.from_dict(self._unwrap(body))

    async def list_memories(
        self, agent_id: str, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentMemory]:
        body = await self._http.get(
            f"/api/v1/agents/{agent_id}/memories", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, AgentMemory.from_dict)

    async def create_memory(
        self,
        agent_id: str,
        *,
        content: str,
        memory_type: str,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chat_session_id: Optional[str] = None,
    ) -> AgentMemory:
        payload: Dict[str, Any] = {"content": content, "memory_type": memory_type}
        if importance is not None:
            payload["importance"] = importance
        if metadata is not None:
            payload["metadata"] = metadata
        if chat_session_id is not None:
            payload["chat_session_id"] = chat_session_id
        body = await self._http.post(f"/api/v1/agents/{agent_id}/memories", json=payload)
        return AgentMemory.from_dict(self._unwrap(body))

    async def search_memories(
        self,
        agent_id: str,
        *,
        query: str,
        threshold: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[AgentMemory]:
        payload: Dict[str, Any] = {"query": query}
        if threshold is not None:
            payload["threshold"] = threshold
        if limit is not None:
            payload["limit"] = limit
        body = await self._http.post(f"/api/v1/agents/{agent_id}/memories/search", json=payload)
        data = self._unwrap(body)
        return [AgentMemory.from_dict(m) for m in (data if isinstance(data, list) else [])]

    async def delete_all_memories(self, agent_id: str) -> None:
        await self._http.delete(f"/api/v1/agents/{agent_id}/memories")
