import httpx
import respx

from promptrails import PromptRails

BASE = "http://localhost:8082"


def _client():
    return PromptRails(api_key="key", base_url=BASE, max_retries=0)


def _ok(json):
    return httpx.Response(200, json=json)


def _page(items):
    return _ok(
        {
            "data": items,
            "meta": {"total": len(items), "page": 1, "limit": 20, "total_pages": 1},
        }
    )


# --------------------------- Agent VFS ---------------------------


@respx.mock
def test_agent_vfs_list_and_usage():
    respx.get(f"{BASE}/api/v1/agents/ag1/vfs").mock(
        return_value=_ok({"data": {"items": [{"path": "/a.txt"}], "total": 1}})
    )
    respx.get(f"{BASE}/api/v1/agents/ag1/vfs/usage").mock(
        return_value=_ok({"data": {"bytes_used": 42}})
    )
    with _client() as c:
        items = c.agent_vfs.list("ag1")
        used = c.agent_vfs.usage("ag1")
    assert len(items) == 1
    assert used == 42


@respx.mock
def test_agent_vfs_write_and_move():
    write = respx.put(f"{BASE}/api/v1/agents/ag1/vfs/file").mock(
        return_value=_ok({"data": {"path": "/a.txt"}})
    )
    move = respx.post(f"{BASE}/api/v1/agents/ag1/vfs/move").mock(return_value=_ok({}))
    with _client() as c:
        c.agent_vfs.write("ag1", "/a.txt", "hi")
        c.agent_vfs.move("ag1", "/a.txt", "/b.txt")
    assert write.called
    body = move.calls.last.request.read()
    assert b'"from"' in body and b'"to"' in body


@respx.mock
def test_agent_vfs_stat_mkdir():
    respx.get(f"{BASE}/api/v1/agents/ag1/vfs/stat").mock(
        return_value=_ok({"data": {"path": "/a.txt"}})
    )
    respx.post(f"{BASE}/api/v1/agents/ag1/vfs/mkdir").mock(
        return_value=_ok({"data": {"path": "/d"}})
    )
    with _client() as c:
        assert c.agent_vfs.stat("ag1", "/a.txt").path == "/a.txt"
        assert c.agent_vfs.mkdir("ag1", "/d").path == "/d"


# --------------------------- Data Sources ---------------------------


@respx.mock
def test_data_sources_crud():
    respx.get(f"{BASE}/api/v1/data-sources").mock(return_value=_page([{"id": "d1"}]))
    respx.get(f"{BASE}/api/v1/data-sources/d1").mock(return_value=_ok({"data": {"id": "d1"}}))
    respx.post(f"{BASE}/api/v1/data-sources").mock(
        return_value=_ok({"data": {"id": "d1", "name": "x"}})
    )
    respx.patch(f"{BASE}/api/v1/data-sources/d1").mock(return_value=_ok({"data": {"id": "d1"}}))
    respx.delete(f"{BASE}/api/v1/data-sources/d1").mock(return_value=_ok({}))

    with _client() as c:
        assert len(c.data_sources.list().data) == 1
        assert c.data_sources.get("d1").id == "d1"
        assert c.data_sources.create(name="x", type="postgres").name == "x"
        c.data_sources.update("d1", name="y")
        c.data_sources.delete("d1")


@respx.mock
def test_data_sources_test_connection():
    route = respx.post(f"{BASE}/api/v1/data-sources/d1/test-connection").mock(
        return_value=_ok({"data": {"ok": True}})
    )
    with _client() as c:
        result = c.data_sources.test_connection("d1")
    assert route.called
    assert result == {"ok": True}


# --------------------------- MCP Tools ---------------------------


@respx.mock
def test_mcp_tools_crud_and_discover():
    respx.get(f"{BASE}/api/v1/mcp-tools").mock(return_value=_page([{"id": "m1"}]))
    respx.get(f"{BASE}/api/v1/mcp-tools/m1").mock(return_value=_ok({"data": {"id": "m1"}}))
    respx.delete(f"{BASE}/api/v1/mcp-tools/m1").mock(return_value=_ok({}))
    discover = respx.post(f"{BASE}/api/v1/mcp-tools/m1/discover").mock(
        return_value=_ok({"data": {"tools": []}})
    )
    with _client() as c:
        assert len(c.mcp_tools.list().data) == 1
        assert c.mcp_tools.get("m1").id == "m1"
        c.mcp_tools.discover_tools("m1")
        c.mcp_tools.delete("m1")
    assert discover.called


# --------------------------- Chat ---------------------------


