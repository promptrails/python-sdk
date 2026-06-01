"""OpenAI / Anthropic integration — wrap a client so each completion call is
traced automatically (model, token usage, latency, output).

Usage::

    from openai import OpenAI
    from promptrails.tracing import Tracer
    from promptrails.tracing.integrations.openai import trace_openai

    tracer = Tracer(api_key="pr_...")
    client = trace_openai(OpenAI(), tracer)

    client.chat.completions.create(model="gpt-4o", messages=[...])  # auto-traced

The wrapper is duck-typed: it patches ``client.chat.completions.create`` and
reads ``model``/``usage``/``choices`` off the response, so it works with the
OpenAI SDK and any API-compatible client. Streaming responses are passed through
untraced for token usage (the span still records the call and model).
"""

from __future__ import annotations

import functools
from typing import Any

from ..tracer import Tracer


def trace_openai(client: Any, tracer: Tracer, *, span_name: str = "openai.chat") -> Any:
    """Patch ``client.chat.completions.create`` to emit an ``llm`` span per call.
    Returns the same client for convenience."""
    completions = client.chat.completions
    original = completions.create

    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        with tracer.span(span_name, kind="llm") as span:
            model = kwargs.get("model")
            if model:
                span.set_model(model)
            if kwargs.get("messages") is not None:
                span.set_input({"messages": kwargs["messages"]})
            response = original(*args, **kwargs)
            _apply_response(span, response)
            return response

    completions.create = wrapped
    return client


def _apply_response(span: Any, response: Any) -> None:
    usage = getattr(response, "usage", None)
    if usage is not None:
        prompt = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
        completion = getattr(usage, "completion_tokens", None) or getattr(
            usage, "output_tokens", None
        )
        total = getattr(usage, "total_tokens", None)
        if prompt is not None or completion is not None:
            span.set_usage(prompt, completion, total)
    model = getattr(response, "model", None)
    if model:
        span.set_model(model)
    text = _first_choice_text(response)
    if text is not None:
        span.set_output({"content": text})


def _first_choice_text(response: Any) -> Any:
    try:
        choice = response.choices[0]
    except Exception:  # pragma: no cover - defensive
        return None
    message = getattr(choice, "message", None)
    if message is not None and getattr(message, "content", None) is not None:
        return message.content
    return getattr(choice, "text", None)
