"""Server-Sent Events parser + typed stream events.

Frames follow the backend's wire format — ``event: <name>\\ndata: <json>\\n\\n``.
Unknown event names are skipped silently so a future server can add new
event types without breaking older clients.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

import httpx

# === Typed stream events ===


@dataclass
class ExecutionEvent:
    """Emitted first on a chat stream — carries the execution identifier."""

    execution_id: str
    user_message_id: Optional[str] = None
    type: str = "execution"


@dataclass
class ThinkingEvent:
    """Intermediate reasoning text between tool rounds."""

    content: str
    type: str = "thinking"


@dataclass
class ToolStartEvent:
    """A tool is about to execute."""

    id: str
    name: str
    type: str = "tool_start"


@dataclass
class ToolEndEvent:
    """A tool finished. ``summary`` is a short display string."""

    id: str
    name: str
    summary: Optional[str] = None
    type: str = "tool_end"


@dataclass
class ContentEvent:
    """Delta of the final assistant response."""

    content: str
    type: str = "content"


@dataclass
class TokenUsage:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@dataclass
class DoneEvent:
    """Terminal event. ``output`` carries the full response when the backend
    did not emit progressive content deltas (e.g. non-tool agents)."""

    output: Optional[Dict[str, Any]] = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    type: str = "done"


@dataclass
class ErrorEvent:
    """Terminal error from the server."""

    message: str
    type: str = "error"


StreamEvent = Union[
    ExecutionEvent,
    ThinkingEvent,
    ToolStartEvent,
    ToolEndEvent,
    ContentEvent,
    DoneEvent,
    ErrorEvent,
]


def _parse_frame(event_name: str, data: str) -> Optional[StreamEvent]:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    def s(k: str) -> str:
        v = parsed.get(k)
        return v if isinstance(v, str) else ""

    if event_name == "execution":
        if not parsed.get("execution_id"):
            return None
        return ExecutionEvent(
            execution_id=s("execution_id"),
            user_message_id=parsed.get("user_message_id") or None,
        )
    if event_name == "thinking":
        return ThinkingEvent(content=s("content"))
    if event_name == "tool_start":
        if not parsed.get("id"):
            return None
        return ToolStartEvent(id=s("id"), name=s("name"))
    if event_name == "tool_end":
        if not parsed.get("id"):
            return None
        return ToolEndEvent(
            id=s("id"),
            name=s("name"),
            summary=parsed.get("summary") or None,
        )
    if event_name == "content":
        return ContentEvent(content=s("content"))
    if event_name == "done":
        usage = parsed.get("token_usage") or {}
        return DoneEvent(
            output=parsed.get("output") if isinstance(parsed.get("output"), dict) else None,
            token_usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
            ),
        )
    if event_name == "error":
        msg = s("message") or s("error") or "stream error"
        return ErrorEvent(message=msg)
    return None


def _iter_sse_frames(text_iter: Iterator[str]) -> Iterator[StreamEvent]:
    buffer = ""
    current_event = ""
    current_data = ""
    for chunk in text_iter:
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                current_data = line[5:].strip()
            elif line == "":
                if current_data:
                    evt = _parse_frame(current_event, current_data)
                    if evt is not None:
                        yield evt
                current_event = ""
                current_data = ""


def iter_sse(response: httpx.Response) -> Iterator[StreamEvent]:
    """Yield typed events from a synchronous httpx streaming response.

    The caller is expected to have opened the response with ``stream=True``
    (or the client's ``stream(...)`` context manager) and owns closing it.
    """
    yield from _iter_sse_frames(response.iter_text())


async def aiter_sse(response: httpx.Response) -> AsyncIterator[StreamEvent]:
    """Async variant of ``iter_sse``."""
    buffer = ""
    current_event = ""
    current_data = ""
    async for chunk in response.aiter_text():
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                current_data = line[5:].strip()
            elif line == "":
                if current_data:
                    evt = _parse_frame(current_event, current_data)
                    if evt is not None:
                        yield evt
                current_event = ""
                current_data = ""
