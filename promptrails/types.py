from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _from_dict(cls, data: Dict[str, Any]):
    """Create a dataclass instance from a dict, ignoring unknown keys."""
    if data is None:
        return None
    known = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in known})


def _strip_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


# --- Agent ---


@dataclass
class AgentVersion:
    id: str = ""
    agent_id: str = ""
    version: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    is_current: bool = False
    message: str = ""
    # Version-scoped model/runtime ownership (API v2).
    model_config: Optional[Dict[str, Any]] = None
    run_budget: Optional[Dict[str, Any]] = None
    approval_policy: Optional[Dict[str, Any]] = None
    cache_timeout: Optional[int] = None
    vfs_enabled: Optional[bool] = None
    masking_enabled: Optional[bool] = None
    tools: List[Dict[str, Any]] = field(default_factory=list)
    sub_agents: List[Dict[str, Any]] = field(default_factory=list)
    guardrails: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVersion":
        return _from_dict(cls, data)


@dataclass
class Agent:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    description: str = ""
    type: str = ""
    status: str = "draft"
    labels: List[str] = field(default_factory=list)
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    current_version: Optional[AgentVersion] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        obj = _from_dict(cls, data)
        if data.get("current_version"):
            obj.current_version = AgentVersion.from_dict(data["current_version"])
        return obj


# --- Prompt ---


@dataclass
class LLMModel:
    id: str = ""
    provider: str = ""
    model_id: str = ""
    display_name: str = ""
    input_price: Optional[float] = None
    output_price: Optional[float] = None
    cached_input_price: Optional[float] = None
    max_tokens: Optional[int] = None
    supports_vision: bool = False
    supports_tools: bool = False
    supports_json: bool = False
    supports_streaming: bool = False
    supports_temperature: bool = False
    supports_top_p: bool = False
    supports_top_k: bool = False
    supports_reasoning: bool = False
    supports_web_search: bool = False
    supports_prompt_caching: bool = False
    is_active: bool = True
    is_deprecated: bool = False
    deprecated_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMModel":
        return _from_dict(cls, data)


@dataclass
class AvailableModelEntry:
    id: str = ""
    model_id: str = ""
    display_name: str = ""
    max_tokens: Optional[int] = None
    supports_vision: bool = False
    supports_tools: bool = False
    supports_json: bool = False
    supports_temperature: bool = False
    supports_top_p: bool = False
    supports_top_k: bool = False
    supports_reasoning: bool = False
    supports_web_search: bool = False
    supports_prompt_caching: bool = False
    input_price: Optional[float] = None
    output_price: Optional[float] = None
    is_deprecated: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AvailableModelEntry":
        return _from_dict(cls, data)


