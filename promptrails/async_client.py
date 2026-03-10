from __future__ import annotations

from ._async_http import AsyncHTTPClient
from .config import Config
from .resources import (
    AsyncA2AResource,
    AsyncAgentsResource,
    AsyncApprovalsResource,
    AsyncChatResource,
    AsyncCostsResource,
    AsyncCredentialsResource,
    AsyncDashboardResource,
    AsyncDataSourcesResource,
    AsyncExecutionsResource,
    AsyncGuardrailsResource,
    AsyncLLMModelsResource,
    AsyncMCPTemplatesResource,
    AsyncMCPToolsResource,
    AsyncMemoriesResource,
    AsyncPromptsResource,
    AsyncScoresResource,
    AsyncSessionsResource,
    AsyncTemplatesResource,
    AsyncTracesResource,
    AsyncWebhookTriggersResource,
)


class AsyncPromptRails:
    """Async PromptRails API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.promptrails.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self._config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._http = AsyncHTTPClient(self._config)

        self.agents = AsyncAgentsResource(self._http)
        self.prompts = AsyncPromptsResource(self._http)
        self.executions = AsyncExecutionsResource(self._http)
        self.credentials = AsyncCredentialsResource(self._http)
        self.data_sources = AsyncDataSourcesResource(self._http)
        self.chat = AsyncChatResource(self._http)
        self.memories = AsyncMemoriesResource(self._http)
        self.traces = AsyncTracesResource(self._http)
        self.costs = AsyncCostsResource(self._http)
        self.mcp_tools = AsyncMCPToolsResource(self._http)
        self.mcp_templates = AsyncMCPTemplatesResource(self._http)
        self.guardrails = AsyncGuardrailsResource(self._http)
        self.llm_models = AsyncLLMModelsResource(self._http)
        self.approvals = AsyncApprovalsResource(self._http)
        self.templates = AsyncTemplatesResource(self._http)
        self.scores = AsyncScoresResource(self._http)
        self.dashboard = AsyncDashboardResource(self._http)
        self.sessions = AsyncSessionsResource(self._http)
        self.a2a = AsyncA2AResource(self._http)
        self.webhook_triggers = AsyncWebhookTriggersResource(self._http)

    async def close(self):
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
