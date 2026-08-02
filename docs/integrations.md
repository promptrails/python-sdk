# Tracing integrations

Auto-instrument popular frameworks so their calls become PromptRails spans. Each
integration only needs its own optional dependency.

```bash
pip install "promptrails[langchain]"   # or [openai], [anthropic], [google], [otel]
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

## OpenAI

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

## Anthropic

Wrap an Anthropic client to trace every `messages.create` call:

```python
from anthropic import Anthropic
from promptrails.tracing.integrations.anthropic import trace_anthropic

client = trace_anthropic(Anthropic(), tracer)
client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, messages=[...])
```

Install with `pip install "promptrails[anthropic]"`.

## Google GenAI

Wrap a Google GenAI client (the unified `google-genai` SDK) to trace every
`models.generate_content` call:

```python
from google import genai
from promptrails.tracing.integrations.google import trace_google

client = trace_google(genai.Client(), tracer)
client.models.generate_content(model="gemini-2.0-flash", contents="Hello")
```

Install with `pip install "promptrails[google]"`.

## OpenTelemetry

Already using OpenTelemetry? Register the PromptRails exporter and your existing
spans flow in — `gen_ai.*` semantic-convention attributes are mapped onto the
span model:

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from promptrails.tracing.integrations.otel import PromptRailsSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(PromptRailsSpanExporter(api_key="pr_...")))
```
