from __future__ import annotations

from ..types import Guardrail
from .base import AsyncBaseResource, BaseResource


class GuardrailsResource(BaseResource):
    def update(self, guardrail_id: str, **kwargs) -> Guardrail:
        body = self._http.patch(f"/api/v1/guardrails/{guardrail_id}", json=kwargs)
        return Guardrail.from_dict(self._unwrap(body))

    def delete(self, guardrail_id: str) -> None:
        self._http.delete(f"/api/v1/guardrails/{guardrail_id}")


class AsyncGuardrailsResource(AsyncBaseResource):
    async def update(self, guardrail_id: str, **kwargs) -> Guardrail:
        body = await self._http.patch(f"/api/v1/guardrails/{guardrail_id}", json=kwargs)
        return Guardrail.from_dict(self._unwrap(body))

    async def delete(self, guardrail_id: str) -> None:
        await self._http.delete(f"/api/v1/guardrails/{guardrail_id}")
