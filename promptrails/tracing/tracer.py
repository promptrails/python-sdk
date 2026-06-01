"""Tracer — the entry point for producing PromptRails traces.

The tracer owns span context propagation (so nested spans automatically link to
their parent) and an exporter that ships finished spans to the ingest API.

Example::

    from promptrails.tracing import Tracer

    tracer = Tracer(api_key="pr_...")

    with tracer.span("agent-run", kind="agent") as root:
        root.set_input({"q": "weather?"})
        with tracer.span("llm-call", kind="llm") as llm:
            llm.set_model("gpt-4o").set_usage(120, 30)

    tracer.flush()
"""

from __future__ import annotations

import contextvars
import functools
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional

from .._http import HTTPClient
from ..config import Config
from .exporter import SpanExporter
from .span import Span

# Holds the currently-active span so child spans can find their parent. Using a
# ContextVar makes nesting work correctly across both threads and asyncio tasks.
_current_span: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar(
    "promptrails_current_span", default=None
)


class Tracer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://api.promptrails.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        http: Optional[HTTPClient] = None,
        exporter: Optional[SpanExporter] = None,
        max_batch_size: int = 100,
        flush_interval: float = 1.0,
    ) -> None:
        if exporter is not None:
            self._exporter = exporter
        else:
            if http is None:
                if not api_key:
                    raise ValueError("Tracer requires an api_key (or an http/exporter)")
                http = HTTPClient(
                    Config(
                        api_key=api_key,
                        base_url=base_url,
                        timeout=timeout,
                        max_retries=max_retries,
                    )
                )
            self._exporter = SpanExporter(
                http, max_batch_size=max_batch_size, flush_interval=flush_interval
            )

    # -- span creation ----------------------------------------------------

    def start_span(
        self,
        name: str,
        *,
        kind: str = "chain",
        session_id: Optional[str] = None,
        parent: Optional[Span] = None,
    ) -> Span:
        """Create a span without entering a context block. The caller is
        responsible for calling :meth:`Span.end`. Parent and trace ID are
        inherited from the active span unless ``parent`` is given."""
        parent = parent or _current_span.get()
        return Span(
            name,
            kind=kind,
            session_id=session_id or (parent.session_id if parent else None),
            trace_id=parent.trace_id if parent else None,
            parent_span_id=parent.span_id if parent else None,
            on_end=self._on_span_end,
        )

    def _on_span_end(self, span: Span) -> None:
        self._exporter.submit(span.to_payload())

    @contextmanager
    def span(
        self,
        name: str,
        *,
        kind: str = "chain",
        session_id: Optional[str] = None,
    ) -> Iterator[Span]:
        """Context manager that creates a span, makes it the active parent for
        the block, ends it on exit, and records exceptions as span errors."""
        span = self.start_span(name, kind=kind, session_id=session_id)
        token = _current_span.set(span)
        try:
            yield span
        except BaseException as exc:
            span.set_error(exc)
            raise
        finally:
            _current_span.reset(token)
            span.end()

    def trace(
        self,
        name: Optional[str] = None,
        *,
        kind: str = "chain",
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator that wraps a function call in a span (named after the
        function unless ``name`` is given)."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            span_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.span(span_name, kind=kind):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    # -- lifecycle --------------------------------------------------------

    def current_span(self) -> Optional[Span]:
        return _current_span.get()

    def flush(self) -> None:
        self._exporter.flush()

    def shutdown(self) -> None:
        self._exporter.shutdown()
