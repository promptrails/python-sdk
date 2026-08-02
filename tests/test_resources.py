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


# --------------------------- A2A ---------------------------


@respx.mock
def test_a2a_agent_card():
    respx.get(f"{BASE}/a2a/agents/ag1/agent-card.json").mock(
        return_value=_ok({"name": "Card", "version": "1.0"})
    )
    with _client() as c:
        card = c.a2a.get_agent_card("ag1")
    assert card.name == "Card"


@respx.mock
def test_a2a_list_tasks():
    respx.get(f"{BASE}/api/v1/a2a/tasks").mock(return_value=_page([{"id": "t1"}]))
    with _client() as c:
        result = c.a2a.list_tasks()
    assert len(result.data) == 1
    assert result.data[0].id == "t1"


@respx.mock
def test_a2a_cancel_task():
    route = respx.post(f"{BASE}/a2a/tasks/cancel").mock(
        return_value=_ok({"result": {"id": "t1", "status": "canceled"}})
    )
    with _client() as c:
        task = c.a2a.cancel_task("t1")
    assert route.called
    assert task.status == "canceled"


# --------------------------- Credentials ---------------------------


@respx.mock
def test_credentials_crud():
    respx.get(f"{BASE}/api/v1/credentials").mock(return_value=_page([{"id": "c1"}]))
    respx.get(f"{BASE}/api/v1/credentials/c1").mock(
        return_value=_ok({"data": {"id": "c1", "provider": "openai"}})
    )
    create_route = respx.post(f"{BASE}/api/v1/credentials").mock(
        return_value=_ok({"data": {"id": "c1", "name": "key"}})
    )
    respx.delete(f"{BASE}/api/v1/credentials/c1").mock(return_value=_ok({}))
    default_route = respx.post(f"{BASE}/api/v1/credentials/c1/set-default").mock(
        return_value=_ok({"data": {"id": "c1"}})
    )

    with _client() as c:
        assert len(c.credentials.list().data) == 1
        assert c.credentials.get("c1").id == "c1"
        created = c.credentials.create(name="key", type="api_key", category="llm", value="sk")
        assert created.name == "key"
        c.credentials.delete("c1")
        c.credentials.set_default("c1")

    assert create_route.called
    assert default_route.called


@respx.mock
def test_credentials_check_connection():
    respx.post(f"{BASE}/api/v1/credentials/c1/check").mock(return_value=_ok({"data": {"ok": True}}))
    with _client() as c:
        result = c.credentials.check_connection("c1")
    assert result == {"ok": True}


# --------------------------- Assets ---------------------------


@respx.mock
def test_assets_list_with_filters():
    route = respx.get(f"{BASE}/api/v1/assets").mock(return_value=_page([{"id": "a1"}]))
    with _client() as c:
        result = c.assets.list(type="image", provider="openai")
    assert len(result.data) == 1
    request = route.calls.last.request
    assert request.url.params["type"] == "image"
    assert request.url.params["provider"] == "openai"


@respx.mock
def test_assets_get_and_signed_url():
    respx.get(f"{BASE}/api/v1/assets/a1").mock(
        return_value=_ok({"data": {"id": "a1", "file_name": "x.png"}})
    )
    respx.get(f"{BASE}/api/v1/assets/a1/signed-url").mock(
        return_value=_ok({"data": {"url": "https://signed"}})
    )
    with _client() as c:
        asset = c.assets.get("a1")
        signed = c.assets.get_signed_url("a1")
    assert asset.id == "a1"
    assert signed.url == "https://signed"


# --------------------------- Traces ---------------------------


@respx.mock
def test_traces_summary():
    route = respx.get(f"{BASE}/api/v1/traces/summary").mock(
        return_value=_ok({"data": {"total_traces": 12, "total_tokens": 3400, "error_count": 1}})
    )
    with _client() as c:
        summary = c.traces.get_summary(agent_id="ag1", date_from="2026-01-01")
    assert summary.total_traces == 12
    assert summary.total_tokens == 3400
    request = route.calls.last.request
    assert request.url.params["agent_id"] == "ag1"
    assert request.url.params["date_from"] == "2026-01-01"


@respx.mock
def test_traces_ingest():
    route = respx.post(f"{BASE}/api/v1/traces/ingest").mock(
        return_value=_ok({"data": {"ingested": 1}})
    )
    with _client() as c:
        result = c.traces.ingest(
            [{"trace_id": "t1", "span_id": "s1", "name": "run", "kind": "agent"}]
        )
    assert result == {"ingested": 1}
    assert b'"spans"' in route.calls.last.request.read()


# --------------------------- Guardrails ---------------------------


@respx.mock
def test_guardrails_scanners_and_update():
    respx.get(f"{BASE}/api/v1/guardrails/scanners").mock(
        return_value=_ok({"data": [{"type": "pii", "label": "PII", "category": "local"}]})
    )
    respx.patch(f"{BASE}/api/v1/guardrails/g1").mock(
        return_value=_ok({"data": {"id": "g1", "action": "log"}})
    )
    respx.delete(f"{BASE}/api/v1/guardrails/g1").mock(return_value=_ok({}))
    with _client() as c:
        scanners = c.guardrails.list_scanners()
        updated = c.guardrails.update("g1", action="log")
        c.guardrails.delete("g1")
    assert scanners[0].type == "pii"
    assert updated.action == "log"