@dataclass
class AvailableModelGroup:
    provider: str = ""
    models: List[AvailableModelEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AvailableModelGroup":
        obj = _from_dict(cls, data)
        if data.get("models"):
            obj.models = [AvailableModelEntry.from_dict(m) for m in data["models"]]
        return obj


@dataclass
class PromptVersion:
    """A content-only prompt version (API v2).

    Model, sampling, tools, output schema and cache TTL live on the agent
    version, not on the prompt — a prompt carries no model configuration.
    """

    id: str = ""
    prompt_id: str = ""
    version: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    is_current: bool = False
    config: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVersion":
        return _from_dict(cls, data)


@dataclass
class Prompt:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    current_version: Optional[PromptVersion] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prompt":
        obj = _from_dict(cls, data)
        if data.get("current_version"):
            obj.current_version = PromptVersion.from_dict(data["current_version"])
        return obj


# --- Execution ---


@dataclass
class AgentExecution:
    """An execution node.

    API v2 executions form a tree: a sub-agent delegation, handoff continuation
    or workflow agent-node run has ``parent_execution_id`` set and appears in its
    parent's ``children``. Root executions have ``parent_execution_id`` ``None``.
    ``status`` gains ``waiting_approval`` (parked at an approval-gated tool call)
    and ``cancel_requested`` (cooperative cancel observed before finalizing).
    """

    id: str = ""
    agent_id: str = ""
    agent_version_id: str = ""
    workspace_id: str = ""
    user_id: str = ""
    session_id: str = ""
    parent_execution_id: Optional[str] = None
    status: str = ""
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_usage: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    duration_ms: Optional[int] = None
    trace_id: Optional[str] = None
    approval_expires_at: Optional[str] = None
    children: List["AgentExecution"] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentExecution":
        obj = _from_dict(cls, data)
        if data.get("children"):
            obj.children = [cls.from_dict(c) for c in data["children"]]
        return obj


# --- Credential ---


@dataclass
class Credential:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    type: str = ""
    category: str = ""
    description: str = ""
    masked_content: str = ""
    is_default: bool = False
    schema_type: str = ""
    is_valid: bool = True
    has_schema: bool = False
    schema_updated_at: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credential":
        return _from_dict(cls, data)


# --- DataSource ---


@dataclass
class DataSourceVersion:
    id: str = ""
    data_source_id: str = ""
    version: str = ""
    credential_id: Optional[str] = None
    connection_config: Dict[str, Any] = field(default_factory=dict)
    query_template: str = ""
    parameters: List[Any] = field(default_factory=list)
    is_current: bool = False
    message: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSourceVersion":
        return _from_dict(cls, data)


@dataclass
class DataSource:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    type: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSource":
        return _from_dict(cls, data)


# --- Chat ---


@dataclass
class ChatMessage:
    id: str = ""
    session_id: str = ""
    role: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: Optional[Dict[str, Any]] = None
    tool_results: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    cost: Optional[float] = None
    token_count: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return _from_dict(cls, data)


@dataclass
class ChatSession:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    user_id: str = ""
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        return _from_dict(cls, data)


# --- Trace ---


@dataclass
class Trace:
    """An observability span (API v2).

    ``token_usage`` carries raw provider counts and, when reported, extends
    beyond prompt/completion/total with ``cached_tokens`` (prompt-cache read
    hits), ``cache_creation_tokens`` and ``reasoning_tokens``.
    """

    id: str = ""
    workspace_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str = ""
    name: str = ""
    kind: str = ""
    status: str = "ok"
    level: str = "default"
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    token_usage: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    duration_ms: Optional[int] = None
    completion_start_time: Optional[str] = None
    error_message: str = ""
    error_type: str = ""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    model_name: str = ""
    agent_id: Optional[str] = None
    agent_name: str = ""
    agent_type: str = ""
    user_id: Optional[str] = None
    session_id: str = ""
    execution_id: Optional[str] = None
    data_source_id: Optional[str] = None
    data_source_name: str = ""
    prompt_name: str = ""
    mcp_tool_name: str = ""
    mcp_tool_type: str = ""
    service_name: str = ""
    started_at: str = ""
    ended_at: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trace":
        return _from_dict(cls, data)


@dataclass
class TraceSummary:
    """Aggregate statistics over a filtered set of traces (``/traces/summary``)."""

    total_traces: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_duration_ms: float = 0.0
    error_count: int = 0
    unique_models: int = 0
    unique_sessions: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TraceSummary":
        return _from_dict(cls, data)


# --- MCP Tool ---


@dataclass
class MCPTool:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    type: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Dict[str, Any]] = None
    is_active: bool = True
    credential_id: Optional[str] = None
    template_id: Optional[str] = None
    status: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPTool":
        return _from_dict(cls, data)


@dataclass
class MCPDiscoveredTool:
    name: str = ""
    description: str = ""
    input_schema: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPDiscoveredTool":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            input_schema=data.get("inputSchema"),
        )


@dataclass
class MCPToolCallContent:
    type: str = ""
    text: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPToolCallContent":
        return cls(type=data.get("type", ""), text=data.get("text", ""))


@dataclass
class MCPDiscoverResult:
    tools: List["MCPDiscoveredTool"] = field(default_factory=list)
    trace_id: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPDiscoverResult":
        tools = [MCPDiscoveredTool.from_dict(t) for t in data.get("tools", [])]
        return cls(tools=tools, trace_id=data.get("trace_id", ""))


