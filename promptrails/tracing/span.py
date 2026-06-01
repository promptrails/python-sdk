"""Span — a single unit of work within a trace."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from ._ids import generate_span_id, generate_trace_id


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt is not None else None


class Span:
    """A single span. Build it up with the ``set_*`` helpers, then call
    :meth:`end` (or use the tracer's context manager, which ends it for you).

    Spans are cheap value objects; the heavy lifting (batching, HTTP) happens
    in the exporter once the span ends.
    """

    def __init__(
        self,
        name: str,
        *,
        kind: str = "chain",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        session_id: Optional[str] = None,
        on_end: Optional[Callable[["Span"], None]] = None,
    ) -> None:
        self.trace_id = trace_id or generate_trace_id()
        self.span_id = generate_span_id()
        self.parent_span_id = parent_span_id
        self.name = name
        self.kind = kind
        self.status = "ok"
        self.level = "default"
        self.session_id = session_id

        self.input: Optional[Any] = None
        self.output: Optional[Any] = None
        self.attributes: Dict[str, Any] = {}
        self.tags: List[str] = []
        self.model_name: Optional[str] = None
        self.prompt_tokens: Optional[int] = None
        self.completion_tokens: Optional[int] = None
        self.total_tokens: Optional[int] = None
        self.cost: Optional[float] = None
        self.error_message: Optional[str] = None
        self.error_type: Optional[str] = None

        self.started_at = _now()
        self.ended_at: Optional[datetime] = None

        self._on_end = on_end
        self._ended = False

    # -- builder helpers (all return self for chaining) -------------------

    def set_input(self, value: Any) -> "Span":
        self.input = value
        return self

    def set_output(self, value: Any) -> "Span":
        self.output = value
        return self

    def set_attributes(self, **attrs: Any) -> "Span":
        self.attributes.update(attrs)
        return self

    def set_tags(self, *tags: str) -> "Span":
        self.tags.extend(tags)
        return self

    def set_model(self, model_name: str) -> "Span":
        self.model_name = model_name
        return self

    def set_usage(
        self,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
    ) -> "Span":
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens
        self.total_tokens = total_tokens
        return self

    def set_cost(self, cost: float) -> "Span":
        self.cost = cost
        return self

    def set_session(self, session_id: str) -> "Span":
        self.session_id = session_id
        return self

    def set_error(self, error: BaseException) -> "Span":
        self.status = "error"
        self.level = "error"
        self.error_message = str(error)
        self.error_type = type(error).__name__
        return self

    # -- lifecycle --------------------------------------------------------

    def end(self) -> None:
        """Finalize the span and hand it to the exporter. Idempotent."""
        if self._ended:
            return
        self._ended = True
        self.ended_at = _now()
        if self._on_end is not None:
            self._on_end(self)

    def to_payload(self) -> Dict[str, Any]:
        """Serialize into the ingest API's span shape, dropping unset fields."""
        payload: Dict[str, Any] = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "level": self.level,
            "started_at": _iso(self.started_at),
        }
        if self.parent_span_id:
            payload["parent_span_id"] = self.parent_span_id
        if self.ended_at:
            payload["ended_at"] = _iso(self.ended_at)
        if self.input is not None:
            payload["input"] = self.input
        if self.output is not None:
            payload["output"] = self.output
        if self.attributes:
            payload["attributes"] = self.attributes
        if self.tags:
            payload["tags"] = self.tags
        if self.model_name:
            payload["model_name"] = self.model_name
        if self.prompt_tokens is not None:
            payload["prompt_tokens"] = self.prompt_tokens
        if self.completion_tokens is not None:
            payload["completion_tokens"] = self.completion_tokens
        if self.total_tokens is not None:
            payload["total_tokens"] = self.total_tokens
        if self.cost is not None:
            payload["cost"] = self.cost
        if self.session_id:
            payload["session_id"] = self.session_id
        if self.error_message:
            payload["error_message"] = self.error_message
        if self.error_type:
            payload["error_type"] = self.error_type
        return payload
