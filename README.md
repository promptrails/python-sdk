# PromptRails Python SDK

[![PyPI version](https://img.shields.io/pypi/v/promptrails.svg)](https://pypi.org/project/promptrails/)
[![Python versions](https://img.shields.io/pypi/pyversions/promptrails.svg)](https://pypi.org/project/promptrails/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [PromptRails](https://promptrails.ai) — the AI agent orchestration platform.

The SDK has two independent parts:

- **API client** — manage agents, prompts, executions, and more.
- **Tracing** (`promptrails.tracing`) — send spans to PromptRails from any code,
  without managing your prompts/agents on the platform.

## Installation

```bash
pip install promptrails
```

## Quick Start

### API client

```python
from promptrails import PromptRails

client = PromptRails(api_key="pr_key_...")
result = client.agents.execute("agent-id", input={"query": "Summarise this week's sales"})
print(result.output)
client.close()
```

Async (`AsyncPromptRails`) and context-manager usage are also supported — see the
[API client guide](docs/api-client.md).

### Tracing

```python
from promptrails.tracing import Tracer

tracer = Tracer(api_key="pr_...")

with tracer.span("agent-run", kind="agent") as root:
    root.set_input({"q": "weather?"})
    with tracer.span("llm-call", kind="llm") as llm:
        llm.set_model("gpt-4o").set_usage(prompt_tokens=120, completion_tokens=30)

tracer.flush()
```

See the [tracing guide](docs/tracing.md) for decorators, manual spans, span
kinds, and configuration. LangChain, OpenAI, and OpenTelemetry can be
auto-instrumented — see [integrations](docs/integrations.md).

## Documentation

- [API client](docs/api-client.md) — resources, error handling, agent versions, approvals, configuration
- [Tracing](docs/tracing.md) — spans, decorators, batching, configuration
- [Integrations](docs/integrations.md) — LangChain, OpenAI, OpenTelemetry

## Contributing

```bash
pip install -e ".[dev]"   # install dev dependencies
ruff check .              # lint
ruff format .             # format
pytest tests/ -v          # test
```

## License

MIT
