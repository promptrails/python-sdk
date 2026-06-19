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


# --------------------------- Costs ---------------------------


@respx.mock
def test_costs_summary():
    respx.get(f"{BASE}/api/v1/costs/summary").mock(
        return_value=_ok({"data": {"total_tokens": 100, "total_executions": 3}})
    )
    with _client() as c:
        summary = c.costs.get_summary()
    assert summary.total_tokens == 100
    assert summary.total_executions == 3


@respx.mock
def test_costs_agent_summary():
    route = respx.get(f"{BASE}/api/v1/costs/agents/ag1").mock(
        return_value=_ok({"data": {"total_tokens": 5}})
    )
    with _client() as c:
        summary = c.costs.get_agent_summary("ag1")
    assert route.called
    assert summary.total_tokens == 5


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


# --------------------------- Scores ---------------------------


@respx.mock
def test_scores_crud():
    respx.get(f"{BASE}/api/v1/scores").mock(return_value=_page([{"id": "s1"}]))
    respx.get(f"{BASE}/api/v1/scores/s1").mock(
        return_value=_ok({"data": {"id": "s1", "value": 0.9}})
    )
    respx.post(f"{BASE}/api/v1/scores").mock(return_value=_ok({"data": {"id": "s1"}}))
    respx.patch(f"{BASE}/api/v1/scores/s1").mock(
        return_value=_ok({"data": {"id": "s1", "value": 0.5}})
    )
    respx.delete(f"{BASE}/api/v1/scores/s1").mock(return_value=_ok({}))

    with _client() as c:
        assert len(c.scores.list().data) == 1
        assert c.scores.get("s1").value == 0.9
        created = c.scores.create(trace_id="tr1", name="acc", value=1.0)
        assert created.id == "s1"
        updated = c.scores.update("s1", value=0.5)
        assert updated.value == 0.5
        c.scores.delete("s1")


@respx.mock
def test_scores_aggregates():
    respx.get(f"{BASE}/api/v1/scores/aggregates").mock(
        return_value=_ok({"data": [{"name": "acc", "count": 3}]})
    )
    with _client() as c:
        aggs = c.scores.get_aggregates()
    assert len(aggs) == 1
    assert aggs[0].count == 3


@respx.mock
def test_score_configs():
    respx.get(f"{BASE}/api/v1/score-configs").mock(return_value=_page([{"id": "cfg1"}]))
    respx.get(f"{BASE}/api/v1/score-configs/cfg1").mock(return_value=_ok({"data": {"id": "cfg1"}}))
    respx.post(f"{BASE}/api/v1/score-configs").mock(return_value=_ok({"data": {"id": "cfg1"}}))
    respx.delete(f"{BASE}/api/v1/score-configs/cfg1").mock(return_value=_ok({}))

    with _client() as c:
        assert len(c.scores.list_configs().data) == 1
        assert c.scores.get_config("cfg1").id == "cfg1"
        created = c.scores.create_config(name="acc", data_type="numeric")
        assert created.id == "cfg1"
        c.scores.delete_config("cfg1")
