import json

import httpx
import respx

from promptrails.tracing import Span, Tracer

BASE = "http://localhost:8082"
INGEST = f"{BASE}/api/v1/traces/ingest"


def _tracer():
    # Long flush interval so the background worker never races the explicit
    # flush() the tests rely on for determinism.
    return Tracer(api_key="key", base_url=BASE, max_retries=0, flush_interval=3600)


def _posted_spans():
    """Collect every span across all ingest POSTs recorded by respx."""
    spans = []
    for call in respx.calls:
        if call.request.url.path == "/api/v1/traces/ingest":
            spans.extend(json.loads(call.request.content)["spans"])
    return spans


@respx.mock
def test_nested_spans_share_trace_and_link_parent():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 2}}))

    tracer = _tracer()
    with tracer.span("agent-run", kind="agent") as root:
        root.set_input({"q": "weather?"})
        with tracer.span("llm-call", kind="llm") as llm:
            llm.set_model("gpt-4o").set_usage(120, 30).set_output({"text": "rainy"})
    tracer.flush()

    spans = {s["name"]: s for s in _posted_spans()}
    assert set(spans) == {"agent-run", "llm-call"}

    root, llm = spans["agent-run"], spans["llm-call"]
    assert root["trace_id"] == llm["trace_id"]
    assert "parent_span_id" not in root  # root has no parent
    assert llm["parent_span_id"] == root["span_id"]

    assert root["kind"] == "agent"
    assert llm["kind"] == "llm"
    assert llm["model_name"] == "gpt-4o"
    assert llm["prompt_tokens"] == 120
    assert llm["completion_tokens"] == 30
    assert llm["total_tokens"] == 150
    assert llm["output"] == {"text": "rainy"}


@respx.mock
def test_exception_marks_span_error_and_propagates():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 1}}))

    tracer = _tracer()
    try:
        with tracer.span("boom", kind="tool"):
            raise ValueError("kaboom")
    except ValueError:
        pass
    tracer.flush()

    span = _posted_spans()[0]
    assert span["status"] == "error"
    assert span["level"] == "error"
    assert span["error_type"] == "ValueError"
    assert span["error_message"] == "kaboom"


@respx.mock
def test_decorator_creates_span():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 1}}))

    tracer = _tracer()

    @tracer.trace(kind="tool")
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    tracer.flush()

    span = _posted_spans()[0]
    assert span["name"] == "add"
    assert span["kind"] == "tool"


@respx.mock
def test_tags_are_sent_as_array():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 1}}))

    tracer = _tracer()
    with tracer.span("tagged") as span:
        span.set_tags("prod", "checkout")
    tracer.flush()

    assert _posted_spans()[0]["tags"] == ["prod", "checkout"]


def test_span_payload_shape_without_http():
    # Pure unit check on the serialized shape — no exporter/network involved.
    span = Span("x", kind="llm", trace_id="t", parent_span_id="p")
    span.set_usage(10, 5).set_cost(0.01).set_model("m")
    span.end()
    payload = span.to_payload()
    assert payload["trace_id"] == "t"
    assert payload["parent_span_id"] == "p"
    assert payload["total_tokens"] == 15
    assert payload["cost"] == 0.01
    assert payload["started_at"] and payload["ended_at"]
