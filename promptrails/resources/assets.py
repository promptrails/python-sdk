from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import Asset, AssetSignedURL
from .base import AsyncBaseResource, BaseResource


class AssetsResource(BaseResource):
    """Resource for managing media assets."""

    def list(
        self,
        *,
        type: Optional[str] = None,
        provider: Optional[str] = None,
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse[Asset]:
        """List assets.

        Args:
            type: Filter by asset type (e.g. ``image``, ``speech``, ``video``).
            provider: Filter by provider.
            execution_id: Filter by execution ID.
            agent_id: Filter by agent ID.
            page: Page number.
            limit: Items per page.

        Returns:
            Paginated list of assets.
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type is not None:
            params["type"] = type
        if provider is not None:
            params["provider"] = provider
        if execution_id is not None:
            params["execution_id"] = execution_id
        if agent_id is not None:
            params["agent_id"] = agent_id
        body = self._http.get("/api/v1/assets", params=params)
        return PaginatedResponse.from_response(body, Asset.from_dict)

    def get(self, asset_id: str) -> Asset:
        """Get a single asset by ID.

        Args:
            asset_id: The asset ID.

        Returns:
            The asset.
        """
        body = self._http.get(f"/api/v1/assets/{asset_id}")
        return Asset.from_dict(self._unwrap(body))

    def delete(self, asset_id: str) -> None:
        """Delete an asset.

        Args:
            asset_id: The asset ID.
        """
        self._http.delete(f"/api/v1/assets/{asset_id}")

    def get_signed_url(self, asset_id: str) -> AssetSignedURL:
        """Get a signed URL for an asset.

        Args:
            asset_id: The asset ID.

        Returns:
            Signed URL details.
        """
        body = self._http.get(f"/api/v1/assets/{asset_id}/signed-url")
        return AssetSignedURL.from_dict(self._unwrap(body))


class AsyncAssetsResource(AsyncBaseResource):
    """Async resource for managing media assets."""

    async def list(
        self,
        *,
        type: Optional[str] = None,
        provider: Optional[str] = None,
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse[Asset]:
        """List assets.

        Args:
            type: Filter by asset type (e.g. ``image``, ``speech``, ``video``).
            provider: Filter by provider.
            execution_id: Filter by execution ID.
            agent_id: Filter by agent ID.
            page: Page number.
            limit: Items per page.

        Returns:
            Paginated list of assets.
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type is not None:
            params["type"] = type
        if provider is not None:
            params["provider"] = provider
        if execution_id is not None:
            params["execution_id"] = execution_id
        if agent_id is not None:
            params["agent_id"] = agent_id
        body = await self._http.get("/api/v1/assets", params=params)
        return PaginatedResponse.from_response(body, Asset.from_dict)

    async def get(self, asset_id: str) -> Asset:
        """Get a single asset by ID.

        Args:
            asset_id: The asset ID.

        Returns:
            The asset.
        """
        body = await self._http.get(f"/api/v1/assets/{asset_id}")
        return Asset.from_dict(self._unwrap(body))

    async def delete(self, asset_id: str) -> None:
        """Delete an asset.

        Args:
            asset_id: The asset ID.
        """
        await self._http.delete(f"/api/v1/assets/{asset_id}")

    async def get_signed_url(self, asset_id: str) -> AssetSignedURL:
        """Get a signed URL for an asset.

        Args:
            asset_id: The asset ID.

        Returns:
            Signed URL details.
        """
        body = await self._http.get(f"/api/v1/assets/{asset_id}/signed-url")
        return AssetSignedURL.from_dict(self._unwrap(body))
