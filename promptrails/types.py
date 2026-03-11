from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _from_dict(cls, data: Dict[str, Any]):
    """Create a dataclass instance from a dict, ignoring unknown keys."""
    if data is None:
        return None
    known = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in known})


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
    max_tokens: Optional[int] = None
    supports_vision: bool = False
    supports_tools: bool = False
    supports_json: bool = False
    supports_streaming: bool = False
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMModel":
        return _from_dict(cls, data)


@dataclass
class RunPromptResponse:
    content: str = ""
    token_usage: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    duration_ms: int = 0
    model: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunPromptResponse":
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
    input_price: Optional[float] = None
    output_price: Optional[float] = None

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
    id: str = ""
    prompt_id: str = ""
    version: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    llm_model_id: Optional[str] = None
    fallback_llm_model_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    is_current: bool = False
    config: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    created_at: str = ""
    llm_model: Optional[LLMModel] = None
    fallback_llm_model: Optional[LLMModel] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVersion":
        obj = _from_dict(cls, data)
        if data.get("llm_model"):
            obj.llm_model = LLMModel.from_dict(data["llm_model"])
        if data.get("fallback_llm_model"):
            obj.fallback_llm_model = LLMModel.from_dict(data["fallback_llm_model"])
        return obj


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
    id: str = ""
    agent_id: str = ""
    agent_version_id: str = ""
    workspace_id: str = ""
    user_id: str = ""
    session_id: str = ""
    status: str = ""
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_usage: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    duration_ms: Optional[int] = None
    trace_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentExecution":
        return _from_dict(cls, data)


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


# --- Memory ---


@dataclass
class AgentMemory:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    content: str = ""
    metadata: Optional[Dict[str, Any]] = None
    memory_type: str = ""
    importance: float = 0.5
    access_count: int = 0
    last_accessed_at: Optional[str] = None
    chat_session_id: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMemory":
        return _from_dict(cls, data)


# --- Trace ---


@dataclass
class Trace:
    id: str = ""
    workspace_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str = ""
    name: str = ""
    kind: str = ""
    status: str = "ok"
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    token_usage: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    duration_ms: Optional[int] = None
    error_message: str = ""
    error_type: str = ""
    error_stack: str = ""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    agent_id: Optional[str] = None
    prompt_id: Optional[str] = None
    llm_model_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: str = ""
    execution_id: Optional[str] = None
    service_name: str = ""
    started_at: str = ""
    ended_at: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trace":
        return _from_dict(cls, data)


# --- Cost ---


@dataclass
class CostSummary:
    total_cost: float = 0.0
    total_executions: int = 0
    total_tokens: int = 0
    daily_costs: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostSummary":
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


# --- Approval ---


@dataclass
class ApprovalRequest:
    id: str = ""
    execution_id: str = ""
    workspace_id: str = ""
    agent_id: Optional[str] = None
    checkpoint_name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    reason: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalRequest":
        return _from_dict(cls, data)


# --- Flow Template ---


@dataclass
class FlowTemplate:
    id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    agent_type: str = ""
    complexity: str = ""
    tags: List[str] = field(default_factory=list)
    icon: str = ""
    node_count: int = 0
    flow_config: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowTemplate":
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


# --- Score ---


@dataclass
class Score:
    id: str = ""
    workspace_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    name: str = ""
    value: Optional[float] = None
    string_value: str = ""
    data_type: str = "numeric"
    source: str = "manual"
    config_id: Optional[str] = None
    comment: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Score":
        return _from_dict(cls, data)


@dataclass
class ScoreConfig:
    id: str = ""
    workspace_id: str = ""
    name: str = ""
    data_type: str = "numeric"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    categories: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreConfig":
        return _from_dict(cls, data)


@dataclass
class ScoreAggregate:
    name: str = ""
    count: int = 0
    avg: float = 0.0
    min: float = 0.0
    max: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreAggregate":
        return _from_dict(cls, data)


# --- Dashboard ---


@dataclass
class DashboardMetrics:
    overview: Dict[str, Any] = field(default_factory=dict)
    executions_by_day: List[Dict[str, Any]] = field(default_factory=list)
    cost_by_day: List[Dict[str, Any]] = field(default_factory=list)
    agent_usage: List[Dict[str, Any]] = field(default_factory=list)
    model_usage: List[Dict[str, Any]] = field(default_factory=list)
    error_rate: List[Dict[str, Any]] = field(default_factory=list)
    score_trends: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DashboardMetrics":
        return _from_dict(cls, data)


# --- Session & User ---


@dataclass
class SessionSummary:
    session_id: str = ""
    trace_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    error_count: int = 0
    first_seen: str = ""
    last_seen: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionSummary":
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
class WebhookTrigger:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    name: str = ""
    token: str = ""
    token_prefix: str = ""
    is_active: bool = True
    has_secret: bool = False
    last_used_at: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookTrigger":
        return _from_dict(cls, data)


@dataclass
class WebhookTriggerCreateResponse:
    id: str = ""
    workspace_id: str = ""
    agent_id: str = ""
    name: str = ""
    token: str = ""
    token_prefix: str = ""
    is_active: bool = True
    has_secret: bool = False
    last_used_at: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    secret: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookTriggerCreateResponse":
        return _from_dict(cls, data)


# --- Media ---


@dataclass
class MediaModel:
    id: str = ""
    provider: str = ""
    model_id: str = ""
    display_name: str = ""
    media_type: str = ""
    is_active: bool = True
    capabilities: Dict[str, Any] = field(default_factory=dict)
    config_schema: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaModel":
        return _from_dict(cls, data)


@dataclass
class MediaGenerateResult:
    asset_id: str = ""
    url: str = ""
    media_type: str = ""
    provider: str = ""
    model: str = ""
    duration_ms: Optional[int] = None
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaGenerateResult":
        return _from_dict(cls, data)


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
