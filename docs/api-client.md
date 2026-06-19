# API Client

The `PromptRails` (sync) and `AsyncPromptRails` (async) clients wrap the
PromptRails REST API for managing agents, prompts, executions, and more.

```python
from promptrails import PromptRails

client = PromptRails(api_key="pr_key_...")
result = client.agents.execute("agent-id", input={"query": "Summarise sales"})
print(result.output)
client.close()
```

## Error handling

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

## Available resources

| Resource                  | Methods                                                                  |
| ------------------------- | ------------------------------------------------------------------------ |
| `client.agents`           | `list`, `get`, `create`, `update`, `delete`, `execute`, `list_versions`, `create_version`, `list_guardrails`, `create_guardrail` |
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
| `client.agent_triggers`   | `list`, `get`, `create` (with `source` + `source_config`), `update`, `delete` |
| `client.agent_vfs`        | `list`, `read`, `write`, `stat`, `mkdir`, `move`, `copy`, `delete`, `grep`, `glob`, `usage` |
| `client.a2a`              | `get_agent_card`, `send_message`, `get_task`, `list_tasks`, `cancel_task` |
| `client.media_models`     | `list`                                                                   |
| `client.media`            | `generate`                                                               |
| `client.assets`           | `list`, `get`, `delete`, `get_signed_url`                                |

## Media Studio

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
