"""Structured error emission for skill scripts (I6).

A thin wrapper over ``telemetry.append_event`` so explicit failure paths land in
the same consolidated sink (``errors.jsonl``) and inherit the identical
``CK_TELEMETRY_DISABLED`` / ``CK_TELEMETRY_DIR`` gate — zero side effects under
pytest (GOLDEN RULE #3). Reuses telemetry rather than reimplementing sink
resolution (DRY).

Use ``emit_error`` on *genuine* failure branches (a handler that aborts, exits,
or degrades the script's result) — NOT on expected control-flow skips like
``except json.JSONDecodeError: continue`` when tolerating a malformed line.
Unhandled crashes are captured automatically by telemetry's excepthook, so
emit_error is only for caught-but-real errors.

Categories: import | parse | io | validation | api (| unhandled — excepthook only).
"""
from __future__ import annotations

import sys
import time

from . import telemetry

CATEGORIES = ("import", "parse", "io", "validation", "api", "unhandled")


def emit_error(category: str, message, context: dict | None = None, *, script: str | None = None) -> None:
    """Append one structured error record to errors.jsonl (no-op when disabled)."""
    telemetry.append_event("errors.jsonl", {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script": script or (sys.argv[0] if sys.argv else "unknown"),
        "category": category,
        "message": str(message)[:200],
        "context": context or {},
    })
