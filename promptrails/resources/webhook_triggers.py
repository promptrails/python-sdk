from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import WebhookTrigger, WebhookTriggerCreateResponse
from .base import AsyncBaseResource, BaseResource


class WebhookTriggersResource(BaseResource):
    def list(
        self, *, agent_id: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[WebhookTrigger]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        body = self._http.get("/api/v1/webhook-triggers", params=params)
        return PaginatedResponse.from_response(body, WebhookTrigger.from_dict)

    def get(self, trigger_id: str) -> WebhookTrigger:
        body = self._http.get(f"/api/v1/webhook-triggers/{trigger_id}")
        return WebhookTrigger.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        agent_id: str,
        generate_secret: bool = False,
    ) -> WebhookTriggerCreateResponse:
        payload: Dict[str, Any] = {
            "name": name,
            "agent_id": agent_id,
            "generate_secret": generate_secret,
        }
        body = self._http.post("/api/v1/webhook-triggers", json=payload)
        return WebhookTriggerCreateResponse.from_dict(self._unwrap(body))

    def update(self, trigger_id: str, **kwargs: Any) -> WebhookTrigger:
        body = self._http.patch(f"/api/v1/webhook-triggers/{trigger_id}", json=kwargs)
        return WebhookTrigger.from_dict(self._unwrap(body))

    def delete(self, trigger_id: str) -> None:
        self._http.delete(f"/api/v1/webhook-triggers/{trigger_id}")


class AsyncWebhookTriggersResource(AsyncBaseResource):
    async def list(
        self, *, agent_id: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[WebhookTrigger]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        body = await self._http.get("/api/v1/webhook-triggers", params=params)
        return PaginatedResponse.from_response(body, WebhookTrigger.from_dict)

    async def get(self, trigger_id: str) -> WebhookTrigger:
        body = await self._http.get(f"/api/v1/webhook-triggers/{trigger_id}")
        return WebhookTrigger.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        agent_id: str,
        generate_secret: bool = False,
    ) -> WebhookTriggerCreateResponse:
        payload: Dict[str, Any] = {
            "name": name,
            "agent_id": agent_id,
            "generate_secret": generate_secret,
        }
        body = await self._http.post("/api/v1/webhook-triggers", json=payload)
        return WebhookTriggerCreateResponse.from_dict(self._unwrap(body))

    async def update(self, trigger_id: str, **kwargs: Any) -> WebhookTrigger:
        body = await self._http.patch(f"/api/v1/webhook-triggers/{trigger_id}", json=kwargs)
        return WebhookTrigger.from_dict(self._unwrap(body))

    async def delete(self, trigger_id: str) -> None:
        await self._http.delete(f"/api/v1/webhook-triggers/{trigger_id}")
