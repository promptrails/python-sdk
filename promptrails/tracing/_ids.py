"""Identifier helpers for trace and span IDs.

Trace IDs are 16 random bytes (32 hex chars) and span IDs are 8 random bytes
(16 hex chars), matching the OpenTelemetry sizing the backend expects.
"""

from __future__ import annotations

import secrets


def generate_trace_id() -> str:
    """Return a 32-character hex trace ID."""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """Return a 16-character hex span ID."""
    return secrets.token_hex(8)
