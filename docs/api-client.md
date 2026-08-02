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
| `client.agents`           | `list`, `get`, `create`, `update`, `delete`, `execute`, `list_versions`, `create_version`, `promote_version`, `preview`, `playground`, `list_guardrails`, `create_guardrail` |
| `client.prompts`          | `list`, `get`, `create`, `update`, `delete`, `list_versions`, `create_version` (content-only), `promote_version`, `preview` |
| `client.executions`       | `list`, `get`, `tree`, `cancel`, `approval_inbox`, `approve`, `deny`, `stream` |
| `client.credentials`      | `list`, `get`, `create`, `update`, `delete`, `set_default`, `check_connection` |
| `client.data_sources`     | `list`, `get`, `create`, `update`, `delete`, `list_versions`, `create_version`, `test_connection`, `query` |
| `client.chat`             | `list_sessions`, `get_session`, `create_session`, `delete_session`, `list_messages`, `send_message` |
| `client.traces`           | `list`, `get_by_trace_id`, `get_summary`, `pii_report`, `ingest`         |
| `client.mcp_tools`        | `list`, `get`, `create`, `update`, `delete`                              |
| `client.guardrails`       | `list_scanners`, `update`, `delete`                                      |
| `client.llm_models`       | `list`, `list_available`                                                 |
| `client.agent_triggers`   | `list`, `get`, `create` (with `source` + `source_config`), `update`, `delete` |
| `client.agent_vfs`        | `list`, `read`, `write`, `stat`, `mkdir`, `move`, `copy`, `delete`, `grep`, `glob`, `usage` |
| `client.a2a`              | `get_agent_card`, `send_message`, `get_task`, `list_tasks`, `cancel_task` |
| `client.assets`           | `list`, `get`, `delete`, `get_signed_url`                                |

## Agent versions (model config)

In API v2 a prompt version is pure content — model, sampling, tools, budget,
approval policy and cache TTL are owned by the **agent version**:

```python
from promptrails import (
    PromptAgentConfig, ModelConfig, RunBudget, ApprovalPolicy, ToolAttachment,
)

client.agents.create_version(
    "agent-id",
    version="1.0.0",
    config=PromptAgentConfig(prompt_id="prompt-id"),
    model_config=ModelConfig(model_id="llm-model-id", temperature=0.2),
    run_budget=RunBudget(max_cost=2.0, max_depth=4),
    approval_policy=ApprovalPolicy(mode="admins"),
    cache_timeout=300,
    tools=[ToolAttachment(mcp_tool_id="tool-id", requires_approval=True)],
)
```

## Human-in-the-loop approvals

Executions form a tree and can park at `waiting_approval`:

```python
for execution in client.executions.approval_inbox().data:
    client.executions.approve(execution.id)   # or .deny(execution.id, reason="…")

tree = client.executions.tree("execution-id")  # full children[] populated
client.executions.cancel("execution-id")       # cooperative cancel
```

## Assets

```python
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
