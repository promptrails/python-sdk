from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pagination import PaginatedResponse
from ..types import Score, ScoreAggregate, ScoreConfig
from .base import AsyncBaseResource, BaseResource


class ScoresResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        trace_id: Optional[str] = None,
        name: Optional[str] = None,
        source: Optional[str] = None,
        data_type: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> PaginatedResponse[Score]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if trace_id:
            params["trace_id"] = trace_id
        if name:
            params["name"] = name
        if source:
            params["source"] = source
        if data_type:
            params["data_type"] = data_type
        if config_id:
            params["config_id"] = config_id
        body = self._http.get("/api/v1/scores", params=params)
        return PaginatedResponse.from_response(body, Score.from_dict)

    def get(self, score_id: str) -> Score:
        body = self._http.get(f"/api/v1/scores/{score_id}")
        return Score.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        trace_id: str,
        name: str,
        value: Optional[float] = None,
        string_value: Optional[str] = None,
        data_type: str = "numeric",
        source: str = "api",
        span_id: Optional[str] = None,
        config_id: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Score:
        payload: Dict[str, Any] = {
            "trace_id": trace_id,
            "name": name,
            "data_type": data_type,
            "source": source,
        }
        if value is not None:
            payload["value"] = value
        if string_value is not None:
            payload["string_value"] = string_value
        if span_id:
            payload["span_id"] = span_id
        if config_id:
            payload["config_id"] = config_id
        if comment:
            payload["comment"] = comment
        body = self._http.post("/api/v1/scores", json=payload)
        return Score.from_dict(self._unwrap(body))

    def update(self, score_id: str, **kwargs: Any) -> Score:
        body = self._http.patch(f"/api/v1/scores/{score_id}", json=kwargs)
        return Score.from_dict(self._unwrap(body))

    def delete(self, score_id: str) -> None:
        self._http.delete(f"/api/v1/scores/{score_id}")

    def get_aggregates(
        self,
        *,
        trace_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[ScoreAggregate]:
        params: Dict[str, Any] = {}
        if trace_id:
            params["trace_id"] = trace_id
        if name:
            params["name"] = name
        body = self._http.get("/api/v1/scores/aggregates", params=params)
        data = self._unwrap(body)
        return [ScoreAggregate.from_dict(d) for d in (data if isinstance(data, list) else [])]

    # Score Configs
    def list_configs(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[ScoreConfig]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        body = self._http.get("/api/v1/score-configs", params=params)
        return PaginatedResponse.from_response(body, ScoreConfig.from_dict)

    def get_config(self, config_id: str) -> ScoreConfig:
        body = self._http.get(f"/api/v1/score-configs/{config_id}")
        return ScoreConfig.from_dict(self._unwrap(body))

    def create_config(
        self,
        *,
        name: str,
        data_type: str = "numeric",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        categories: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
    ) -> ScoreConfig:
        payload: Dict[str, Any] = {"name": name, "data_type": data_type}
        if min_value is not None:
            payload["min_value"] = min_value
        if max_value is not None:
            payload["max_value"] = max_value
        if categories:
            payload["categories"] = categories
        if description:
            payload["description"] = description
        body = self._http.post("/api/v1/score-configs", json=payload)
        return ScoreConfig.from_dict(self._unwrap(body))

    def update_config(self, config_id: str, **kwargs: Any) -> ScoreConfig:
        body = self._http.patch(f"/api/v1/score-configs/{config_id}", json=kwargs)
        return ScoreConfig.from_dict(self._unwrap(body))

    def delete_config(self, config_id: str) -> None:
        self._http.delete(f"/api/v1/score-configs/{config_id}")


class AsyncScoresResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        trace_id: Optional[str] = None,
        name: Optional[str] = None,
        source: Optional[str] = None,
        data_type: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> PaginatedResponse[Score]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if trace_id:
            params["trace_id"] = trace_id
        if name:
            params["name"] = name
        if source:
            params["source"] = source
        if data_type:
            params["data_type"] = data_type
        if config_id:
            params["config_id"] = config_id
        body = await self._http.get("/api/v1/scores", params=params)
        return PaginatedResponse.from_response(body, Score.from_dict)

    async def get(self, score_id: str) -> Score:
        body = await self._http.get(f"/api/v1/scores/{score_id}")
        return Score.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        trace_id: str,
        name: str,
        value: Optional[float] = None,
        string_value: Optional[str] = None,
        data_type: str = "numeric",
        source: str = "api",
        span_id: Optional[str] = None,
        config_id: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Score:
        payload: Dict[str, Any] = {
            "trace_id": trace_id,
            "name": name,
            "data_type": data_type,
            "source": source,
        }
        if value is not None:
            payload["value"] = value
        if string_value is not None:
            payload["string_value"] = string_value
        if span_id:
            payload["span_id"] = span_id
        if config_id:
            payload["config_id"] = config_id
        if comment:
            payload["comment"] = comment
        body = await self._http.post("/api/v1/scores", json=payload)
        return Score.from_dict(self._unwrap(body))

    async def update(self, score_id: str, **kwargs: Any) -> Score:
        body = await self._http.patch(f"/api/v1/scores/{score_id}", json=kwargs)
        return Score.from_dict(self._unwrap(body))

    async def delete(self, score_id: str) -> None:
        await self._http.delete(f"/api/v1/scores/{score_id}")

    async def get_aggregates(
        self,
        *,
        trace_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[ScoreAggregate]:
        params: Dict[str, Any] = {}
        if trace_id:
            params["trace_id"] = trace_id
        if name:
            params["name"] = name
        body = await self._http.get("/api/v1/scores/aggregates", params=params)
        data = self._unwrap(body)
        return [ScoreAggregate.from_dict(d) for d in (data if isinstance(data, list) else [])]

    async def list_configs(
        self, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[ScoreConfig]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        body = await self._http.get("/api/v1/score-configs", params=params)
        return PaginatedResponse.from_response(body, ScoreConfig.from_dict)

    async def get_config(self, config_id: str) -> ScoreConfig:
        body = await self._http.get(f"/api/v1/score-configs/{config_id}")
        return ScoreConfig.from_dict(self._unwrap(body))

    async def create_config(
        self,
        *,
        name: str,
        data_type: str = "numeric",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        categories: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
    ) -> ScoreConfig:
        payload: Dict[str, Any] = {"name": name, "data_type": data_type}
        if min_value is not None:
            payload["min_value"] = min_value
        if max_value is not None:
            payload["max_value"] = max_value
        if categories:
            payload["categories"] = categories
        if description:
            payload["description"] = description
        body = await self._http.post("/api/v1/score-configs", json=payload)
        return ScoreConfig.from_dict(self._unwrap(body))

    async def update_config(self, config_id: str, **kwargs: Any) -> ScoreConfig:
        body = await self._http.patch(f"/api/v1/score-configs/{config_id}", json=kwargs)
        return ScoreConfig.from_dict(self._unwrap(body))

    async def delete_config(self, config_id: str) -> None:
        await self._http.delete(f"/api/v1/score-configs/{config_id}")
