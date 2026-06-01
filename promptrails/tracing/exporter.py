"""SpanExporter — buffers finished spans and ships them to the ingest API.

Spans are queued in memory and flushed in batches either when the buffer fills
up or on a fixed interval by a background daemon thread. Export is best-effort:
failures are logged and dropped rather than raised into the caller's code path,
and the buffer is bounded so a broken endpoint can't grow memory without limit.
"""

from __future__ import annotations

import atexit
import logging
import threading
from typing import Any, Dict, List

from .._http import HTTPClient

logger = logging.getLogger("promptrails.tracing")

INGEST_PATH = "/api/v1/traces/ingest"


class SpanExporter:
    def __init__(
        self,
        http: HTTPClient,
        *,
        max_batch_size: int = 100,
        flush_interval: float = 1.0,
        max_queue_size: int = 10_000,
    ) -> None:
        self._http = http
        self._max_batch_size = max_batch_size
        self._flush_interval = flush_interval
        self._max_queue_size = max_queue_size

        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._flush_now = threading.Event()
        self._stop = threading.Event()

        self._worker = threading.Thread(
            target=self._run, name="promptrails-span-exporter", daemon=True
        )
        self._worker.start()
        atexit.register(self.shutdown)

    def submit(self, payload: Dict[str, Any]) -> None:
        """Queue a span payload for export. Drops the span (with a warning) if
        the buffer is full, so a stalled endpoint never blocks the caller."""
        with self._lock:
            if len(self._buffer) >= self._max_queue_size:
                logger.warning("promptrails tracing buffer full; dropping span")
                return
            self._buffer.append(payload)
            should_flush = len(self._buffer) >= self._max_batch_size
        if should_flush:
            self._flush_now.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            # Wake on interval, on an explicit flush signal, or on shutdown.
            self._flush_now.wait(self._flush_interval)
            self._flush_now.clear()
            self._drain()

    def _drain(self) -> None:
        while True:
            with self._lock:
                if not self._buffer:
                    return
                batch = self._buffer[: self._max_batch_size]
                self._buffer = self._buffer[self._max_batch_size :]
            self._send(batch)

    def _send(self, spans: List[Dict[str, Any]]) -> None:
        if not spans:
            return
        try:
            self._http.post(INGEST_PATH, json={"spans": spans})
        except Exception as exc:
            logger.warning("promptrails trace export failed (%d spans): %s", len(spans), exc)

    def flush(self) -> None:
        """Block until the current buffer has been sent."""
        self._drain()

    def shutdown(self) -> None:
        """Flush remaining spans and stop the worker. Idempotent."""
        if self._stop.is_set():
            return
        self._stop.set()
        self._flush_now.set()
        self._drain()
        if self._worker.is_alive():
            self._worker.join(timeout=2.0)
