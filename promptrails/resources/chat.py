from __future__ import annotations

from typing import Any, Dict, Optional

from ..pagination import PaginatedResponse
from ..types import ChatMessage, ChatSession
from .base import AsyncBaseResource, BaseResource


class ChatResource(BaseResource):
    def list_sessions(self, *, page: int = 1, limit: int = 20) -> PaginatedResponse[ChatSession]:
        body = self._http.get("/api/v1/chat/sessions", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, ChatSession.from_dict)

    def get_session(self, session_id: str) -> ChatSession:
        body = self._http.get(f"/api/v1/chat/sessions/{session_id}")
        return ChatSession.from_dict(self._unwrap(body))

    def create_session(
        self, *, agent_id: str, title: str = "", metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        payload: Dict[str, Any] = {"agent_id": agent_id}
        if title:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        body = self._http.post("/api/v1/chat/sessions", json=payload)
        return ChatSession.from_dict(self._unwrap(body))

    def delete_session(self, session_id: str) -> None:
        self._http.delete(f"/api/v1/chat/sessions/{session_id}")

    def list_messages(
        self, session_id: str, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[ChatMessage]:
        body = self._http.get(
            f"/api/v1/chat/sessions/{session_id}/messages", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, ChatMessage.from_dict)

    def send_message(self, session_id: str, *, content: str) -> ChatMessage:
        body = self._http.post(
            f"/api/v1/chat/sessions/{session_id}/messages", json={"content": content}
        )
        return ChatMessage.from_dict(self._unwrap(body))


class AsyncChatResource(AsyncBaseResource):
    async def list_sessions(
        self, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[ChatSession]:
        body = await self._http.get("/api/v1/chat/sessions", params={"page": page, "limit": limit})
        return PaginatedResponse.from_response(body, ChatSession.from_dict)

    async def get_session(self, session_id: str) -> ChatSession:
        body = await self._http.get(f"/api/v1/chat/sessions/{session_id}")
        return ChatSession.from_dict(self._unwrap(body))

    async def create_session(
        self, *, agent_id: str, title: str = "", metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        payload: Dict[str, Any] = {"agent_id": agent_id}
        if title:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        body = await self._http.post("/api/v1/chat/sessions", json=payload)
        return ChatSession.from_dict(self._unwrap(body))

    async def delete_session(self, session_id: str) -> None:
        await self._http.delete(f"/api/v1/chat/sessions/{session_id}")

    async def list_messages(
        self, session_id: str, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse[ChatMessage]:
        body = await self._http.get(
            f"/api/v1/chat/sessions/{session_id}/messages", params={"page": page, "limit": limit}
        )
        return PaginatedResponse.from_response(body, ChatMessage.from_dict)

    async def send_message(self, session_id: str, *, content: str) -> ChatMessage:
        body = await self._http.post(
            f"/api/v1/chat/sessions/{session_id}/messages", json={"content": content}
        )
        return ChatMessage.from_dict(self._unwrap(body))
