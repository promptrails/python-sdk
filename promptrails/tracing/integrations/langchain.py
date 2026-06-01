"""LangChain integration — a callback handler that turns LangChain runs into
PromptRails spans (Sentry-style auto-instrumentation).

Usage::

    from promptrails.tracing import Tracer
    from promptrails.tracing.integrations.langchain import PromptRailsCallbackHandler

    tracer = Tracer(api_key="pr_...")
    handler = PromptRailsCallbackHandler(tracer)

    chain.invoke({"q": "hi"}, config={"callbacks": [handler]})

The handler builds the span tree from LangChain's ``run_id``/``parent_run_id``
(not thread-local context), so it works under threads and async runs.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from ..tracer import Tracer

try:  # LangChain is an optional dependency.
    from langchain_core.callbacks import BaseCallbackHandler as _Base
except Exception:  # pragma: no cover - exercised only without langchain
    _Base = object


class PromptRailsCallbackHandler(_Base):
    """Maps LangChain callbacks onto PromptRails spans."""

    def __init__(self, tracer: Tracer, *, session_id: Optional[str] = None) -> None:
        # When langchain is installed, _Base is its BaseCallbackHandler so the
        # handler plugs into LangChain's callback system; without it the class
        # still works (e.g. for testing) but won't be auto-discovered by chains.
        super().__init__()
        self._tracer = tracer
        self._session_id = session_id
        self._spans: Dict[Any, Any] = {}
        self._lock = threading.Lock()

    # -- span tree bookkeeping -------------------------------------------

    def _start(self, run_id, parent_run_id, name, kind, input_value=None):
        with self._lock:
            parent = self._spans.get(parent_run_id)
        span = self._tracer.start_span(name, kind=kind, parent=parent, session_id=self._session_id)
        if input_value is not None:
            span.set_input(input_value)
        with self._lock:
            self._spans[run_id] = span
        return span

    def _end(self, run_id, output_value=None):
        with self._lock:
            span = self._spans.pop(run_id, None)
        if span is None:
            return
        if output_value is not None:
            span.set_output(output_value)
        span.end()

    def _error(self, run_id, error):
        with self._lock:
            span = self._spans.pop(run_id, None)
        if span is None:
            return
        span.set_error(error)
        span.end()

    # -- chains -----------------------------------------------------------

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None, **kwargs):
        self._start(run_id, parent_run_id, _name(serialized, "chain"), "chain", inputs)

    def on_chain_end(self, outputs, *, run_id, **kwargs):
        self._end(run_id, outputs)

    def on_chain_error(self, error, *, run_id, **kwargs):
        self._error(run_id, error)

    # -- LLMs -------------------------------------------------------------

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, **kwargs):
        span = self._start(
            run_id, parent_run_id, _name(serialized, "llm"), "llm", {"prompts": prompts}
        )
        _apply_model(span, kwargs)

    def on_chat_model_start(self, serialized, messages, *, run_id, parent_run_id=None, **kwargs):
        span = self._start(
            run_id,
            parent_run_id,
            _name(serialized, "llm"),
            "llm",
            {"messages": _stringify(messages)},
        )
        _apply_model(span, kwargs)

    def on_llm_end(self, response, *, run_id, **kwargs):
        with self._lock:
            span = self._spans.get(run_id)
        if span is not None:
            _apply_llm_output(span, response)
        self._end(run_id, _llm_text(response))

    def on_llm_error(self, error, *, run_id, **kwargs):
        self._error(run_id, error)

    # -- tools ------------------------------------------------------------

    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, **kwargs):
        self._start(run_id, parent_run_id, _name(serialized, "tool"), "tool", {"input": input_str})

    def on_tool_end(self, output, *, run_id, **kwargs):
        self._end(run_id, {"output": str(output)})

    def on_tool_error(self, error, *, run_id, **kwargs):
        self._error(run_id, error)

    # -- retrievers -------------------------------------------------------

    def on_retriever_start(self, serialized, query, *, run_id, parent_run_id=None, **kwargs):
        self._start(
            run_id, parent_run_id, _name(serialized, "retriever"), "datasource", {"query": query}
        )

    def on_retriever_end(self, documents, *, run_id, **kwargs):
        self._end(run_id, {"documents": len(documents) if documents is not None else 0})

    def on_retriever_error(self, error, *, run_id, **kwargs):
        self._error(run_id, error)


# -- helpers --------------------------------------------------------------


def _name(serialized: Optional[Dict[str, Any]], default: str) -> str:
    if not serialized:
        return default
    if serialized.get("name"):
        return serialized["name"]
    ident = serialized.get("id")
    if isinstance(ident, list) and ident:
        return ident[-1]
    return default


def _apply_model(span, kwargs: Dict[str, Any]) -> None:
    params = kwargs.get("invocation_params") or {}
    model = params.get("model") or params.get("model_name")
    if model:
        span.set_model(model)


def _apply_llm_output(span, response) -> None:
    output = getattr(response, "llm_output", None) or {}
    usage = output.get("token_usage") or output.get("usage") or {}
    prompt = usage.get("prompt_tokens") or usage.get("input_tokens")
    completion = usage.get("completion_tokens") or usage.get("output_tokens")
    if prompt is not None or completion is not None:
        span.set_usage(prompt, completion, usage.get("total_tokens"))
    model = output.get("model_name") or output.get("model")
    if model:
        span.set_model(model)


def _llm_text(response) -> Optional[Dict[str, Any]]:
    try:
        generations = response.generations
        first = generations[0][0]
        return {"text": getattr(first, "text", None) or str(first)}
    except Exception:  # pragma: no cover - defensive
        return None


def _stringify(messages) -> Any:
    try:
        return [[getattr(m, "content", str(m)) for m in batch] for batch in messages]
    except Exception:  # pragma: no cover - defensive
        return str(messages)
