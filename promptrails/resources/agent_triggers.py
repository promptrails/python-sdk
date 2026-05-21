from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import AgentTrigger, AgentTriggerCreateResponse
from .base import AsyncBaseResource, BaseResource


class AgentTriggersResource(BaseResource):
    """Manage agent triggers: generic webhook, Slack, Telegram, Teams, WhatsApp, schedule."""

    def list(
        self, *, agent_id: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentTrigger]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        body = self._http.get("/api/v1/triggers", params=params)
        return PaginatedResponse.from_response(body, AgentTrigger.from_dict)

    def get(self, trigger_id: str) -> AgentTrigger:
        body = self._http.get(f"/api/v1/triggers/{trigger_id}")
        return AgentTrigger.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        agent_id: str,
        source: str = "generic",
        source_config: Optional[Dict[str, Any]] = None,
        reply_config: Optional[Dict[str, Any]] = None,
        generate_secret: bool = False,
    ) -> AgentTriggerCreateResponse:
        payload: Dict[str, Any] = {
            "name": name,
            "agent_id": agent_id,
            "source": source,
            "generate_secret": generate_secret,
        }
        if source_config is not None:
            payload["source_config"] = source_config
        if reply_config is not None:
            payload["reply_config"] = reply_config
        body = self._http.post("/api/v1/triggers", json=payload)
        return AgentTriggerCreateResponse.from_dict(self._unwrap(body))

    def update(self, trigger_id: str, **kwargs: Any) -> AgentTrigger:
        body = self._http.patch(f"/api/v1/triggers/{trigger_id}", json=kwargs)
        return AgentTrigger.from_dict(self._unwrap(body))

    def delete(self, trigger_id: str) -> None:
        self._http.delete(f"/api/v1/triggers/{trigger_id}")


class AsyncAgentTriggersResource(AsyncBaseResource):
    """Async variant of AgentTriggersResource."""

    async def list(
        self, *, agent_id: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[AgentTrigger]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        body = await self._http.get("/api/v1/triggers", params=params)
        return PaginatedResponse.from_response(body, AgentTrigger.from_dict)

    async def get(self, trigger_id: str) -> AgentTrigger:
        body = await self._http.get(f"/api/v1/triggers/{trigger_id}")
        return AgentTrigger.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        agent_id: str,
        source: str = "generic",
        source_config: Optional[Dict[str, Any]] = None,
        reply_config: Optional[Dict[str, Any]] = None,
        generate_secret: bool = False,
    ) -> AgentTriggerCreateResponse:
        payload: Dict[str, Any] = {
            "name": name,
            "agent_id": agent_id,
            "source": source,
            "generate_secret": generate_secret,
        }
        if source_config is not None:
            payload["source_config"] = source_config
        if reply_config is not None:
            payload["reply_config"] = reply_config
        body = await self._http.post("/api/v1/triggers", json=payload)
        return AgentTriggerCreateResponse.from_dict(self._unwrap(body))

    async def update(self, trigger_id: str, **kwargs: Any) -> AgentTrigger:
        body = await self._http.patch(f"/api/v1/triggers/{trigger_id}", json=kwargs)
        return AgentTrigger.from_dict(self._unwrap(body))

    async def delete(self, trigger_id: str) -> None:
        await self._http.delete(f"/api/v1/triggers/{trigger_id}")
