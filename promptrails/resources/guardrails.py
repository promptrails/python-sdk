from __future__ import annotations

from typing import List

from ..types import Guardrail, ScannerMeta
from .base import AsyncBaseResource, BaseResource


class GuardrailsResource(BaseResource):
    def list_scanners(self) -> List[ScannerMeta]:
        """List the guardrail scanners available in this workspace."""
        body = self._http.get("/api/v1/guardrails/scanners")
        data = self._unwrap(body)
        return [ScannerMeta.from_dict(s) for s in (data if isinstance(data, list) else [])]

    def update(self, guardrail_id: str, **kwargs) -> Guardrail:
        body = self._http.patch(f"/api/v1/guardrails/{guardrail_id}", json=kwargs)
        return Guardrail.from_dict(self._unwrap(body))

    def delete(self, guardrail_id: str) -> None:
        self._http.delete(f"/api/v1/guardrails/{guardrail_id}")


class AsyncGuardrailsResource(AsyncBaseResource):
    async def list_scanners(self) -> List[ScannerMeta]:
        """List the guardrail scanners available in this workspace."""
        body = await self._http.get("/api/v1/guardrails/scanners")
        data = self._unwrap(body)
        return [ScannerMeta.from_dict(s) for s in (data if isinstance(data, list) else [])]

    async def update(self, guardrail_id: str, **kwargs) -> Guardrail:
        body = await self._http.patch(f"/api/v1/guardrails/{guardrail_id}", json=kwargs)
        return Guardrail.from_dict(self._unwrap(body))

    async def delete(self, guardrail_id: str) -> None:
        await self._http.delete(f"/api/v1/guardrails/{guardrail_id}")
