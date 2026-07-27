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
async def test_async_agent_vfs():
    respx.get(f"{BASE}/api/v1/agents/ag1/vfs").mock(
        return_value=_ok({"data": {"items": [{"path": "/a.txt"}], "total": 1}})
    )
    respx.get(f"{BASE}/api/v1/agents/ag1/vfs/usage").mock(
        return_value=_ok({"data": {"bytes_used": 42}})
    )
    respx.put(f"{BASE}/api/v1/agents/ag1/vfs/file").mock(
        return_value=_ok({"data": {"path": "/a.txt"}})
    )
    async with _client() as c:
        assert len(await c.agent_vfs.list("ag1")) == 1
        assert await c.agent_vfs.usage("ag1") == 42
        await c.agent_vfs.write("ag1", "/a.txt", "hi")


@pytest.mark.asyncio
@respx.mock
async def test_async_data_sources():
    respx.get(f"{BASE}/api/v1/data-sources").mock(return_value=_page([{"id": "d1"}]))
    respx.post(f"{BASE}/api/v1/data-sources").mock(
        return_value=_ok({"data": {"id": "d1", "name": "x"}})
    )
    respx.delete(f"{BASE}/api/v1/data-sources/d1").mock(return_value=_ok({}))
    async with _client() as c:
        assert len((await c.data_sources.list()).data) == 1
        assert (await c.data_sources.create(name="x", type="postgres")).name == "x"
        await c.data_sources.delete("d1")


@pytest.mark.asyncio
@respx.mock
async def test_async_mcp_tools():
    respx.get(f"{BASE}/api/v1/mcp-tools").mock(return_value=_page([{"id": "m1"}]))
    respx.get(f"{BASE}/api/v1/mcp-tools/m1").mock(return_value=_ok({"data": {"id": "m1"}}))
    respx.post(f"{BASE}/api/v1/mcp-tools/m1/discover").mock(
        return_value=_ok({"data": {"tools": []}})
    )
    async with _client() as c:
        assert len((await c.mcp_tools.list()).data) == 1
        assert (await c.mcp_tools.get("m1")).id == "m1"
        await c.mcp_tools.discover_tools("m1")


@pytest.mark.asyncio
@respx.mock
async def test_async_chat():
    respx.get(f"{BASE}/api/v1/chat/sessions").mock(return_value=_page([{"id": "s1"}]))
    respx.post(f"{BASE}/api/v1/chat/sessions").mock(return_value=_ok({"data": {"id": "s1"}}))
    respx.post(f"{BASE}/api/v1/chat/sessions/s1/messages").mock(
        return_value=_ok({"data": {"id": "m1"}})
    )
    respx.delete(f"{BASE}/api/v1/chat/sessions/s1").mock(return_value=_ok({}))
    async with _client() as c:
        assert len((await c.chat.list_sessions()).data) == 1
        await c.chat.create_session(agent_id="a1")
        await c.chat.send_message("s1", content="hi")
        await c.chat.delete_session("s1")


@pytest.mark.asyncio
@respx.mock
async def test_async_execution_approvals_triggers():
    respx.get(f"{BASE}/api/v1/executions/approval-inbox").mock(
        return_value=_page([{"id": "e1", "status": "waiting_approval"}])
    )
    respx.post(f"{BASE}/api/v1/executions/e1/approve").mock(
        return_value=_ok({"data": {"id": "e1", "status": "running"}})
    )
    respx.get(f"{BASE}/api/v1/triggers").mock(return_value=_page([{"id": "t1"}]))
    respx.post(f"{BASE}/api/v1/triggers").mock(return_value=_ok({"data": {"id": "t1"}}))
    async with _client() as c:
        assert len((await c.executions.approval_inbox()).data) == 1
        assert (await c.executions.approve("e1")).status == "running"
        assert len((await c.agent_triggers.list()).data) == 1
        await c.agent_triggers.create(name="t", agent_id="a1")
