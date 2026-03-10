from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import DataSource, DataSourceVersion
from .base import AsyncBaseResource, BaseResource


class DataSourcesResource(BaseResource):
    def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[DataSource]:
        body = self._http.get("/api/v1/data-sources", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, DataSource.from_dict)

    def get(self, data_source_id: str) -> DataSource:
        body = self._http.get(f"/api/v1/data-sources/{data_source_id}")
        return DataSource.from_dict(self._unwrap(body))

    def create(self, *, name: str, type: str) -> DataSource:
        body = self._http.post("/api/v1/data-sources", json={"name": name, "type": type})
        return DataSource.from_dict(self._unwrap(body))

    def update(self, data_source_id: str, **kwargs) -> DataSource:
        body = self._http.patch(f"/api/v1/data-sources/{data_source_id}", json=kwargs)
        return DataSource.from_dict(self._unwrap(body))

    def delete(self, data_source_id: str) -> None:
        self._http.delete(f"/api/v1/data-sources/{data_source_id}")

    def list_versions(self, data_source_id: str) -> List[DataSourceVersion]:
        body = self._http.get(f"/api/v1/data-sources/{data_source_id}/versions")
        data = self._unwrap(body)
        return [DataSourceVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    def create_version(
        self,
        data_source_id: str,
        *,
        version: str,
        query_template: str = "",
        credential_id: Optional[str] = None,
        connection_config: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> DataSourceVersion:
        payload: Dict[str, Any] = {
            "version": version,
            "query_template": query_template,
            "set_current": set_current,
        }
        if credential_id is not None:
            payload["credential_id"] = credential_id
        if connection_config is not None:
            payload["connection_config"] = connection_config
        if parameters is not None:
            payload["parameters"] = parameters
        if message is not None:
            payload["message"] = message
        body = self._http.post(f"/api/v1/data-sources/{data_source_id}/versions", json=payload)
        return DataSourceVersion.from_dict(self._unwrap(body))

    def promote_version(self, data_source_id: str, version_id: str) -> Dict[str, Any]:
        body = self._http.put(
            f"/api/v1/data-sources/{data_source_id}/versions/{version_id}/promote", json={}
        )
        return self._unwrap(body)

    def preview_query(
        self,
        data_source_id: str,
        *,
        query_template: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"query_template": query_template}
        if parameters is not None:
            payload["parameters"] = parameters
        body = self._http.post(f"/api/v1/data-sources/{data_source_id}/preview-query", json=payload)
        return self._unwrap(body)

    def test_connection(self, data_source_id: str) -> Dict[str, Any]:
        body = self._http.post(f"/api/v1/data-sources/{data_source_id}/test-connection")
        return self._unwrap(body)

    def query(
        self, data_source_id: str, *, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if parameters is not None:
            payload["parameters"] = parameters
        body = self._http.post(f"/api/v1/data-sources/{data_source_id}/query", json=payload)
        return self._unwrap(body)


class AsyncDataSourcesResource(AsyncBaseResource):
    async def list(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[DataSource]:
        body = await self._http.get("/api/v1/data-sources", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, DataSource.from_dict)

    async def get(self, data_source_id: str) -> DataSource:
        body = await self._http.get(f"/api/v1/data-sources/{data_source_id}")
        return DataSource.from_dict(self._unwrap(body))

    async def create(self, *, name: str, type: str) -> DataSource:
        body = await self._http.post("/api/v1/data-sources", json={"name": name, "type": type})
        return DataSource.from_dict(self._unwrap(body))

    async def update(self, data_source_id: str, **kwargs) -> DataSource:
        body = await self._http.patch(f"/api/v1/data-sources/{data_source_id}", json=kwargs)
        return DataSource.from_dict(self._unwrap(body))

    async def delete(self, data_source_id: str) -> None:
        await self._http.delete(f"/api/v1/data-sources/{data_source_id}")

    async def list_versions(self, data_source_id: str) -> List[DataSourceVersion]:
        body = await self._http.get(f"/api/v1/data-sources/{data_source_id}/versions")
        data = self._unwrap(body)
        return [DataSourceVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    async def create_version(
        self,
        data_source_id: str,
        *,
        version: str,
        query_template: str = "",
        credential_id: Optional[str] = None,
        connection_config: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
    ) -> DataSourceVersion:
        payload: Dict[str, Any] = {
            "version": version,
            "query_template": query_template,
            "set_current": set_current,
        }
        if credential_id is not None:
            payload["credential_id"] = credential_id
        if connection_config is not None:
            payload["connection_config"] = connection_config
        if parameters is not None:
            payload["parameters"] = parameters
        if message is not None:
            payload["message"] = message
        body = await self._http.post(
            f"/api/v1/data-sources/{data_source_id}/versions", json=payload
        )
        return DataSourceVersion.from_dict(self._unwrap(body))

    async def promote_version(self, data_source_id: str, version_id: str) -> Dict[str, Any]:
        body = await self._http.put(
            f"/api/v1/data-sources/{data_source_id}/versions/{version_id}/promote", json={}
        )
        return self._unwrap(body)

    async def preview_query(
        self,
        data_source_id: str,
        *,
        query_template: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"query_template": query_template}
        if parameters is not None:
            payload["parameters"] = parameters
        body = await self._http.post(
            f"/api/v1/data-sources/{data_source_id}/preview-query", json=payload
        )
        return self._unwrap(body)

    async def test_connection(self, data_source_id: str) -> Dict[str, Any]:
        body = await self._http.post(f"/api/v1/data-sources/{data_source_id}/test-connection")
        return self._unwrap(body)

    async def query(
        self, data_source_id: str, *, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if parameters is not None:
            payload["parameters"] = parameters
        body = await self._http.post(f"/api/v1/data-sources/{data_source_id}/query", json=payload)
        return self._unwrap(body)
