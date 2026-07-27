from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginationMeta:
    total: int
    page: int
    limit: int
    pages: int


@dataclass
class PaginatedResponse(Generic[T]):
    data: List[T]
    meta: PaginationMeta

    @classmethod
    def from_response(cls, body: Dict[str, Any], item_factory) -> "PaginatedResponse":
        raw_data = body.get("data", [])
        items = [item_factory(item) for item in raw_data]
        meta_raw = body.get("meta", {})
        meta = PaginationMeta(
            total=meta_raw.get("total", 0),
            page=meta_raw.get("page", 1),
            limit=meta_raw.get("limit", 20),
            # API v2 standardizes on ``pages``; older payloads used ``total_pages``.
            pages=meta_raw.get("pages", meta_raw.get("total_pages", 0)),
        )
        return cls(data=items, meta=meta)
