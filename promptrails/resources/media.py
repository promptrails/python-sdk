from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import MediaGenerateResult
from .base import AsyncBaseResource, BaseResource


class MediaResource(BaseResource):
    """Resource for media generation (Media Studio)."""

    def generate(
        self,
        *,
        provider: str,
        media_type: str,
        model: str,
        prompt: Optional[str] = None,
        input_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        guardrails: Optional[List[Dict[str, Any]]] = None,
    ) -> MediaGenerateResult:
        """Generate media content.

        Args:
            provider: Media provider (e.g. ``fal``, ``elevenlabs``, ``stability``).
            media_type: Type of media to generate (``image``, ``speech``, ``video``).
            model: Model identifier to use.
            prompt: Text prompt for generation.
            input_url: Input URL for transformations (e.g. image-to-video).
            config: Provider-specific configuration options.
            guardrails: Optional guardrail configurations.

        Returns:
            Media generation result.
        """
        payload: Dict[str, Any] = {
            "provider": provider,
            "media_type": media_type,
            "model": model,
        }
        if prompt is not None:
            payload["prompt"] = prompt
        if input_url is not None:
            payload["input_url"] = input_url
        if config is not None:
            payload["config"] = config
        if guardrails is not None:
            payload["guardrails"] = guardrails
        body = self._http.post("/api/v1/media/generate", json=payload)
        return MediaGenerateResult.from_dict(self._unwrap(body))


class AsyncMediaResource(AsyncBaseResource):
    """Async resource for media generation (Media Studio)."""

    async def generate(
        self,
        *,
        provider: str,
        media_type: str,
        model: str,
        prompt: Optional[str] = None,
        input_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        guardrails: Optional[List[Dict[str, Any]]] = None,
    ) -> MediaGenerateResult:
        """Generate media content.

        Args:
            provider: Media provider (e.g. ``fal``, ``elevenlabs``, ``stability``).
            media_type: Type of media to generate (``image``, ``speech``, ``video``).
            model: Model identifier to use.
            prompt: Text prompt for generation.
            input_url: Input URL for transformations (e.g. image-to-video).
            config: Provider-specific configuration options.
            guardrails: Optional guardrail configurations.

        Returns:
            Media generation result.
        """
        payload: Dict[str, Any] = {
            "provider": provider,
            "media_type": media_type,
            "model": model,
        }
        if prompt is not None:
            payload["prompt"] = prompt
        if input_url is not None:
            payload["input_url"] = input_url
        if config is not None:
            payload["config"] = config
        if guardrails is not None:
            payload["guardrails"] = guardrails
        body = await self._http.post("/api/v1/media/generate", json=payload)
        return MediaGenerateResult.from_dict(self._unwrap(body))
