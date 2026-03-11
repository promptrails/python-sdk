from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import MediaModel
from .base import AsyncBaseResource, BaseResource


class MediaModelsResource(BaseResource):
    """Resource for listing available media models."""

    def list(
        self,
        *,
        provider: Optional[str] = None,
        media_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[MediaModel]:
        """List available media models.

        Args:
            provider: Filter by provider (e.g. ``fal``, ``elevenlabs``).
            media_type: Filter by media type (e.g. ``image``, ``speech``, ``video``).
            is_active: Filter by active status.

        Returns:
            List of media models.
        """
        params: Dict[str, Any] = {}
        if provider is not None:
            params["provider"] = provider
        if media_type is not None:
            params["media_type"] = media_type
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        body = self._http.get("/api/v1/media-models", params=params)
        data = self._unwrap(body)
        return [MediaModel.from_dict(m) for m in (data if isinstance(data, list) else [])]


class AsyncMediaModelsResource(AsyncBaseResource):
    """Async resource for listing available media models."""

    async def list(
        self,
        *,
        provider: Optional[str] = None,
        media_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[MediaModel]:
        """List available media models.

        Args:
            provider: Filter by provider (e.g. ``fal``, ``elevenlabs``).
            media_type: Filter by media type (e.g. ``image``, ``speech``, ``video``).
            is_active: Filter by active status.

        Returns:
            List of media models.
        """
        params: Dict[str, Any] = {}
        if provider is not None:
            params["provider"] = provider
        if media_type is not None:
            params["media_type"] = media_type
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        body = await self._http.get("/api/v1/media-models", params=params)
        data = self._unwrap(body)
        return [MediaModel.from_dict(m) for m in (data if isinstance(data, list) else [])]
