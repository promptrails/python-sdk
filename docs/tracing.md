# Tracing

Send spans to PromptRails from any Python code — you do **not** need to manage
your prompts or agents on the platform. This makes PromptRails usable as a
standalone LLM observability backend (like Langfuse/Helicone) for LangChain,
the OpenAI/Anthropic SDKs, or your own code.

The tracing module lives under `promptrails.tracing` and is independent of the
API-client resources. All you need is an API key with the `traces:write` scope.

> Already using LangChain, the OpenAI SDK, or OpenTelemetry? See
> [integrations](integrations.md) for auto-instrumentation instead of manual spans.

## Quick start

```python
from promptrails.tracing import Tracer

tracer = Tracer(api_key="pr_...")

with tracer.span("agent-run", kind="agent") as root:
    root.set_input({"q": "What's the weather in Istanbul?"})

    with tracer.span("llm-call", kind="llm") as llm:
        llm.set_model("gpt-4o").set_usage(prompt_tokens=120, completion_tokens=30)
        llm.set_output({"text": "18°C and rainy."})

tracer.flush()  # optional — spans also flush in the background and at exit
```

Nested spans automatically share the same `trace_id` and link to their parent,
so the tree renders correctly in the PromptRails trace viewer.

## Span data

Every `set_*` helper returns the span, so calls can be chained:

```python
with tracer.span("retrieve", kind="datasource") as span:
    span.set_input({"query": "weather istanbul"})
    span.set_output({"rows": 3})
    span.set_attributes(index="weather", cache_hit=False)
    span.set_tags("prod", "search")
    span.set_session("session-abc")
```

For LLM spans:

```python
span.set_model("gpt-4o")
span.set_usage(prompt_tokens=120, completion_tokens=30)  # total is computed
span.set_cost(0.0023)
```

Errors are captured automatically when you use the context manager — the span
is marked `error` and the exception re-raised:

```python
with tracer.span("tool", kind="tool"):
    raise ValueError("boom")   # span.status = "error", then the error propagates
```

## Decorator

```python
@tracer.trace(kind="tool")
def search(query: str) -> list[str]:
    ...
```

The span is named after the function (override with `@tracer.trace("custom-name")`).

## Manual spans

When a context block doesn't fit your control flow, create and end spans by hand.
Parent/trace linkage is inherited from the currently-active span:

```python
span = tracer.start_span("step", kind="agent_step")
try:
    ...
finally:
    span.end()
```

## Span kinds

`kind` accepts any of the PromptRails span kinds:

`agent`, `llm`, `tool`, `datasource`, `prompt`, `guardrail`, `chain`,
`workflow`, `agent_step`, `mcp_call`, `preprocessing`, `postprocessing`,
`memory`, `embedding`, `speech`, `image`, `video`, `storage`.

## Lifecycle & flushing

Spans are buffered and shipped in batches by a background daemon thread:

- automatically every `flush_interval` seconds (default `1.0`),
- immediately once the buffer reaches `max_batch_size` (default `100`),
- on interpreter exit (an `atexit` hook flushes what's left).

Export is best-effort: network failures are logged (`promptrails.tracing`
logger) and dropped, never raised into your code. Call `tracer.flush()` to block
until the buffer is sent, or `tracer.shutdown()` to flush and stop the worker
(e.g. in a short-lived script or a serverless handler).

## Configuration

```python
Tracer(
    api_key="pr_...",
    base_url="https://api.promptrails.ai",  # point at your deployment
    timeout=30.0,
    max_retries=3,
    max_batch_size=100,
    flush_interval=1.0,
)
```

### Reusing an existing client

If you already build a `PromptRails` API client, share its HTTP layer instead of
opening a second connection pool:

```python
from promptrails import PromptRails
from promptrails.tracing import Tracer

client = PromptRails(api_key="pr_...")
tracer = Tracer(http=client._http)
```

## What gets sent

Each span is POSTed to `POST /api/v1/traces/ingest`. The workspace is taken from
the API key (key-scoped), and the `source` attribute is set to `sdk` so these
traces are distinguishable from platform-managed ones in the UI.
```
