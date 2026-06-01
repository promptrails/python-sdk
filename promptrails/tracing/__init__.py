"""PromptRails tracing — send spans to PromptRails from any code, without
managing your prompts or agents on the platform.

This subpackage is independent of the API-client resources; you only need an
API key with the ``traces:write`` scope.

    from promptrails.tracing import Tracer

    tracer = Tracer(api_key="pr_...")
    with tracer.span("my-pipeline", kind="chain") as span:
        ...
"""

from .exporter import SpanExporter
from .span import Span
from .tracer import Tracer

__all__ = ["Span", "SpanExporter", "Tracer"]
