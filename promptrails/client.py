from __future__ import annotations

from ._http import HTTPClient
from .config import Config
from .resources import (
    A2AResource,
    AgentsResource,
    AgentTriggersResource,
    AgentVFSResource,
    ApprovalsResource,
    AssetsResource,
    ChatResource,
    CostsResource,
    CredentialsResource,
    DashboardResource,
    DataSourcesResource,
    ExecutionsResource,
    GuardrailsResource,
    LLMModelsResource,
    MCPTemplatesResource,
    MCPToolsResource,
    MediaModelsResource,
    MediaResource,
    MemoriesResource,
    PromptsResource,
    ScoresResource,
    SessionsResource,
    TemplatesResource,
    TracesResource,
)


class PromptRails:
    """Synchronous PromptRails API client."""

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
        self._http = HTTPClient(self._config)

        self.agents = AgentsResource(self._http)
        self.prompts = PromptsResource(self._http)
        self.executions = ExecutionsResource(self._http)
        self.credentials = CredentialsResource(self._http)
        self.data_sources = DataSourcesResource(self._http)
        self.chat = ChatResource(self._http)
        self.memories = MemoriesResource(self._http)
        self.traces = TracesResource(self._http)
        self.costs = CostsResource(self._http)
        self.mcp_tools = MCPToolsResource(self._http)
        self.mcp_templates = MCPTemplatesResource(self._http)
        self.guardrails = GuardrailsResource(self._http)
        self.llm_models = LLMModelsResource(self._http)
        self.approvals = ApprovalsResource(self._http)
        self.templates = TemplatesResource(self._http)
        self.scores = ScoresResource(self._http)
        self.dashboard = DashboardResource(self._http)
        self.sessions = SessionsResource(self._http)
        self.a2a = A2AResource(self._http)
        self.agent_triggers = AgentTriggersResource(self._http)
        self.agent_vfs = AgentVFSResource(self._http)
        self.media_models = MediaModelsResource(self._http)
        self.media = MediaResource(self._http)
        self.assets = AssetsResource(self._http)

    def close(self):
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
