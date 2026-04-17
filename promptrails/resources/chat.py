from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Iterator, Optional

from .._sse import StreamEvent, aiter_sse, iter_sse
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

    def send_message_stream(self, session_id: str, *, content: str) -> Iterator[StreamEvent]:
        """Post a message and iterate the live SSE event stream.

        Yields typed events — start with :class:`ExecutionEvent`, end on
        :class:`DoneEvent` or :class:`ErrorEvent`. The HTTP body stays open
        until iteration completes, so run it inside a ``for event in ...``
        loop (don't materialise it to a list and drop the iterator).
        """
        with self._http.stream(
            "POST",
            f"/api/v1/chat/sessions/{session_id}/messages/stream",
            json={"content": content},
        ) as response:
            response.raise_for_status()
            yield from iter_sse(response)


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

    async def send_message_stream(
        self, session_id: str, *, content: str
    ) -> AsyncIterator[StreamEvent]:
        """Async variant of :meth:`ChatResource.send_message_stream`."""
        async with self._http.stream(
            "POST",
            f"/api/v1/chat/sessions/{session_id}/messages/stream",
            json={"content": content},
        ) as response:
            response.raise_for_status()
            async for event in aiter_sse(response):
                yield event
