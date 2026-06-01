"""Anthropic integration — wrap a client so each Messages call is traced
automatically (model, token usage, latency, output).

Usage::

    from anthropic import Anthropic
    from promptrails.tracing import Tracer
    from promptrails.tracing.integrations.anthropic import trace_anthropic

    tracer = Tracer(api_key="pr_...")
    client = trace_anthropic(Anthropic(), tracer)

    client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, messages=[...])

Duck-typed: it patches ``client.messages.create`` and reads ``model``/``usage``/
``content`` off the response, so it works with the Anthropic SDK and any
API-compatible client.
"""

from __future__ import annotations

import functools
from typing import Any

from ..tracer import Tracer


def trace_anthropic(client: Any, tracer: Tracer, *, span_name: str = "anthropic.messages") -> Any:
    """Patch ``client.messages.create`` to emit an ``llm`` span per call.
    Returns the same client for convenience."""
    messages = client.messages
    original = messages.create

    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        with tracer.span(span_name, kind="llm") as span:
            model = kwargs.get("model")
            if model:
                span.set_model(model)
            if kwargs.get("messages") is not None:
                span.set_input({"messages": kwargs["messages"], "system": kwargs.get("system")})
            response = original(*args, **kwargs)
            _apply_response(span, response)
            return response

    messages.create = wrapped
    return client


def _apply_response(span: Any, response: Any) -> None:
    usage = getattr(response, "usage", None)
    if usage is not None:
        prompt = getattr(usage, "input_tokens", None)
        completion = getattr(usage, "output_tokens", None)
        if prompt is not None or completion is not None:
            span.set_usage(prompt, completion)
    model = getattr(response, "model", None)
    if model:
        span.set_model(model)
    text = _content_text(response)
    if text is not None:
        span.set_output({"content": text})


def _content_text(response: Any) -> Any:
    content = getattr(response, "content", None)
    if isinstance(content, list) and content:
        # Anthropic returns a list of content blocks; surface the first text block.
        for block in content:
            text = getattr(block, "text", None)
            if text is not None:
                return text
    return None
