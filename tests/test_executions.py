import httpx
import respx

from promptrails import PromptRails
from promptrails.types import AgentExecution

BASE = "http://localhost:8082"


def _client():
    return PromptRails(api_key="key", base_url=BASE, max_retries=0)


@respx.mock
def test_list_executions():
    respx.get(f"{BASE}/api/v1/executions").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "e1",
                        "agent_id": "a1",
                        "status": "completed",
                        "workspace_id": "ws",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                    },
                ],
                "meta": {"total": 1, "page": 1, "limit": 20, "total_pages": 1},
            },
        )
    )
    with _client() as client:
        result = client.executions.list()
    assert len(result.data) == 1
    assert result.data[0].status == "completed"


@respx.mock
def test_get_execution():
    respx.get(f"{BASE}/api/v1/executions/e1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "e1",
                    "agent_id": "a1",
                    "status": "completed",
                    "workspace_id": "ws",
                    "input": {"query": "test"},
                    "output": {"result": "ok"},
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        execution = client.executions.get("e1")
    assert execution.id == "e1"
    assert execution.status == "completed"
