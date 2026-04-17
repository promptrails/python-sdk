"""Typed agent configs used by ``agents.create_version``.

Each concrete class declares the fields the backend expects for its agent
type. ``to_dict()`` emits the JSON payload with the ``type`` discriminator
injected automatically, so callers never forget to set it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class PromptLink:
    """Pins a prompt into a chain/multi-agent step at a role."""

    prompt_id: str
    role: str
    sort_order: int


@dataclass
class WorkflowNode:
    id: str
    depends_on: List[str] = field(default_factory=list)
    prompt_id: Optional[str] = None
    node_type: Optional[str] = None  # "prompt" | "media"
    media_provider: Optional[str] = None
    media_type: Optional[str] = None
    media_model: Optional[str] = None
    media_config: Optional[Dict[str, Any]] = None


@dataclass
class CompositeStep:
    id: str
    agent_id: str
    depends_on: List[str] = field(default_factory=list)
    input_mapping: Optional[Dict[str, Any]] = None


def _strip_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


class AgentConfig:
    """Marker base class. Subclasses implement ``to_dict()``."""

    type: str = ""

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover — abstract
        raise NotImplementedError


@dataclass
class SimpleAgentConfig(AgentConfig):
    prompt_id: str
    approval_required: bool = False
    approval_checkpoint_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    llm_model_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out = _strip_none(
            {
                "prompt_id": self.prompt_id,
                "approval_required": self.approval_required,
                "approval_checkpoint_name": self.approval_checkpoint_name,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "llm_model_id": self.llm_model_id,
            }
        )
        out["type"] = "simple"
        return out


@dataclass
class ChainAgentConfig(AgentConfig):
    prompt_ids: List[PromptLink]
    approval_required: bool = False
    approval_checkpoint_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "prompt_ids": [asdict(p) for p in self.prompt_ids],
            "approval_required": self.approval_required,
        }
        if self.approval_checkpoint_name is not None:
            out["approval_checkpoint_name"] = self.approval_checkpoint_name
        out["type"] = "chain"
        return out


@dataclass
class MultiAgentConfig(AgentConfig):
    prompt_ids: List[PromptLink]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_ids": [asdict(p) for p in self.prompt_ids],
            "type": "multi_agent",
        }


@dataclass
class WorkflowAgentConfig(AgentConfig):
    nodes: List[WorkflowNode]

    def to_dict(self) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        for n in self.nodes:
            d = asdict(n)
            nodes.append(_strip_none(d))
        return {"nodes": nodes, "type": "workflow"}


@dataclass
class CompositeAgentConfig(AgentConfig):
    steps: List[CompositeStep]

    def to_dict(self) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        for s in self.steps:
            d = asdict(s)
            steps.append(_strip_none(d))
        return {"steps": steps, "type": "composite"}


AnyAgentConfig = Union[
    SimpleAgentConfig,
    ChainAgentConfig,
    MultiAgentConfig,
    WorkflowAgentConfig,
    CompositeAgentConfig,
]
