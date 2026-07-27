import json

import httpx
import pytest
import respx

from promptrails import (
    ModelConfig,
    PromptAgentConfig,
    PromptRails,
    RunBudget,
    ToolAttachment,
    WorkflowAgentConfig,
)
from promptrails.agent_config import WorkflowNode
from promptrails.exceptions import NotFoundError
from promptrails.types import Agent

BASE = "http://localhost:8082"


def _client():
    return PromptRails(api_key="key", base_url=BASE, max_retries=0)


@respx.mock
def test_list_agents():
    respx.get(f"{BASE}/api/v1/agents").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "a1",
                        "name": "Agent 1",
                        "type": "agent",
                        "status": "active",
                        "workspace_id": "ws",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                    },
                    {
                        "id": "a2",
                        "name": "Agent 2",
                        "type": "workflow",
                        "status": "draft",
                        "workspace_id": "ws",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                    },
                ],
                "meta": {"total": 2, "page": 1, "limit": 20, "total_pages": 1},
            },
        )
    )
    with _client() as client:
        result = client.agents.list()
    assert len(result.data) == 2
    assert result.meta.total == 2
    assert isinstance(result.data[0], Agent)
    assert result.data[0].name == "Agent 1"


@respx.mock
def test_get_agent():
    respx.get(f"{BASE}/api/v1/agents/a1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "a1",
                    "name": "Test Agent",
                    "type": "agent",
                    "status": "active",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        agent = client.agents.get("a1")
    assert agent.id == "a1"
    assert agent.name == "Test Agent"


@respx.mock
def test_create_agent():
    respx.post(f"{BASE}/api/v1/agents").mock(
        return_value=httpx.Response(
            201,
            json={
                "data": {
                    "id": "a3",
                    "name": "New Agent",
                    "type": "agent",
                    "status": "draft",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        agent = client.agents.create(name="New Agent", type="agent")
    assert agent.id == "a3"
    assert agent.name == "New Agent"


@respx.mock
def test_update_agent():
    respx.patch(f"{BASE}/api/v1/agents/a1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "a1",
                    "name": "Updated",
                    "type": "agent",
                    "status": "active",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        agent = client.agents.update("a1", name="Updated")
    assert agent.name == "Updated"


@respx.mock
def test_delete_agent():
    respx.delete(f"{BASE}/api/v1/agents/a1").mock(
        return_value=httpx.Response(200, json={"message": "deleted"})
    )
    with _client() as client:
        client.agents.delete("a1")


@respx.mock
def test_execute_agent():
    respx.post(f"{BASE}/api/v1/agents/a1/execute").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "output": {"result": "hello"},
                    "trace_id": "t1",
                    "execution_id": "e1",
                    "status": "completed",
                    "cost": 0.001,
                },
            },
        )
    )
    with _client() as client:
        result = client.agents.execute("a1", input={"prompt": "hi"})
    assert result.output == {"result": "hello"}
    assert result.trace_id == "t1"


@respx.mock
def test_create_agent_version_with_model_config():
    route = respx.post(f"{BASE}/api/v1/agents/a1/versions").mock(
        return_value=httpx.Response(200, json={"data": {"id": "v1", "version": "1.0.0"}})
    )
    with _client() as client:
        version = client.agents.create_version(
            "a1",
            version="1.0.0",
            config=PromptAgentConfig(prompt_id="p1"),
            model_config=ModelConfig(model_id="m1", temperature=0.2),
            run_budget=RunBudget(max_cost=1.5),
            cache_timeout=60,
            masking_enabled=True,
            tools=[ToolAttachment(mcp_tool_id="t1", requires_approval=True)],
        )
    assert version.id == "v1"
    body = json.loads(route.calls.last.request.read())
    assert body["config"] == {"prompt_id": "p1", "type": "agent"}
    assert body["model_config"] == {"model_id": "m1", "temperature": 0.2}
    assert body["run_budget"] == {"max_cost": 1.5}
    assert body["cache_timeout"] == 60
    assert body["masking_enabled"] is True
    assert body["tools"] == [{"mcp_tool_id": "t1", "requires_approval": True, "no_retry": False}]


@respx.mock
def test_create_workflow_version():
    route = respx.post(f"{BASE}/api/v1/agents/a2/versions").mock(
        return_value=httpx.Response(200, json={"data": {"id": "v2"}})
    )
    with _client() as client:
        client.agents.create_version(
            "a2",
            version="1.0.0",
            config=WorkflowAgentConfig(nodes=[WorkflowNode(id="n1", prompt_id="p1")]),
        )
    body = json.loads(route.calls.last.request.read())
    assert body["config"]["type"] == "workflow"
    assert body["config"]["nodes"][0]["id"] == "n1"


@respx.mock
def test_agent_playground():
    route = respx.post(f"{BASE}/api/v1/agents/a1/playground").mock(
        return_value=httpx.Response(200, json={"data": {"output": {"content": "hi"}}})
    )
    with _client() as client:
        result = client.agents.playground(
            "a1",
            input={"q": "x"},
            prompt_override={"system_prompt": "be terse"},
        )
    assert result["output"]["content"] == "hi"
    body = json.loads(route.calls.last.request.read())
    assert body["prompt_override"] == {"system_prompt": "be terse"}


@respx.mock
def test_not_found():
    respx.get(f"{BASE}/api/v1/agents/missing").mock(
        return_value=httpx.Response(404, json={"error": {"message": "agent not found"}})
    )
    with _client() as client:
        with pytest.raises(NotFoundError):
            client.agents.get("missing")
