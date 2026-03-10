from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import AvailableModelGroup, LLMModel
from .base import AsyncBaseResource, BaseResource


class LLMModelsResource(BaseResource):
    def list(
        self, *, page: int = 1, limit: int = 20, provider: Optional[str] = None
    ) -> PaginatedResponse[LLMModel]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if provider is not None:
            params["provider"] = provider
        body = self._http.get("/api/v1/llm-models", params=params)
        return PaginatedResponse.from_response(body, LLMModel.from_dict)

    def list_available(self) -> List[AvailableModelGroup]:
        body = self._http.get("/api/v1/llm-models/available")
        data = self._unwrap(body)
        return [AvailableModelGroup.from_dict(g) for g in (data if isinstance(data, list) else [])]


class AsyncLLMModelsResource(AsyncBaseResource):
    async def list(
        self, *, page: int = 1, limit: int = 20, provider: Optional[str] = None
    ) -> PaginatedResponse[LLMModel]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if provider is not None:
            params["provider"] = provider
        body = await self._http.get("/api/v1/llm-models", params=params)
        return PaginatedResponse.from_response(body, LLMModel.from_dict)

    async def list_available(self) -> List[AvailableModelGroup]:
        body = await self._http.get("/api/v1/llm-models/available")
        data = self._unwrap(body)
        return [AvailableModelGroup.from_dict(g) for g in (data if isinstance(data, list) else [])]
