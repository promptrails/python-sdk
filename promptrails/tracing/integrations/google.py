"""Google GenAI integration — wrap a client so each generate_content call is
traced automatically (model, token usage, latency, output).

Usage::

    from google import genai
    from promptrails.tracing import Tracer
    from promptrails.tracing.integrations.google import trace_google

    tracer = Tracer(api_key="pr_...")
    client = trace_google(genai.Client(), tracer)

    client.models.generate_content(model="gemini-2.0-flash", contents="Hello")

Targets the unified ``google-genai`` SDK (``client.models.generate_content``).
Duck-typed: it reads ``usage_metadata`` and ``text`` off the response.
"""

from __future__ import annotations

import functools
from typing import Any

from ..tracer import Tracer


def trace_google(client: Any, tracer: Tracer, *, span_name: str = "google.generate_content") -> Any:
    """Patch ``client.models.generate_content`` to emit an ``llm`` span per call.
    Returns the same client for convenience."""
    models = client.models
    original = models.generate_content

    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        with tracer.span(span_name, kind="llm") as span:
            model = kwargs.get("model")
            if model:
                span.set_model(model)
            if kwargs.get("contents") is not None:
                span.set_input({"contents": kwargs["contents"]})
            response = original(*args, **kwargs)
            _apply_response(span, response, model)
            return response

    models.generate_content = wrapped
    return client


def _apply_response(span: Any, response: Any, request_model: Any) -> None:
    usage = getattr(response, "usage_metadata", None)
    if usage is not None:
        prompt = getattr(usage, "prompt_token_count", None)
        completion = getattr(usage, "candidates_token_count", None)
        total = getattr(usage, "total_token_count", None)
        if prompt is not None or completion is not None:
            span.set_usage(prompt, completion, total)
    model = getattr(response, "model_version", None) or request_model
    if model:
        span.set_model(model)
    text = getattr(response, "text", None)
    if text is not None:
        span.set_output({"text": text})
