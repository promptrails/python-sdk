from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import Prompt, PromptVersion
from .base import AsyncBaseResource, BaseResource


class PromptsResource(BaseResource):
    def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[Prompt]:
        body = self._http.get("/api/v1/prompts", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, Prompt.from_dict)

    def get(self, prompt_id: str) -> Prompt:
        body = self._http.get(f"/api/v1/prompts/{prompt_id}")
        return Prompt.from_dict(self._unwrap(body))

    def create(self, *, name: str, description: str = "") -> Prompt:
        body = self._http.post("/api/v1/prompts", json={"name": name, "description": description})
        return Prompt.from_dict(self._unwrap(body))

    def update(self, prompt_id: str, **kwargs) -> Prompt:
        body = self._http.patch(f"/api/v1/prompts/{prompt_id}", json=kwargs)
        return Prompt.from_dict(self._unwrap(body))

    def delete(self, prompt_id: str) -> None:
        self._http.delete(f"/api/v1/prompts/{prompt_id}")

    def list_versions(self, prompt_id: str) -> List[PromptVersion]:
        body = self._http.get(f"/api/v1/prompts/{prompt_id}/versions")
        data = self._unwrap(body)
        return [PromptVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    def create_version(
        self,
        prompt_id: str,
        *,
        version: str,
        user_prompt: str,
        system_prompt: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> PromptVersion:
        """Create a content-only prompt version.

        Model, sampling, tools, output schema and cache TTL live on the agent
        version (see :meth:`AgentsResource.create_version`), not on the prompt.
        """
        payload: Dict[str, Any] = {
            "version": version,
            "user_prompt": user_prompt,
            "system_prompt": system_prompt,
            "set_current": set_current,
        }
        if input_schema is not None:
            payload["input_schema"] = input_schema
        if config is not None:
            payload["config"] = config
        if message is not None:
            payload["message"] = message
        body = self._http.post(f"/api/v1/prompts/{prompt_id}/versions", json=payload)
        return PromptVersion.from_dict(self._unwrap(body))

    def promote_version(self, prompt_id: str, version_id: str) -> Dict[str, Any]:
        body = self._http.put(f"/api/v1/prompts/{prompt_id}/versions/{version_id}/promote", json={})
        return self._unwrap(body)

    def preview(
        self,
        prompt_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = self._http.post(f"/api/v1/prompts/{prompt_id}/preview", json=payload)
        return self._unwrap(body)


class AsyncPromptsResource(AsyncBaseResource):
    async def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[Prompt]:
        body = await self._http.get("/api/v1/prompts", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, Prompt.from_dict)

    async def get(self, prompt_id: str) -> Prompt:
        body = await self._http.get(f"/api/v1/prompts/{prompt_id}")
        return Prompt.from_dict(self._unwrap(body))

    async def create(self, *, name: str, description: str = "") -> Prompt:
        body = await self._http.post(
            "/api/v1/prompts", json={"name": name, "description": description}
        )
        return Prompt.from_dict(self._unwrap(body))

    async def update(self, prompt_id: str, **kwargs) -> Prompt:
        body = await self._http.patch(f"/api/v1/prompts/{prompt_id}", json=kwargs)
        return Prompt.from_dict(self._unwrap(body))

    async def delete(self, prompt_id: str) -> None:
        await self._http.delete(f"/api/v1/prompts/{prompt_id}")

    async def list_versions(self, prompt_id: str) -> List[PromptVersion]:
        body = await self._http.get(f"/api/v1/prompts/{prompt_id}/versions")
        data = self._unwrap(body)
        return [PromptVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    async def create_version(
        self,
        prompt_id: str,
        *,
        version: str,
        user_prompt: str,
        system_prompt: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> PromptVersion:
        """Async variant of :meth:`PromptsResource.create_version`."""
        payload: Dict[str, Any] = {
            "version": version,
            "user_prompt": user_prompt,
            "system_prompt": system_prompt,
            "set_current": set_current,
        }
        if input_schema is not None:
            payload["input_schema"] = input_schema
        if config is not None:
            payload["config"] = config
        if message is not None:
            payload["message"] = message
        body = await self._http.post(f"/api/v1/prompts/{prompt_id}/versions", json=payload)
        return PromptVersion.from_dict(self._unwrap(body))

    async def promote_version(self, prompt_id: str, version_id: str) -> Dict[str, Any]:
        body = await self._http.put(
            f"/api/v1/prompts/{prompt_id}/versions/{version_id}/promote", json={}
        )
        return self._unwrap(body)

    async def preview(
        self,
        prompt_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = await self._http.post(f"/api/v1/prompts/{prompt_id}/preview", json=payload)
        return self._unwrap(body)
