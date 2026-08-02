from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..agent_config import AgentConfig, SubAgentAttachment, ToolAttachment
from ..pagination import PaginatedResponse
from ..types import (
    Agent,
    AgentVersion,
    ApprovalPolicy,
    ExecutionResult,
    Guardrail,
    GuardrailSpec,
    ModelConfig,
    RunBudget,
)
from .base import AsyncBaseResource, BaseResource


def _payload(value: Any) -> Any:
    """Serialize a typed helper (``ModelConfig``, ``GuardrailSpec``, ...) or pass
    a plain dict through unchanged."""
    return value.to_dict() if hasattr(value, "to_dict") else value


def _build_version_payload(
    *,
    version: str,
    config: AgentConfig,
    input_schema: Optional[Dict[str, Any]],
    output_schema: Optional[Dict[str, Any]],
    set_current: bool,
    message: Optional[str],
    model_config: Optional[Any],
    run_budget: Optional[Any],
    approval_policy: Optional[Any],
    cache_timeout: Optional[int],
    vfs_enabled: Optional[bool],
    masking_enabled: Optional[bool],
    tools: Optional[List[Any]],
    sub_agents: Optional[List[Any]],
    guardrails: Optional[List[Any]],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": version,
        "set_current": set_current,
        "config": config.to_dict(),
    }
    if input_schema is not None:
        payload["input_schema"] = input_schema
    if output_schema is not None:
        payload["output_schema"] = output_schema
    if message is not None:
        payload["message"] = message
    if model_config is not None:
        payload["model_config"] = _payload(model_config)
    if run_budget is not None:
        payload["run_budget"] = _payload(run_budget)
    if approval_policy is not None:
        payload["approval_policy"] = _payload(approval_policy)
    if cache_timeout is not None:
        payload["cache_timeout"] = cache_timeout
    if vfs_enabled is not None:
        payload["vfs_enabled"] = vfs_enabled
    if masking_enabled is not None:
        payload["masking_enabled"] = masking_enabled
    if tools is not None:
        payload["tools"] = [_payload(t) for t in tools]
    if sub_agents is not None:
        payload["sub_agents"] = [_payload(s) for s in sub_agents]
    if guardrails is not None:
        payload["guardrails"] = [_payload(g) for g in guardrails]
    return payload


