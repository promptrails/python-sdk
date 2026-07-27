import httpx
import pytest
import respx

from promptrails import AsyncPromptRails

BASE = "http://localhost:8082"


def _client():
    return AsyncPromptRails(api_key="key", base_url=BASE, max_retries=0)


def _ok(json):
    return httpx.Response(200, json=json)


def _page(items):
    return _ok(
        {
            "data": items,
            "meta": {"total": len(items), "page": 1, "limit": 20, "total_pages": 1},
        }
    )


@pytest.mark.asyncio
@respx.mock
async def test_async_a2a_card_and_cancel():
    respx.get(f"{BASE}/a2a/agents/ag1/agent-card.json").mock(return_value=_ok({"name": "Card"}))
    respx.post(f"{BASE}/a2a/tasks/cancel").mock(
        return_value=_ok({"result": {"id": "t1", "status": "canceled"}})
    )
    async with _client() as c:
        card = await c.a2a.get_agent_card("ag1")
        task = await c.a2a.cancel_task("t1")
    assert card.name == "Card"
    assert task.status == "canceled"


@pytest.mark.asyncio
@respx.mock
async def test_async_a2a_list_tasks():
    respx.get(f"{BASE}/api/v1/a2a/tasks").mock(return_value=_page([{"id": "t1"}]))
    async with _client() as c:
        result = await c.a2a.list_tasks()
    assert len(result.data) == 1


@pytest.mark.asyncio
@respx.mock
async def test_async_credentials_crud():
    respx.get(f"{BASE}/api/v1/credentials").mock(return_value=_page([{"id": "c1"}]))
    respx.get(f"{BASE}/api/v1/credentials/c1").mock(return_value=_ok({"data": {"id": "c1"}}))
    respx.post(f"{BASE}/api/v1/credentials").mock(
        return_value=_ok({"data": {"id": "c1", "name": "key"}})
    )
    respx.delete(f"{BASE}/api/v1/credentials/c1").mock(return_value=_ok({}))
    respx.post(f"{BASE}/api/v1/credentials/c1/set-default").mock(
        return_value=_ok({"data": {"id": "c1"}})
    )

    async with _client() as c:
        assert len((await c.credentials.list()).data) == 1
        assert (await c.credentials.get("c1")).id == "c1"
        created = await c.credentials.create(name="key", type="api_key", category="llm", value="sk")
        assert created.name == "key"
        await c.credentials.delete("c1")
        await c.credentials.set_default("c1")


@pytest.mark.asyncio
@respx.mock
async def test_async_assets():
    respx.get(f"{BASE}/api/v1/assets").mock(return_value=_page([{"id": "a1"}]))
    respx.get(f"{BASE}/api/v1/assets/a1").mock(
        return_value=_ok({"data": {"id": "a1", "file_name": "x.png"}})
    )
    respx.get(f"{BASE}/api/v1/assets/a1/signed-url").mock(
        return_value=_ok({"data": {"url": "https://signed"}})
    )
    async with _client() as c:
        listed = await c.assets.list(type="image")
        asset = await c.assets.get("a1")
        signed = await c.assets.get_signed_url("a1")
    assert len(listed.data) == 1
    assert asset.id == "a1"
    assert signed.url == "https://signed"


@pytest.mark.asyncio
@respx.mock
async def test_async_traces_summary():
    respx.get(f"{BASE}/api/v1/traces/summary").mock(
        return_value=_ok({"data": {"total_traces": 5, "total_cost": 0.02}})
    )
    async with _client() as c:
        summary = await c.traces.get_summary(session_id="sess1")
    assert summary.total_traces == 5
    assert summary.total_cost == 0.02
