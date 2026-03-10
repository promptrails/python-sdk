import httpx
import respx

from promptrails import PromptRails
from promptrails.types import Prompt

BASE = "http://localhost:8082"


def _client():
    return PromptRails(api_key="key", base_url=BASE, max_retries=0)


@respx.mock
def test_list_prompts():
    respx.get(f"{BASE}/api/v1/prompts").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "p1",
                        "name": "Prompt 1",
                        "status": "active",
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
        result = client.prompts.list()
    assert len(result.data) == 1
    assert isinstance(result.data[0], Prompt)
    assert result.data[0].name == "Prompt 1"


@respx.mock
def test_get_prompt():
    respx.get(f"{BASE}/api/v1/prompts/p1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "p1",
                    "name": "Test Prompt",
                    "status": "active",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        prompt = client.prompts.get("p1")
    assert prompt.id == "p1"
    assert prompt.name == "Test Prompt"


@respx.mock
def test_create_prompt():
    respx.post(f"{BASE}/api/v1/prompts").mock(
        return_value=httpx.Response(
            201,
            json={
                "data": {
                    "id": "p2",
                    "name": "New Prompt",
                    "status": "draft",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        prompt = client.prompts.create(name="New Prompt")
    assert prompt.id == "p2"
    assert prompt.name == "New Prompt"


@respx.mock
def test_update_prompt():
    respx.patch(f"{BASE}/api/v1/prompts/p1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "p1",
                    "name": "Updated",
                    "status": "active",
                    "workspace_id": "ws",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            },
        )
    )
    with _client() as client:
        prompt = client.prompts.update("p1", name="Updated")
    assert prompt.name == "Updated"


@respx.mock
def test_delete_prompt():
    respx.delete(f"{BASE}/api/v1/prompts/p1").mock(
        return_value=httpx.Response(200, json={"message": "deleted"})
    )
    with _client() as client:
        client.prompts.delete("p1")