class AgentsResource(BaseResource):
    def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        type: Optional[str] = None,
        name: Optional[str] = None,
    ) -> PaginatedResponse[Agent]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        body = self._http.get("/api/v1/agents", params=params)
        return PaginatedResponse.from_response(body, Agent.from_dict)

    def get(self, agent_id: str) -> Agent:
        body = self._http.get(f"/api/v1/agents/{agent_id}")
        return Agent.from_dict(self._unwrap(body))

    def create(
        self,
        *,
        name: str,
        type: str,
        description: str = "",
        template_id: Optional[str] = None,
    ) -> Agent:
        """Create an agent. ``type`` is ``agent`` or ``workflow``."""
        payload: Dict[str, Any] = {"name": name, "type": type, "description": description}
        if template_id is not None:
            payload["template_id"] = template_id
        body = self._http.post("/api/v1/agents", json=payload)
        return Agent.from_dict(self._unwrap(body))

    def update(self, agent_id: str, **kwargs) -> Agent:
        body = self._http.patch(f"/api/v1/agents/{agent_id}", json=kwargs)
        return Agent.from_dict(self._unwrap(body))

    def delete(self, agent_id: str) -> None:
        self._http.delete(f"/api/v1/agents/{agent_id}")

    def execute(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        session_id: Optional[str] = None,
        version_id: Optional[str] = None,
        sync: Optional[bool] = None,
    ) -> ExecutionResult:
        payload: Dict[str, Any] = {"input": input}
        if session_id:
            payload["session_id"] = session_id
        if version_id is not None:
            payload["version_id"] = version_id
        if sync is not None:
            payload["sync"] = sync
        body = self._http.post(f"/api/v1/agents/{agent_id}/execute", json=payload)
        return ExecutionResult.from_dict(self._unwrap(body))

    def list_versions(self, agent_id: str) -> List[AgentVersion]:
        body = self._http.get(f"/api/v1/agents/{agent_id}/versions")
        data = self._unwrap(body)
        return [AgentVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    def create_version(
        self,
        agent_id: str,
        *,
        version: str,
        config: AgentConfig,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
        model_config: Optional[ModelConfig] = None,
        run_budget: Optional[RunBudget] = None,
        approval_policy: Optional[ApprovalPolicy] = None,
        cache_timeout: Optional[int] = None,
        vfs_enabled: Optional[bool] = None,
        masking_enabled: Optional[bool] = None,
        tools: Optional[List[ToolAttachment]] = None,
        sub_agents: Optional[List[SubAgentAttachment]] = None,
        guardrails: Optional[List[GuardrailSpec]] = None,
    ) -> AgentVersion:
        """Create an agent version.

        The version owns the model + sampling (``model_config``), the
        execution-tree budget (``run_budget``), the approval policy, cache TTL,
        version-scoped VFS/masking overrides, and the attached ``tools`` /
        ``sub_agents`` / ``guardrails``.
        """
        payload = _build_version_payload(
            version=version,
            config=config,
            input_schema=input_schema,
            output_schema=output_schema,
            set_current=set_current,
            message=message,
            model_config=model_config,
            run_budget=run_budget,
            approval_policy=approval_policy,
            cache_timeout=cache_timeout,
            vfs_enabled=vfs_enabled,
            masking_enabled=masking_enabled,
            tools=tools,
            sub_agents=sub_agents,
            guardrails=guardrails,
        )
        body = self._http.post(f"/api/v1/agents/{agent_id}/versions", json=payload)
        return AgentVersion.from_dict(self._unwrap(body))

    def promote_version(self, agent_id: str, version_id: str) -> Dict[str, Any]:
        body = self._http.put(f"/api/v1/agents/{agent_id}/versions/{version_id}/promote", json={})
        return self._unwrap(body)

    def preview(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = self._http.post(f"/api/v1/agents/{agent_id}/preview", json=payload)
        return self._unwrap(body)

    def playground(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        prompt_override: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the agent with an ad-hoc prompt override without saving a version.

        ``prompt_override`` may carry ``system_prompt``, ``user_prompt`` and
        ``input_schema``. ``version_id`` selects whose runtime behavior is used
        (defaults to the current version).
        """
        payload: Dict[str, Any] = {"input": input, "prompt_override": prompt_override}
        if version_id is not None:
            payload["version_id"] = version_id
        body = self._http.post(f"/api/v1/agents/{agent_id}/playground", json=payload)
        return self._unwrap(body)

    def list_guardrails(self, agent_id: str) -> List[Guardrail]:
        body = self._http.get(f"/api/v1/agents/{agent_id}/guardrails")
        data = self._unwrap(body)
        return [Guardrail.from_dict(g) for g in (data if isinstance(data, list) else [])]

    def create_guardrail(
        self,
        agent_id: str,
        *,
        type: str,
        scanner_type: str,
        action: str = "block",
        config: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        sort_order: Optional[int] = None,
    ) -> Guardrail:
        payload: Dict[str, Any] = {"type": type, "scanner_type": scanner_type, "action": action}
        if config is not None:
            payload["config"] = config
        if is_active is not None:
            payload["is_active"] = is_active
        if sort_order is not None:
            payload["sort_order"] = sort_order
        body = self._http.post(f"/api/v1/agents/{agent_id}/guardrails", json=payload)
        return Guardrail.from_dict(self._unwrap(body))


class AsyncAgentsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        type: Optional[str] = None,
        name: Optional[str] = None,
    ) -> PaginatedResponse[Agent]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        body = await self._http.get("/api/v1/agents", params=params)
        return PaginatedResponse.from_response(body, Agent.from_dict)

    async def get(self, agent_id: str) -> Agent:
        body = await self._http.get(f"/api/v1/agents/{agent_id}")
        return Agent.from_dict(self._unwrap(body))

    async def create(
        self,
        *,
        name: str,
        type: str,
        description: str = "",
        template_id: Optional[str] = None,
    ) -> Agent:
        """Create an agent. ``type`` is ``agent`` or ``workflow``."""
        payload: Dict[str, Any] = {"name": name, "type": type, "description": description}
        if template_id is not None:
            payload["template_id"] = template_id
        body = await self._http.post("/api/v1/agents", json=payload)
        return Agent.from_dict(self._unwrap(body))

    async def update(self, agent_id: str, **kwargs) -> Agent:
        body = await self._http.patch(f"/api/v1/agents/{agent_id}", json=kwargs)
        return Agent.from_dict(self._unwrap(body))

    async def delete(self, agent_id: str) -> None:
        await self._http.delete(f"/api/v1/agents/{agent_id}")

    async def execute(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        session_id: Optional[str] = None,
        version_id: Optional[str] = None,
        sync: Optional[bool] = None,
    ) -> ExecutionResult:
        payload: Dict[str, Any] = {"input": input}
        if session_id:
            payload["session_id"] = session_id
        if version_id is not None:
            payload["version_id"] = version_id
        if sync is not None:
            payload["sync"] = sync
        body = await self._http.post(f"/api/v1/agents/{agent_id}/execute", json=payload)
        return ExecutionResult.from_dict(self._unwrap(body))

    async def list_versions(self, agent_id: str) -> List[AgentVersion]:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/versions")
        data = self._unwrap(body)
        return [AgentVersion.from_dict(v) for v in (data if isinstance(data, list) else [])]

    async def create_version(
        self,
        agent_id: str,
        *,
        version: str,
        config: AgentConfig,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        set_current: bool = False,
        message: Optional[str] = None,
        model_config: Optional[ModelConfig] = None,
        run_budget: Optional[RunBudget] = None,
        approval_policy: Optional[ApprovalPolicy] = None,
        cache_timeout: Optional[int] = None,
        vfs_enabled: Optional[bool] = None,
        masking_enabled: Optional[bool] = None,
        tools: Optional[List[ToolAttachment]] = None,
        sub_agents: Optional[List[SubAgentAttachment]] = None,
        guardrails: Optional[List[GuardrailSpec]] = None,
    ) -> AgentVersion:
        """Async variant of :meth:`AgentsResource.create_version`."""
        payload = _build_version_payload(
            version=version,
            config=config,
            input_schema=input_schema,
            output_schema=output_schema,
            set_current=set_current,
            message=message,
            model_config=model_config,
            run_budget=run_budget,
            approval_policy=approval_policy,
            cache_timeout=cache_timeout,
            vfs_enabled=vfs_enabled,
            masking_enabled=masking_enabled,
            tools=tools,
            sub_agents=sub_agents,
            guardrails=guardrails,
        )
        body = await self._http.post(f"/api/v1/agents/{agent_id}/versions", json=payload)
        return AgentVersion.from_dict(self._unwrap(body))

    async def promote_version(self, agent_id: str, version_id: str) -> Dict[str, Any]:
        body = await self._http.put(
            f"/api/v1/agents/{agent_id}/versions/{version_id}/promote", json={}
        )
        return self._unwrap(body)

    async def preview(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"input": input}
        if version_id is not None:
            payload["version_id"] = version_id
        body = await self._http.post(f"/api/v1/agents/{agent_id}/preview", json=payload)
        return self._unwrap(body)

    async def playground(
        self,
        agent_id: str,
        *,
        input: Dict[str, Any],
        prompt_override: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async variant of :meth:`AgentsResource.playground`."""
        payload: Dict[str, Any] = {"input": input, "prompt_override": prompt_override}
        if version_id is not None:
            payload["version_id"] = version_id
        body = await self._http.post(f"/api/v1/agents/{agent_id}/playground", json=payload)
        return self._unwrap(body)

    async def list_guardrails(self, agent_id: str) -> List[Guardrail]:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/guardrails")
        data = self._unwrap(body)
        return [Guardrail.from_dict(g) for g in (data if isinstance(data, list) else [])]

    async def create_guardrail(
        self,
        agent_id: str,
        *,
        type: str,
        scanner_type: str,
        action: str = "block",
        config: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        sort_order: Optional[int] = None,
    ) -> Guardrail:
        payload: Dict[str, Any] = {"type": type, "scanner_type": scanner_type, "action": action}
        if config is not None:
            payload["config"] = config
        if is_active is not None:
            payload["is_active"] = is_active
        if sort_order is not None:
            payload["sort_order"] = sort_order
        body = await self._http.post(f"/api/v1/agents/{agent_id}/guardrails", json=payload)
        return Guardrail.from_dict(self._unwrap(body))
