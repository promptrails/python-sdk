"""Typed agent-version configs used by ``agents.create_version``.

PromptRails API v2 has exactly two agent kinds:

* ``agent``    — a prompt plus optional tools / sub-agents (a supervisor when it
  has sub-agents). Built with :class:`PromptAgentConfig`.
* ``workflow`` — a deterministic DAG of nodes. Built with
  :class:`WorkflowAgentConfig`.

``to_dict()`` emits the JSON ``config`` payload with the ``type`` discriminator
injected automatically, so callers never forget to set it. Model, sampling,
budget, approval policy, cache TTL and tool/sub-agent attachments are *not* part
of ``config`` — they are version-scoped fields passed alongside it to
``create_version`` (see :class:`~promptrails.types.ModelConfig`,
:class:`~promptrails.types.RunBudget`, :class:`~promptrails.types.ApprovalPolicy`,
:class:`ToolAttachment`, :class:`SubAgentAttachment`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union


def _strip_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


@dataclass
class WorkflowNode:
    """A single node in a ``workflow`` agent's DAG."""

    id: str
    depends_on: List[str] = field(default_factory=list)
    prompt_id: Optional[str] = None
    node_type: Optional[str] = None  # "prompt" | "media"
    media_provider: Optional[str] = None
    media_type: Optional[str] = None
    media_model: Optional[str] = None
    media_config: Optional[Dict[str, Any]] = None


@dataclass
class ToolAttachment:
    """An MCP tool attached to an agent version with per-tool policy."""

    mcp_tool_id: str
    requires_approval: bool = False
    no_retry: bool = False
    sort_order: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none(
            {
                "mcp_tool_id": self.mcp_tool_id,
                "requires_approval": self.requires_approval,
                "no_retry": self.no_retry,
                "sort_order": self.sort_order,
            }
        )


@dataclass
class SubAgentAttachment:
    """A delegate sub-agent attached to an agent version (agents-as-tools)."""

    agent_id: str
    alias: str
    description: Optional[str] = None
    mode: Optional[str] = None  # "delegate" | "handoff"
    context_mode: Optional[str] = None  # "task" | "window"
    requires_approval: bool = False
    sort_order: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _strip_none(
            {
                "agent_id": self.agent_id,
                "alias": self.alias,
                "description": self.description,
                "mode": self.mode,
                "context_mode": self.context_mode,
                "requires_approval": self.requires_approval,
                "sort_order": self.sort_order,
            }
        )


class AgentConfig:
    """Marker base class for version ``config`` payloads."""

    type: str = ""

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover — abstract
        raise NotImplementedError


@dataclass
class PromptAgentConfig(AgentConfig):
    """Config for an ``agent`` — a single prompt (+ optional tools/sub-agents)."""

    prompt_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {"prompt_id": self.prompt_id, "type": "agent"}


@dataclass
class WorkflowAgentConfig(AgentConfig):
    """Config for a ``workflow`` — a deterministic DAG of nodes."""

    nodes: List[WorkflowNode]

    def to_dict(self) -> Dict[str, Any]:
        nodes = [_strip_none(asdict(n)) for n in self.nodes]
        return {"nodes": nodes, "type": "workflow"}


AnyAgentConfig = Union[PromptAgentConfig, WorkflowAgentConfig]
