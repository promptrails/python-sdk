from __future__ import annotations

from promptrails._sse import (
    ContentEvent,
    DoneEvent,
    ErrorEvent,
    ExecutionEvent,
    ThinkingEvent,
    ToolEndEvent,
    ToolStartEvent,
    _iter_sse_frames,
)
from promptrails.agent_config import (
    ChainAgentConfig,
    CompositeAgentConfig,
    CompositeStep,
    MultiAgentConfig,
    PromptLink,
    SimpleAgentConfig,
    WorkflowAgentConfig,
    WorkflowNode,
)


def _parse(*chunks: str):
    return list(_iter_sse_frames(iter(chunks)))


def test_parses_full_chat_stream():
    body = (
        'event: execution\ndata: {"execution_id":"e1","user_message_id":"m1"}\n\n'
        'event: thinking\ndata: {"content":"checking"}\n\n'
        'event: tool_start\ndata: {"id":"t1","name":"search"}\n\n'
        'event: tool_end\ndata: {"id":"t1","name":"search","summary":"3 hits"}\n\n'
        'event: content\ndata: {"content":"Hello"}\n\n'
        "event: done\ndata: "
        '{"output":{"content":"Hello world"},"token_usage":{"total_tokens":42}}\n\n'
    )
    events = _parse(body)
    assert len(events) == 6

    assert isinstance(events[0], ExecutionEvent)
    assert events[0].execution_id == "e1"
    assert events[0].user_message_id == "m1"

    assert isinstance(events[1], ThinkingEvent)
    assert events[1].content == "checking"

    assert isinstance(events[2], ToolStartEvent)
    assert events[2].id == "t1"

    assert isinstance(events[3], ToolEndEvent)
    assert events[3].summary == "3 hits"

    assert isinstance(events[4], ContentEvent)
    assert events[4].content == "Hello"

    assert isinstance(events[5], DoneEvent)
    assert events[5].output == {"content": "Hello world"}
    assert events[5].token_usage.total_tokens == 42


def test_handles_frames_split_across_chunks():
    events = _parse(
        "event: conte",
        'nt\ndata: {"cont',
        'ent":"hi"}\n\n',
        "event: done\ndata: {}\n\n",
    )
    assert len(events) == 2
    assert isinstance(events[0], ContentEvent)
    assert events[0].content == "hi"
    assert isinstance(events[1], DoneEvent)


def test_skips_unknown_event_types():
    events = _parse(
        'event: ping\ndata: {"ok":true}\n\n',
        'event: content\ndata: {"content":"x"}\n\n',
    )
    assert len(events) == 1
    assert isinstance(events[0], ContentEvent)


def test_error_event_prefers_message_then_error():
    events = _parse('event: error\ndata: {"message":"quota"}\n\n')
    assert isinstance(events[0], ErrorEvent)
    assert events[0].message == "quota"


def test_agent_config_to_dict_injects_type_discriminator():
    assert SimpleAgentConfig(prompt_id="p1").to_dict()["type"] == "simple"
    assert ChainAgentConfig(prompt_ids=[PromptLink("p1", "main", 0)]).to_dict()["type"] == "chain"
    assert (
        MultiAgentConfig(prompt_ids=[PromptLink("p1", "a", 0)]).to_dict()["type"] == "multi_agent"
    )
    assert WorkflowAgentConfig(nodes=[WorkflowNode(id="n1")]).to_dict()["type"] == "workflow"
    assert (
        CompositeAgentConfig(steps=[CompositeStep(id="s1", agent_id="a1")]).to_dict()["type"]
        == "composite"
    )


def test_simple_config_drops_unset_fields():
    out = SimpleAgentConfig(prompt_id="p1").to_dict()
    # Optional fields not set should not leak through.
    assert "max_tokens" not in out
    assert "temperature" not in out
    assert "llm_model_id" not in out
    assert "approval_checkpoint_name" not in out
