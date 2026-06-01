import json
import uuid

import httpx
import respx

from promptrails.tracing import Tracer
from promptrails.tracing.integrations.langchain import PromptRailsCallbackHandler
from promptrails.tracing.integrations.openai import trace_openai
from promptrails.tracing.integrations.otel import otel_span_to_payload

BASE = "http://localhost:8082"
INGEST = f"{BASE}/api/v1/traces/ingest"


def _tracer():
    return Tracer(api_key="key", base_url=BASE, max_retries=0, flush_interval=3600)


def _posted_spans():
    spans = []
    for call in respx.calls:
        if call.request.url.path == "/api/v1/traces/ingest":
            spans.extend(json.loads(call.request.content)["spans"])
    return spans


# -- LangChain ------------------------------------------------------------


class _FakeLLMResult:
    def __init__(self):
        self.llm_output = {
            "token_usage": {"prompt_tokens": 10, "completion_tokens": 5},
            "model_name": "gpt-4o",
        }
        self.generations = [[type("G", (), {"text": "hi"})()]]


@respx.mock
def test_langchain_handler_builds_span_tree():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 2}}))

    tracer = _tracer()
    handler = PromptRailsCallbackHandler(tracer)

    chain_id, llm_id = uuid.uuid4(), uuid.uuid4()
    handler.on_chain_start({"name": "AgentExecutor"}, {"q": "hi"}, run_id=chain_id)
    handler.on_llm_start({"name": "ChatOpenAI"}, ["prompt"], run_id=llm_id, parent_run_id=chain_id)
    handler.on_llm_end(_FakeLLMResult(), run_id=llm_id)
    handler.on_chain_end({"answer": "done"}, run_id=chain_id)
    tracer.flush()

    spans = {s["name"]: s for s in _posted_spans()}
    assert set(spans) == {"AgentExecutor", "ChatOpenAI"}
    chain, llm = spans["AgentExecutor"], spans["ChatOpenAI"]
    assert chain["trace_id"] == llm["trace_id"]
    assert "parent_span_id" not in chain
    assert llm["parent_span_id"] == chain["span_id"]
    assert llm["kind"] == "llm"
    assert llm["model_name"] == "gpt-4o"
    assert llm["prompt_tokens"] == 10
    assert llm["total_tokens"] == 15


@respx.mock
def test_langchain_handler_records_errors():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 1}}))
    tracer = _tracer()
    handler = PromptRailsCallbackHandler(tracer)

    run_id = uuid.uuid4()
    handler.on_tool_start({"name": "search"}, "query", run_id=run_id)
    handler.on_tool_error(ValueError("boom"), run_id=run_id)
    tracer.flush()

    span = _posted_spans()[0]
    assert span["kind"] == "tool"
    assert span["status"] == "error"
    assert span["error_type"] == "ValueError"


# -- OpenAI ---------------------------------------------------------------


class _FakeUsage:
    prompt_tokens = 12
    completion_tokens = 8
    total_tokens = 20


class _FakeResp:
    model = "gpt-4o"
    usage = _FakeUsage()

    def __init__(self):
        self.choices = [type("C", (), {"message": type("M", (), {"content": "hello"})()})()]


class _FakeClient:
    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                return _FakeResp()


@respx.mock
def test_trace_openai_wraps_create():
    respx.post(INGEST).mock(return_value=httpx.Response(200, json={"data": {"ingested": 1}}))
    tracer = _tracer()
    client = trace_openai(_FakeClient(), tracer)

    resp = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": "hi"}]
    )
    assert resp.model == "gpt-4o"
    tracer.flush()

    span = _posted_spans()[0]
    assert span["kind"] == "llm"
    assert span["model_name"] == "gpt-4o"
    assert span["prompt_tokens"] == 12
    assert span["completion_tokens"] == 8
    assert span["total_tokens"] == 20
    assert span["output"] == {"content": "hello"}


# -- OpenTelemetry mapper -------------------------------------------------


def test_otel_span_to_payload_maps_genai():
    span = type(
        "S",
        (),
        {
            "name": "chat gpt-4o",
            "context": type("Ctx", (), {"trace_id": 0x0AF7, "span_id": 0xB7AD})(),
            "parent": type("P", (), {"span_id": 0xEEC0})(),
            "attributes": {
                "gen_ai.operation.name": "chat",
                "gen_ai.response.model": "gpt-4o-mini",
                "gen_ai.usage.input_tokens": 100,
                "gen_ai.usage.output_tokens": 20,
            },
            "start_time": 1_700_000_000_000_000_000,
            "end_time": 1_700_000_001_000_000_000,
            "status": type("St", (), {"status_code": type("Code", (), {"name": "OK"})()})(),
        },
    )()

    payload = otel_span_to_payload(span)
    assert payload["trace_id"] == format(0x0AF7, "032x")
    assert payload["span_id"] == format(0xB7AD, "016x")
    assert payload["parent_span_id"] == format(0xEEC0, "016x")
    assert payload["kind"] == "llm"
    assert payload["model_name"] == "gpt-4o-mini"
    assert payload["prompt_tokens"] == 100
    assert payload["total_tokens"] == 120
    assert payload["status"] == "ok"
    assert payload["started_at"] and payload["ended_at"]
