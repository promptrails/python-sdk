from __future__ import annotations

from typing import Any, Dict

from ..pagination import PaginatedResponse
from ..types import Credential
from .base import AsyncBaseResource, BaseResource


class CredentialsResource(BaseResource):
    def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[Credential]:
        body = self._http.get("/api/v1/credentials", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, Credential.from_dict)

    def get(self, credential_id: str) -> Credential:
        body = self._http.get(f"/api/v1/credentials/{credential_id}")
        return Credential.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        type: str,
        category: str,
        value: str,
        description: str = "",
        is_default: bool = False,
        schema_type: str = "",
    ) -> Credential:
        payload = {
            "name": name,
            "type": type,
            "category": category,
            "value": value,
            "description": description,
            "is_default": is_default,
        }
        if schema_type:
            payload["schema_type"] = schema_type
        body = self._http.post("/api/v1/credentials", json=payload)
        return Credential.from_dict(self._unwrap(body))

    def update(self, credential_id: str, **kwargs) -> Credential:
        body = self._http.patch(f"/api/v1/credentials/{credential_id}", json=kwargs)
        return Credential.from_dict(self._unwrap(body))

    def delete(self, credential_id: str) -> None:
        self._http.delete(f"/api/v1/credentials/{credential_id}")

    def set_default(self, credential_id: str) -> Credential:
        body = self._http.post(f"/api/v1/credentials/{credential_id}/set-default")
        return Credential.from_dict(self._unwrap(body))

    def check_connection(self, credential_id: str) -> Dict[str, Any]:
        body = self._http.post(f"/api/v1/credentials/{credential_id}/check")
        return self._unwrap(body)


class AsyncCredentialsResource(AsyncBaseResource):
    async def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[Credential]:
        body = await self._http.get("/api/v1/credentials", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, Credential.from_dict)

    async def get(self, credential_id: str) -> Credential:
        body = await self._http.get(f"/api/v1/credentials/{credential_id}")
        return Credential.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        type: str,
        category: str,
        value: str,
        description: str = "",
        is_default: bool = False,
        schema_type: str = "",
    ) -> Credential:
        payload = {
            "name": name,
            "type": type,
            "category": category,
            "value": value,
            "description": description,
            "is_default": is_default,
        }
        if schema_type:
            payload["schema_type"] = schema_type
        body = await self._http.post("/api/v1/credentials", json=payload)
        return Credential.from_dict(self._unwrap(body))

    async def update(self, credential_id: str, **kwargs) -> Credential:
        body = await self._http.patch(f"/api/v1/credentials/{credential_id}", json=kwargs)
        return Credential.from_dict(self._unwrap(body))

    async def delete(self, credential_id: str) -> None:
        await self._http.delete(f"/api/v1/credentials/{credential_id}")

    async def set_default(self, credential_id: str) -> Credential:
        body = await self._http.post(f"/api/v1/credentials/{credential_id}/set-default")
        return Credential.from_dict(self._unwrap(body))

    async def check_connection(self, credential_id: str) -> Dict[str, Any]:
        body = await self._http.post(f"/api/v1/credentials/{credential_id}/check")
        return self._unwrap(body)