@dataclass
class MCPCallToolResult:
    content: List["MCPToolCallContent"] = field(default_factory=list)
    is_error: bool = False
    trace_id: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPCallToolResult":
        content = [MCPToolCallContent.from_dict(c) for c in data.get("content", [])]
        return cls(
            content=content,
            is_error=data.get("is_error", False),
            trace_id=data.get("trace_id", ""),
        )


# --- MCP Template ---


@dataclass
class MCPTemplateParameterSpec:
    name: str = ""
    type: str = ""
    required: bool = False
    secret: bool = False
    description: str = ""
    default: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPTemplateParameterSpec":
        return _from_dict(cls, data)


@dataclass
class MCPTemplate:
    id: str = ""
    slug: str = ""
    name: str = ""
    description: str = ""
    type: str = ""
    category: str = ""
    icon_url: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    required_parameters: List[MCPTemplateParameterSpec] = field(default_factory=list)
    documentation_url: str = ""
    setup_instructions: str = ""
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPTemplate":
        obj = _from_dict(cls, data)
        if data.get("required_parameters"):
            obj.required_parameters = [
                MCPTemplateParameterSpec.from_dict(p) for p in data["required_parameters"]
            ]
        return obj


@dataclass
class InstallMCPTemplateRequest:
    name: str = ""
    parameters: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallMCPTemplateRequest":
        return _from_dict(cls, data)


# --- Guardrail ---


@dataclass
class Guardrail:
    id: str = ""
    agent_id: str = ""
    type: str = ""
    scanner_type: str = ""
    action: str = "block"
    config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Guardrail":
        return _from_dict(cls, data)


