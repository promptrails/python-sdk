from __future__ import annotations

from ..types import AgentMemory
from .base import AsyncBaseResource, BaseResource


class MemoriesResource(BaseResource):
    def get(self, memory_id: str) -> AgentMemory:
        body = self._http.get(f"/api/v1/memories/{memory_id}")
        return AgentMemory.from_dict(self._unwrap(body))

    def delete(self, memory_id: str) -> None:
        self._http.delete(f"/api/v1/memories/{memory_id}")


class AsyncMemoriesResource(AsyncBaseResource):
    async def get(self, memory_id: str) -> AgentMemory:
        body = await self._http.get(f"/api/v1/memories/{memory_id}")
        return AgentMemory.from_dict(self._unwrap(body))

    async def delete(self, memory_id: str) -> None:
        await self._http.delete(f"/api/v1/memories/{memory_id}")
