"""Core types, constants, and primitive detection functions for session health monitoring.

Layers: process liveness, file freshness, content inspection, error classification.
"""
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ErrorClass(Enum):
    NONE = "none"
    RETRYABLE = "retryable"
    TIME_RETRYABLE = "time_retryable"
    NON_RETRYABLE = "non_retryable"


class Severity(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


RETRYABLE_PATTERNS = [
    "API Error", "JSON Parse error", "Unexpected EOF",
    "ECONNRESET", "socket hang up",
    "Internal Server Error", "Service Unavailable",
]

TIME_RETRYABLE_PATTERNS = ["429", "Rate limit", "rate_limit", "Too Many Requests"]

NON_RETRYABLE_PATTERNS = [
    "invalid_api_key", "context_length_exceeded", "credit", "billing",
]

VERBOSITY_MAP = {"error": Severity.ERROR, "warn": Severity.WARN, "info": Severity.INFO, "debug": Severity.DEBUG}


@dataclass
class SessionPaths:
    jsonl: Path | None = None
    pid_file: Path | None = None
    session_id: str = ""
    project_slug: str = ""


@dataclass
class HealthEvent:
    severity: Severity
    category: str
    target: str
    message: str


@dataclass
class MonitorConfig:
    soft_threshold: int = 120
    hard_threshold: int = 300
    include_429: bool = False
    verbosity: Severity = Severity.WARN
    poll_interval: int = 30
    team_name: str = ""


def resolve_project_slug(cwd: str | None = None) -> str:
    """Convert CWD to Claude Code project slug (keeps leading dash)."""
    return (cwd or os.getcwd()).replace("/", "-")


def read_last_jsonl_line(path: Path, tail_bytes: int = 8192) -> dict | None:
    """Read last complete JSON line from a JSONL file (only reads tail)."""
    if not path or not path.exists():
        return None
    size = path.stat().st_size
    if size == 0:
        return None

    try:
        with open(path, "rb") as f:
            read_size = min(tail_bytes, size)
            f.seek(max(0, size - read_size))
            chunk = f.read().decode("utf-8", errors="replace")
    except OSError:
        return None

    for line in reversed(chunk.strip().split("\n")):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def extract_error_text(jsonl_line: dict) -> list[str]:
    """Extract text fields that may contain errors from both JSONL locations."""
    texts = []
    tr = jsonl_line.get("toolUseResult", {})
    if isinstance(tr, dict):
        for item in tr.get("content", []):
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
    msg = jsonl_line.get("message", {})
    if isinstance(msg, dict):
        for item in msg.get("content", []):
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
    return texts


def classify_error(texts: list[str], include_429: bool = False) -> ErrorClass:
    """Classify error from extracted text fields."""
    combined = " ".join(texts)
    if not combined.strip():
        return ErrorClass.NONE

    for pat in NON_RETRYABLE_PATTERNS:
        if pat in combined:
            return ErrorClass.NON_RETRYABLE

    for pat in RETRYABLE_PATTERNS:
        if pat in combined:
            return ErrorClass.RETRYABLE

    if include_429:
        for pat in TIME_RETRYABLE_PATTERNS:
            if pat in combined:
                return ErrorClass.TIME_RETRYABLE

    return ErrorClass.NONE


def check_process_liveness(pid: int) -> bool:
    """Check if a process is alive via kill -0."""
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def check_file_freshness(path: Path, soft: int, hard: int) -> HealthEvent | None:
    """Check file mtime against thresholds."""
    if not path or not path.exists():
        return None
    try:
        delta = time.time() - path.stat().st_mtime
    except OSError:
        return None

    target = path.stem
    if delta > hard:
        return HealthEvent(Severity.ERROR, "STALL", target,
                           f"no activity for {int(delta)}s (hard: {hard}s) — check network/proxy")
    if delta > soft:
        return HealthEvent(Severity.WARN, "STALL", target,
                           f"no activity for {int(delta)}s (soft: {soft}s) — may be thinking")
    return None


def format_event(event: HealthEvent) -> str:
    """Format event as human-readable line."""
    sev = event.severity.name.ljust(5)
    return f"[{sev}] {event.category} {event.target}: {event.message}"


def emit(event: HealthEvent, min_severity: Severity) -> bool:
    """Print event to stdout if severity meets threshold. Returns True if emitted."""
    if event.severity.value < min_severity.value:
        return False
    print(format_event(event), flush=True)
    return True
