import pytest

from promptrails import AsyncPromptRails, PromptRails
from promptrails.config import Config
from promptrails.exceptions import (
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
    raise_for_status,
)


class TestConfig:
    def test_defaults(self):
        cfg = Config(api_key="key")
        assert cfg.base_url == "https://api.promptrails.ai"
        assert cfg.timeout == 30.0
        assert cfg.max_retries == 3

    def test_trailing_slash_stripped(self):
        cfg = Config(api_key="key", base_url="http://localhost:8082/")
        assert cfg.base_url == "http://localhost:8082"

    def test_headers(self):
        cfg = Config(api_key="test-key")
        h = cfg.headers
        assert h["X-API-Key"] == "test-key"
        assert "X-Workspace-ID" not in h
        assert h["Content-Type"] == "application/json"


class TestClient:
    def test_creates_resources(self):
        client = PromptRails(api_key="k")
        assert client.agents is not None
        assert client.prompts is not None
        assert client.executions is not None
        assert client.credentials is not None
        assert client.data_sources is not None
        assert client.chat is not None
        assert client.traces is not None
        assert client.mcp_tools is not None
        assert client.guardrails is not None
        assert not hasattr(client, "costs")
        assert not hasattr(client, "scores")
        assert not hasattr(client, "approvals")
        client.close()

    def test_context_manager(self):
        with PromptRails(api_key="k") as client:
            assert client.agents is not None


class TestAsyncClient:
    def test_creates_resources(self):
        client = AsyncPromptRails(api_key="k")
        assert client.agents is not None
        assert client.prompts is not None
        assert client.executions is not None


class TestExceptions:
    def test_raise_400(self):
        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(400, {"error": {"message": "bad input", "code": "VALIDATION"}})
        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "VALIDATION"

    def test_raise_401(self):
        with pytest.raises(UnauthorizedError):
            raise_for_status(401, {"error": "unauthorized"})

    def test_raise_404(self):
        with pytest.raises(NotFoundError):
            raise_for_status(404, {"error": {"message": "not found"}})

    def test_raise_429(self):
        with pytest.raises(RateLimitError):
            raise_for_status(429, {"error": {"message": "rate limited"}})

    def test_no_raise_on_200(self):
        raise_for_status(200, {"data": {}})
