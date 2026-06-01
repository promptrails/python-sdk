"""OpenTelemetry bridge — export OTel spans to PromptRails.

Teams that already instrument with OpenTelemetry can forward spans to PromptRails
by registering this exporter; GenAI semantic-convention attributes (``gen_ai.*``)
are mapped onto the PromptRails span model.

Usage::

    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from promptrails.tracing.integrations.otel import PromptRailsSpanExporter

    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(PromptRailsSpanExporter(api_key="pr_..."))
    )
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from ..._http import HTTPClient
from ...config import Config
from ..exporter import INGEST_PATH

try:  # OpenTelemetry SDK is an optional dependency.
    from opentelemetry.sdk.trace.export import SpanExporter as _Base
    from opentelemetry.sdk.trace.export import SpanExportResult as _Result
except Exception:  # pragma: no cover - exercised only without the otel sdk
    _Base = object
    _Result = None

_GENAI_OP = "gen_ai.operation.name"
_GENAI_REQ_MODEL = "gen_ai.request.model"
_GENAI_RESP_MODEL = "gen_ai.response.model"
_GENAI_IN_TOKENS = "gen_ai.usage.input_tokens"
_GENAI_OUT_TOKENS = "gen_ai.usage.output_tokens"


class PromptRailsSpanExporter(_Base):
    """An OpenTelemetry ``SpanExporter`` that ships spans to the PromptRails
    ingest API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://api.promptrails.ai",
        http: Optional[HTTPClient] = None,
    ) -> None:
        if _Base is object:
            raise ImportError(
                "OpenTelemetry SDK is required for PromptRailsSpanExporter. "
                "Install it with `pip install opentelemetry-sdk`."
            )
        if http is None:
            if not api_key:
                raise ValueError("PromptRailsSpanExporter requires an api_key (or http)")
            http = HTTPClient(Config(api_key=api_key, base_url=base_url))
        self._http = http

    def export(self, spans: Sequence[Any]):  # -> SpanExportResult
        payloads = [otel_span_to_payload(s) for s in spans]
        try:
            self._http.post(INGEST_PATH, json={"spans": payloads})
            return _Result.SUCCESS
        except Exception:
            return _Result.FAILURE

    def shutdown(self) -> None:
        self._http.close()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


def otel_span_to_payload(span: Any) -> Dict[str, Any]:
    """Map an OpenTelemetry ReadableSpan onto the PromptRails ingest shape."""
    ctx = span.get_span_context() if hasattr(span, "get_span_context") else span.context
    attrs: Dict[str, Any] = dict(span.attributes or {})

    payload: Dict[str, Any] = {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
        "name": span.name,
        "kind": _kind(attrs),
        "status": _status(span),
        "started_at": _iso(span.start_time),
        "attributes": attrs,
    }
    parent = getattr(span, "parent", None)
    if parent is not None:
        payload["parent_span_id"] = format(parent.span_id, "016x")
    if span.end_time:
        payload["ended_at"] = _iso(span.end_time)

    model = attrs.get(_GENAI_RESP_MODEL) or attrs.get(_GENAI_REQ_MODEL)
    if model:
        payload["model_name"] = model
    prompt = attrs.get(_GENAI_IN_TOKENS)
    completion = attrs.get(_GENAI_OUT_TOKENS)
    if prompt is not None:
        payload["prompt_tokens"] = int(prompt)
    if completion is not None:
        payload["completion_tokens"] = int(completion)
    if prompt is not None and completion is not None:
        payload["total_tokens"] = int(prompt) + int(completion)
    return payload


def _kind(attrs: Dict[str, Any]) -> str:
    op = attrs.get(_GENAI_OP)
    if op in ("chat", "text_completion", "completion", "generate_content"):
        return "llm"
    if op in ("execute_tool", "tool"):
        return "tool"
    if op in ("embeddings", "embedding"):
        return "embedding"
    return "chain"


def _status(span: Any) -> str:
    status = getattr(span, "status", None)
    code = getattr(status, "status_code", None)
    if code is not None and getattr(code, "name", "") == "ERROR":
        return "error"
    return "ok"


def _iso(ns: Optional[int]) -> Optional[str]:
    if not ns:
        return None
    return datetime.fromtimestamp(ns / 1e9, tz=timezone.utc).isoformat()


__all__: List[str] = ["PromptRailsSpanExporter", "otel_span_to_payload"]