@respx.mock
def test_chat_sessions():
    respx.get(f"{BASE}/api/v1/chat/sessions").mock(return_value=_page([{"id": "s1"}]))
    respx.get(f"{BASE}/api/v1/chat/sessions/s1").mock(return_value=_ok({"data": {"id": "s1"}}))
    respx.post(f"{BASE}/api/v1/chat/sessions").mock(return_value=_ok({"data": {"id": "s1"}}))
    respx.delete(f"{BASE}/api/v1/chat/sessions/s1").mock(return_value=_ok({}))
    msg = respx.post(f"{BASE}/api/v1/chat/sessions/s1/messages").mock(
        return_value=_ok({"data": {"id": "m1"}})
    )
    feedback = respx.post(f"{BASE}/api/v1/chat/sessions/s1/feedback").mock(
        return_value=_ok({"data": {"submitted": True}})
    )
    with _client() as c:
        assert len(c.chat.list_sessions().data) == 1
        assert c.chat.get_session("s1").id == "s1"
        c.chat.create_session(agent_id="a1")
        c.chat.send_message("s1", content="hi")
        result = c.chat.submit_feedback("s1", execution_id="exec1", value=1)
        assert result.submitted is True
        c.chat.delete_session("s1")
    assert msg.called
    assert feedback.calls.last.request.content == b'{"execution_id":"exec1","value":1}'


# --------------------------- Agent Triggers ---------------------------


@respx.mock
def test_agent_triggers_crud():
    respx.get(f"{BASE}/api/v1/triggers").mock(return_value=_page([{"id": "t1"}]))
    respx.get(f"{BASE}/api/v1/triggers/t1").mock(return_value=_ok({"data": {"id": "t1"}}))
    respx.post(f"{BASE}/api/v1/triggers").mock(return_value=_ok({"data": {"id": "t1"}}))
    respx.patch(f"{BASE}/api/v1/triggers/t1").mock(return_value=_ok({"data": {"id": "t1"}}))
    respx.delete(f"{BASE}/api/v1/triggers/t1").mock(return_value=_ok({}))
    with _client() as c:
        assert len(c.agent_triggers.list().data) == 1
        assert c.agent_triggers.get("t1").id == "t1"
        c.agent_triggers.create(name="t", agent_id="a1")
        c.agent_triggers.update("t1", name="x")
        c.agent_triggers.delete("t1")


# --------------- Traces / Execution approvals / LLM models ---------------


@respx.mock
def test_traces():
    respx.get(f"{BASE}/api/v1/traces").mock(return_value=_page([{"id": "tr1"}]))
    respx.get(f"{BASE}/api/v1/traces/trace-abc").mock(
        return_value=_ok({"data": [{"id": "s1", "trace_id": "trace-abc"}]})
    )
    with _client() as c:
        assert len(c.traces.list().data) == 1
        spans = c.traces.get_by_trace_id("trace-abc")
    assert spans[0].trace_id == "trace-abc"


@respx.mock
def test_execution_approvals():
    respx.get(f"{BASE}/api/v1/executions/approval-inbox").mock(
        return_value=_page([{"id": "e1", "status": "waiting_approval"}])
    )
    approve = respx.post(f"{BASE}/api/v1/executions/e1/approve").mock(
        return_value=_ok({"data": {"id": "e1", "status": "running"}})
    )
    deny = respx.post(f"{BASE}/api/v1/executions/e1/deny").mock(
        return_value=_ok({"data": {"id": "e1", "status": "rejected"}})
    )
    cancel = respx.post(f"{BASE}/api/v1/executions/e1/cancel").mock(
        return_value=_ok({"data": {"id": "e1", "status": "cancel_requested"}})
    )
    with _client() as c:
        inbox = c.executions.approval_inbox()
        assert inbox.data[0].status == "waiting_approval"
        assert c.executions.approve("e1").status == "running"
        assert c.executions.deny("e1", reason="nope").status == "rejected"
        assert c.executions.cancel("e1").status == "cancel_requested"
    assert approve.called and deny.called and cancel.called
    assert b'"reason"' in deny.calls.last.request.read()


@respx.mock
def test_execution_tree():
    respx.get(f"{BASE}/api/v1/executions/e1/tree").mock(
        return_value=_ok(
            {
                "data": {
                    "id": "e1",
                    "status": "completed",
                    "children": [{"id": "e2", "parent_execution_id": "e1"}],
                }
            }
        )
    )
    with _client() as c:
        root = c.executions.tree("e1")
    assert root.id == "e1"
    assert len(root.children) == 1
    assert root.children[0].parent_execution_id == "e1"


@respx.mock
def test_llm_models():
    respx.get(f"{BASE}/api/v1/llm-models").mock(return_value=_page([{"id": "gpt-4o"}]))
    respx.get(f"{BASE}/api/v1/llm-models/available").mock(
        return_value=_ok({"data": {"groups": []}})
    )
    with _client() as c:
        assert len(c.llm_models.list().data) == 1
        c.llm_models.list_available()
