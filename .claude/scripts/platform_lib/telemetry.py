"""Project telemetry: consolidated observability sink + auto script-metrics (I4).

Two responsibilities:

1. **Canonical sink root.** `TELEMETRY_DIR` (`.claude/telemetry/`) is the single
   directory all project-owned JSONL event/signal/audit streams live in, so the
   dashboard (M1) and forensics parser (P1) read one place instead of five.
   `sink_path(name)` and `append_event(name, record)` are the shared writers.

2. **Auto script metrics.** Importing this module (it is auto-imported via
   ``platform_lib/__init__.py``) registers an ``atexit`` handler that records the
   script's path, exit state, duration, and argv to ``script-telemetry.jsonl``.

Disabled (no atexit, no writes) whenever ``CK_TELEMETRY_DISABLED`` is set or a
pytest run is detected (``PYTEST_CURRENT_TEST``) — keeps test runs zero-side-effect
(GOLDEN RULE #3). The conftest sets ``CK_TELEMETRY_DISABLED`` before any import.
"""
from __future__ import annotations

import atexit
import json
import os
import sys
import time
import traceback
from pathlib import Path

# Rotate a sink once it crosses this size; keeps one .bak generation.
_MAX_SINK_BYTES = 8 * 1024 * 1024  # 8 MB


def _disabled() -> bool:
    return bool(os.environ.get("CK_TELEMETRY_DISABLED")) or "PYTEST_CURRENT_TEST" in os.environ


def _find_telemetry_dir() -> Path:
    """Resolve the consolidated sink root. CK_TELEMETRY_DIR env overrides (test isolation)."""
    override = os.environ.get("CK_TELEMETRY_DIR")
    if override:
        return Path(override)
    p = Path(__file__).resolve()
    while p != p.parent:
        if (p / ".claude").is_dir():
            return p / ".claude" / "telemetry"
        p = p.parent
    # Fallback: .claude/scripts/platform_lib/telemetry.py -> parents[2] == .claude
    return Path(__file__).resolve().parents[2] / "telemetry"


TELEMETRY_DIR = _find_telemetry_dir()


def telemetry_dir() -> Path:
    """Absolute path to the consolidated telemetry root (created on demand)."""
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    return TELEMETRY_DIR


def sink_path(name: str) -> Path:
    """Resolve a JSONL sink file inside the consolidated root, e.g. ``"invocations.jsonl"``."""
    return telemetry_dir() / name


def _rotate_if_large(path: Path) -> None:
    try:
        if path.exists() and path.stat().st_size > _MAX_SINK_BYTES:
            path.replace(path.with_suffix(path.suffix + ".bak"))
    except OSError:
        pass


def append_event(name: str, record: dict) -> None:
    """Append one JSON line to a consolidated sink. No-op when telemetry is disabled.

    Shared by every project-owned writer so the sink directory stays single-rooted.
    """
    if _disabled():
        return
    try:
        path = sink_path(name)
        _rotate_if_large(path)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


# --- I4: automatic per-script execution metrics -----------------------------

_start = time.time()
_failed = False

_orig_excepthook = sys.excepthook


def _excepthook(exc_type, exc_value, exc_tb):
    global _failed
    _failed = True
    # Auto-capture the crash as a structured error (I6) — covers every script
    # that imports platform_lib, no per-script boilerplate. Never let error
    # logging mask the original traceback.
    try:
        append_event("errors.jsonl", {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "script": sys.argv[0] if sys.argv else "unknown",
            "category": "unhandled",
            "message": f"{exc_type.__name__}: {exc_value}"[:200],
            "context": {"frame": traceback.format_tb(exc_tb)[-1][:200] if exc_tb else ""},
        })
    except Exception:  # pragma: no cover - defensive
        pass
    _orig_excepthook(exc_type, exc_value, exc_tb)


def _emit_script_metrics() -> None:
    append_event(
        "script-telemetry.jsonl",
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "script": sys.argv[0] if sys.argv else "unknown",
            "exit": 1 if _failed else 0,
            "ms": int((time.time() - _start) * 1000),
            "argv": sys.argv[1:6],
        },
    )


if not _disabled():
    sys.excepthook = _excepthook
    atexit.register(_emit_script_metrics)
