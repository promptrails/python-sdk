# PromptRails Python SDK

[![PyPI version](https://img.shields.io/pypi/v/promptrails.svg)](https://pypi.org/project/promptrails/)
[![Python versions](https://img.shields.io/pypi/pyversions/promptrails.svg)](https://pypi.org/project/promptrails/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [PromptRails](https://promptrails.ai) — the AI agent orchestration platform.

## Installation

```bash
pip install promptrails
```

## Quick Start

### Synchronous

```python
from promptrails import PromptRails

client = PromptRails(api_key="pr_key_...")

# Execute an agent
result = client.agents.execute("agent-id", input={"query": "Summarise this week's sales"})
print(result.output)

client.close()
```

### Async

```python
import asyncio
from promptrails import AsyncPromptRails

async def main():
    async with AsyncPromptRails(api_key="pr_key_...") as client:
        result = await client.agents.execute("agent-id", input={"query": "hello"})
        print(result.output)

asyncio.run(main())
```

### Context Manager

```python
with PromptRails(api_key="pr_key_...") as client:
    agents = client.agents.list()
    for agent in agents.data:
        print(agent.name)
```

## Error Handling

```python
from promptrails import NotFoundError, ValidationError, RateLimitError, QuotaExceededError

try:
    result = client.agents.execute("agent-id", input={})
except QuotaExceededError:
    print("Execution limit reached — upgrade your plan")
except RateLimitError:
    print("Too many requests, back off and retry")
except NotFoundError as e:
    print(f"Agent not found: {e.message}")
```

## Available Resources

| Resource                  | Methods                                                                  |
| ------------------------- | ------------------------------------------------------------------------ |
| `client.agents`           | `list`, `get`, `create`, `update`, `delete`, `execute`, `list_versions`, `create_version`, `list_guardrails`, `create_guardrail`, `list_memories`, `create_memory`, `search_memories`, `delete_all_memories` |
| `client.prompts`          | `list`, `get`, `create`, `update`, `delete`, `list_versions`, `create_version` |
| `client.executions`       | `list`, `get`                                                            |
| `client.credentials`      | `list`, `get`, `create`, `update`, `delete`, `set_default`, `check_connection` |
| `client.data_sources`     | `list`, `get`, `create`, `update`, `delete`, `list_versions`, `create_version`, `test_connection`, `query` |
| `client.chat`             | `list_sessions`, `get_session`, `create_session`, `delete_session`, `list_messages`, `send_message` |
| `client.traces`           | `list`, `get_by_trace_id`                                                |
| `client.costs`            | `get_summary`, `get_agent_summary`                                       |
| `client.scores`           | `list`, `get`, `create`, `update`, `delete`, `list_configs`, `get_config`, `create_config`, `update_config`, `delete_config`, `aggregates` |
| `client.mcp_tools`        | `list`, `get`, `create`, `update`, `delete`                              |
| `client.approvals`        | `list`, `get`, `decide`                                                  |
| `client.webhook_triggers` | `list`, `get`, `create`, `update`, `delete`                              |
| `client.a2a`              | `get_agent_card`, `send_message`, `get_task`, `list_tasks`, `cancel_task` |
| `client.media_models`     | `list`                                                                   |
| `client.media`            | `generate`                                                               |
| `client.assets`           | `list`, `get`, `delete`, `get_signed_url`                                |

### Media Studio

Generate images, speech, and video using various providers:

```python
# List available media models
models = client.media_models.list(media_type="image")
for model in models:
    print(f"{model.provider}/{model.model_id}: {model.display_name}")

# Generate an image
result = client.media.generate(
    provider="fal",
    media_type="image",
    model="fal-ai/flux/schnell",
    prompt="A futuristic cityscape at sunset",
    config={"width": 1024, "height": 768},
)
print(result.url)

# List assets
assets = client.assets.list(type="image")
for asset in assets.data:
    print(f"{asset.file_name} ({asset.mime_type})")

# Get a signed download URL
signed = client.assets.get_signed_url(asset_id="asset-id")
print(signed.url)

# Delete an asset
client.assets.delete(asset_id="asset-id")
```

## Configuration

| Option        | Default                      | Description                       |
| ------------- | ---------------------------- | --------------------------------- |
| `api_key`     | required                     | API key                           |
| `base_url`    | `https://api.promptrails.ai` | API base URL                      |
| `timeout`     | `30.0`                       | Request timeout (seconds)         |
| `max_retries` | `3`                          | Max retries on network/5xx errors |

## Contributing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linter
ruff check .

# Run formatter
ruff format .

# Run tests
pytest tests/ -v
```

## License

MIT
