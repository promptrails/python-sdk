from __future__ import annotations

from typing import Literal, Optional

from ..pagination import PaginatedResponse
from ..types import ApprovalRequest
from .base import AsyncBaseResource, BaseResource


class ApprovalsResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> PaginatedResponse[ApprovalRequest]:
        params: dict = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        body = self._http.get("/api/v1/approvals", params=params)
        return PaginatedResponse.from_response(body, ApprovalRequest.from_dict)

    def get(self, approval_id: str) -> ApprovalRequest:
        body = self._http.get(f"/api/v1/approvals/{approval_id}")
        return ApprovalRequest.from_dict(self._unwrap(body))

    def decide(
        self,
        approval_id: str,
        *,
        decision: Literal["approved", "rejected"],
        reason: Optional[str] = None,
    ) -> ApprovalRequest:
        payload: dict = {"decision": decision}
        if reason is not None:
            payload["reason"] = reason
        body = self._http.post(f"/api/v1/approvals/{approval_id}/decide", json=payload)
        return ApprovalRequest.from_dict(self._unwrap(body))


class AsyncApprovalsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> PaginatedResponse[ApprovalRequest]:
        params: dict = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        body = await self._http.get("/api/v1/approvals", params=params)
        return PaginatedResponse.from_response(body, ApprovalRequest.from_dict)

    async def get(self, approval_id: str) -> ApprovalRequest:
        body = await self._http.get(f"/api/v1/approvals/{approval_id}")
        return ApprovalRequest.from_dict(self._unwrap(body))

    async def decide(
        self,
        approval_id: str,
        *,
        decision: Literal["approved", "rejected"],
        reason: Optional[str] = None,
    ) -> ApprovalRequest:
        payload: dict = {"decision": decision}
        if reason is not None:
            payload["reason"] = reason
        body = await self._http.post(f"/api/v1/approvals/{approval_id}/decide", json=payload)
        return ApprovalRequest.from_dict(self._unwrap(body))
