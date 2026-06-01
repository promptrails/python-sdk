# Tracing integrations

Auto-instrument popular frameworks so their calls become PromptRails spans. Each
integration only needs its own optional dependency.

```bash
pip install "promptrails[langchain]"   # or [openai], or [otel]
```

## LangChain

A callback handler that turns LangChain runs (chains, LLMs, tools, retrievers)
into a span tree. Pass it via `callbacks`:

```python
from promptrails.tracing import Tracer
from promptrails.tracing.integrations.langchain import PromptRailsCallbackHandler

tracer = Tracer(api_key="pr_...")
handler = PromptRailsCallbackHandler(tracer)

chain.invoke({"question": "What's the weather?"}, config={"callbacks": [handler]})
tracer.flush()
```

The tree is built from LangChain's `run_id`/`parent_run_id`, so it is correct
under threads and async runs. Token usage and model are read from `on_llm_end`.

## OpenAI / Anthropic

Wrap an OpenAI-compatible client so every `chat.completions.create` call emits an
`llm` span with model, token usage, latency, and output:

```python
from openai import OpenAI
from promptrails.tracing import Tracer
from promptrails.tracing.integrations.openai import trace_openai

tracer = Tracer(api_key="pr_...")
client = trace_openai(OpenAI(), tracer)

client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": "hi"}])
```

The wrapper is duck-typed, so it also works with any API-compatible client.

## OpenTelemetry

Already using OpenTelemetry? Register the PromptRails exporter and your existing
spans flow in — `gen_ai.*` semantic-convention attributes are mapped onto the
span model:

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from promptrails.tracing.integrations.otel import PromptRailsSpanExporter

provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(PromptRailsSpanExporter(api_key="pr_..."))
)
```
