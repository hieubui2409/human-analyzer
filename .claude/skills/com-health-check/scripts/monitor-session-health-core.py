"""Core types, constants, and primitive detection functions for session health monitoring.

Layers: process liveness, file freshness, content inspection, error classification.
"""
import json
import os
import time
from dataclasses import dataclass, field
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

INTERACTIVE_TOOLS = {"AskUserQuestion"}


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
    checks: str = "all"
    seen_errors: set = field(default_factory=set)
    wait_detected_ts: float = 0.0
    last_heartbeat_ts: float = 0.0
    heartbeat_interval: int = 3600


def resolve_project_slug(cwd: str | None = None) -> str:
    """Convert CWD to Claude Code project slug (keeps leading dash)."""
    return (cwd or os.getcwd()).replace("/", "-")


def _read_tail_chunk(path: Path, tail_bytes: int) -> str | None:
    """Read tail_bytes from end of file, return decoded string or None."""
    try:
        size = path.stat().st_size
        if size == 0:
            return None
        with open(path, "rb") as f:
            read_size = min(tail_bytes, size)
            f.seek(max(0, size - read_size))
            return f.read().decode("utf-8", errors="replace")
    except OSError:
        return None


_TAIL_SIZES = [8192, 32768, 131072]


def read_last_jsonl_line(path: Path) -> dict | None:
    """Read last complete JSON line. Progressively reads more if lines are large."""
    if not path or not path.exists():
        return None
    for sz in _TAIL_SIZES:
        chunk = _read_tail_chunk(path, sz)
        if chunk is None:
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


def read_tail_jsonl_lines(path: Path) -> list[dict]:
    """Read all complete JSON lines from file tail. Progressively reads more if needed."""
    if not path or not path.exists():
        return []
    for sz in _TAIL_SIZES:
        chunk = _read_tail_chunk(path, sz)
        if chunk is None:
            return []
        results = []
        for line in chunk.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if results:
            return results
    return []


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


def is_waiting_for_user(path: Path) -> bool:
    """Detect if LLM finished work and is waiting for user input.

    True when last JSONL entry shows AskUserQuestion pending or clean end_turn.
    """
    last = read_last_jsonl_line(path)
    if not last:
        return False
    msg = last.get("message", {})
    if not isinstance(msg, dict):
        return False
    sr = msg.get("stop_reason", "")
    content = msg.get("content", [])

    if sr == "tool_use":
        for c in content:
            if (isinstance(c, dict) and c.get("type") == "tool_use"
                    and c.get("name") in INTERACTIVE_TOOLS):
                return True

    if sr == "end_turn":
        has_tool = any(
            isinstance(c, dict) and c.get("type") == "tool_use"
            for c in content
        )
        if not has_tool:
            return True

    return False


def check_session_alive(session_id: str) -> bool | None:
    """Check if a session's parent process is alive via ~/.claude/sessions/*.json.

    Returns True if alive, False if dead, None if no session file found.
    """
    sessions_dir = Path.home() / ".claude" / "sessions"
    if not sessions_dir.exists():
        return None
    for pf in sessions_dir.glob("*.json"):
        try:
            data = json.loads(pf.read_text())
            if data.get("sessionId") == session_id:
                pid = data.get("pid")
                return check_process_liveness(pid) if pid else None
        except (json.JSONDecodeError, OSError):
            continue
    return None


def is_subagent_completed(path: Path, hard_threshold: int) -> bool:
    """Detect completed/abandoned subagent via 2 signals. Requires stale > hard_threshold first.

    Signal 1 (clean exit): last message has stop_reason in (end_turn, stop_sequence) with no pending tool_use.
    Signal 2 (error exit): last JSONL entries contain API error patterns — subagent crashed.
    """
    if not path or not path.exists():
        return False
    try:
        delta = time.time() - path.stat().st_mtime
    except OSError:
        return False
    if delta <= hard_threshold:
        return False

    lines = read_tail_jsonl_lines(path)
    if not lines:
        return False

    # Signal 1: clean completion — last assistant message ended cleanly
    last = lines[-1]
    msg = last.get("message", {})
    if isinstance(msg, dict) and msg.get("stop_reason") in ("end_turn", "stop_sequence"):
        content = msg.get("content", [])
        has_pending_tool = any(
            isinstance(c, dict) and c.get("type") == "tool_use"
            for c in content
        )
        if not has_pending_tool:
            return True

    # Signal 2: error exit — LAST line contains API error (not any line in tail,
    # because earlier errors may have been retried successfully)
    texts = extract_error_text(last)
    err_class = classify_error(texts)
    if err_class in (ErrorClass.RETRYABLE, ErrorClass.NON_RETRYABLE):
        return True

    return False


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