@dataclass
class GuardrailSpec:
    """A guardrail attachment spec — the input shape used to create/attach a
    guardrail on an agent or agent version.

    ``id`` is present on responses only; omit it on create.
    """

    type: str  # "input" | "output"
    scanner_type: str
    action: str = "block"
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    sort_order: Optional[int] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none(
            {
                "id": self.id,
                "type": self.type,
                "scanner_type": self.scanner_type,
                "action": self.action,
                "config": self.config,
                "is_active": self.is_active,
                "sort_order": self.sort_order,
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuardrailSpec":
        return _from_dict(cls, data)


@dataclass
class ScannerMeta:
    """Metadata for an available guardrail scanner (``/guardrails/scanners``)."""

    type: str = ""
    label: str = ""
    description: str = ""
    category: str = ""  # "local" | "llm_guard"
    enabled: bool = True
    config_fields: List[str] = field(default_factory=list)
    disabled_reason: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScannerMeta":
        return _from_dict(cls, data)


# --- Version-scoped runtime config (inputs to agents.create_version) ---


@dataclass
class ModelConfig:
    """Version-scoped model + sampling ownership. Every field is optional;
    unset sampling inherits the provider/model default."""

    model_id: Optional[str] = None
    fallback_model_id: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none(
            {
                "model_id": self.model_id,
                "fallback_model_id": self.fallback_model_id,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "max_tokens": self.max_tokens,
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        return _from_dict(cls, data)


@dataclass
class RunBudget:
    """Bounds the whole execution tree, enforced at the root. Every field is
    optional."""

    max_cost: Optional[float] = None
    max_total_tokens: Optional[int] = None
    max_tool_calls: Optional[int] = None
    max_children: Optional[int] = None
    max_depth: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none(
            {
                "max_cost": self.max_cost,
                "max_total_tokens": self.max_total_tokens,
                "max_tool_calls": self.max_tool_calls,
                "max_children": self.max_children,
                "max_depth": self.max_depth,
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunBudget":
        return _from_dict(cls, data)


@dataclass
class ApprovalPolicy:
    """Who may approve/deny a parked, approval-gated call."""

    mode: Optional[str] = None  # "admins" (default) | "assigned" | "any_member"
    member_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none({"mode": self.mode, "member_ids": self.member_ids})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalPolicy":
        return _from_dict(cls, data)


# --- Execution Result ---


@dataclass
class ExecutionResult:
    output: Optional[Dict[str, Any]] = None
    error: str = ""
    trace_id: str = ""
    execution_id: str = ""
    status: str = ""
    token_usage: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    duration_ms: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        return _from_dict(cls, data)


# --- A2A (Agent-to-Agent) ---


@dataclass
class A2APart:
    type: str = ""
    text: str = ""
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2APart":
        return _from_dict(cls, data)


@dataclass
class A2AMessage:
    role: str = ""
    parts: List[A2APart] = field(default_factory=list)
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        obj = _from_dict(cls, data)
        if data.get("parts"):
            obj.parts = [A2APart.from_dict(p) for p in data["parts"]]
        return obj


@dataclass
class A2AArtifact:
    id: str = ""
    parts: List[A2APart] = field(default_factory=list)
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AArtifact":
        obj = _from_dict(cls, data)
        if data.get("parts"):
            obj.parts = [A2APart.from_dict(p) for p in data["parts"]]
        return obj


@dataclass
class A2ATaskStatus:
    state: str = ""
    message: str = ""
    timestamp: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2ATaskStatus":
        return _from_dict(cls, data)


@dataclass
class A2ATask:
    id: str = ""
    context_id: str = ""
    status: Optional[A2ATaskStatus] = None
    messages: List[A2AMessage] = field(default_factory=list)
    artifacts: List[A2AArtifact] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2ATask":
        obj = _from_dict(cls, data)
        if data.get("status") and isinstance(data["status"], dict):
            obj.status = A2ATaskStatus.from_dict(data["status"])
        if data.get("messages"):
            obj.messages = [A2AMessage.from_dict(m) for m in data["messages"]]
        if data.get("artifacts"):
            obj.artifacts = [A2AArtifact.from_dict(a) for a in data["artifacts"]]
        return obj


@dataclass
class A2AAgentSkill:
    id: str = ""
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AAgentSkill":
        return _from_dict(cls, data)


@dataclass
class AgentTrigger:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    name: str = ""
    token: str = ""
    token_prefix: str = ""
    source: str = "generic"
    source_config: Dict[str, Any] = field(default_factory=dict)
    reply_config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    has_secret: bool = False
    last_used_at: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTrigger":
        return _from_dict(cls, data)


@dataclass
class AgentTriggerCreateResponse:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    name: str = ""
    token: str = ""
    token_prefix: str = ""
    source: str = "generic"
    source_config: Dict[str, Any] = field(default_factory=dict)
    reply_config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    has_secret: bool = False
    last_used_at: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    secret: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTriggerCreateResponse":
        return _from_dict(cls, data)


@dataclass
class AgentVFSFile:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    path: str = ""
    parent_path: str = ""
    name: str = ""
    is_dir: bool = False
    content: str = ""
    size_bytes: int = 0
    mime_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_writer_kind: str = "user"
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVFSFile":
        return _from_dict(cls, data)


@dataclass
class AgentVFSGrepMatch:
    path: str = ""
    line_number: int = 0
    line: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVFSGrepMatch":
        return _from_dict(cls, data)


# --- Asset ---


@dataclass
class Asset:
    id: str = ""
    workspace_id: str = ""
    type: str = ""
    provider: str = ""
    model: str = ""
    file_name: str = ""
    file_size: Optional[int] = None
    mime_type: str = ""
    storage_path: str = ""
    execution_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        return _from_dict(cls, data)


@dataclass
class AssetSignedURL:
    url: str = ""
    expires_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetSignedURL":
        return _from_dict(cls, data)


@dataclass
class A2AAgentCapabilities:
    streaming: bool = False
    push_notifications: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AAgentCapabilities":
        return _from_dict(cls, data)


@dataclass
class A2AAgentCard:
    name: str = ""
    description: str = ""
    url: str = ""
    version: str = ""
    capabilities: Optional[A2AAgentCapabilities] = None
    skills: List[A2AAgentSkill] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AAgentCard":
        obj = _from_dict(cls, data)
        if data.get("capabilities"):
            obj.capabilities = A2AAgentCapabilities.from_dict(data["capabilities"])
        if data.get("skills"):
            obj.skills = [A2AAgentSkill.from_dict(s) for s in data["skills"]]
        return obj
