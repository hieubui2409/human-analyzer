#!/usr/bin/env python3
"""CLI wrapper for Claude Code session health monitor.

Polls session JSONL files and outputs health notifications to stdout
for consumption by Claude's Monitor tool.
"""
import argparse
import importlib.util
import os
import signal
import sys
import time
from pathlib import Path

_scripts_dir = Path(__file__).parent


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, _scripts_dir / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_core = _load_module("_core", "monitor-session-health-core.py")
_targets = _load_module("_targets", "monitor-session-health-targets.py")

MonitorConfig = _core.MonitorConfig
Severity = _core.Severity
VERBOSITY_MAP = _core.VERBOSITY_MAP
emit = _core.emit
resolve_session_paths = _targets.resolve_session_paths
check_main_agent = _targets.check_main_agent
check_subagents = _targets.check_subagents
check_team_agents = _targets.check_team_agents

SHUTDOWN = False


def handle_signal(signum, frame):
    global SHUTDOWN
    SHUTDOWN = True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor Claude Code session health")
    p.add_argument("--target", choices=["main", "subagent", "team", "all"], default="main")
    p.add_argument("--soft", type=int, default=120, help="Soft stall threshold (seconds)")
    p.add_argument("--hard", type=int, default=300, help="Hard stall threshold (seconds)")
    p.add_argument("--verbosity", choices=["error", "warn", "info", "debug"], default="warn")
    p.add_argument("--include-429", action="store_true", help="Report 429/rate limit as time-retryable")
    p.add_argument("--poll", type=int, default=30, help="Poll interval (seconds)")
    p.add_argument("--session-id", help="Explicit session UUID (auto-detect if omitted)")
    p.add_argument("--team-name", help="Team name for team monitoring")
    p.add_argument("--cwd", help="Override CWD for project slug resolution")
    return p.parse_args()


import re


def _sanitize_id(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)


def create_lockfile(session_id: str, target: str) -> Path:
    """Create PID lockfile atomically. Raises SystemExit if another monitor is active."""
    lock = Path(f"/tmp/claude-health-{_sanitize_id(session_id)}-{_sanitize_id(target)}.lock")
    if lock.exists():
        try:
            existing_pid = int(lock.read_text().strip())
            try:
                os.kill(existing_pid, 0)
                print(f"[ERROR] Another monitor (PID {existing_pid}) is already running for this session+target",
                      flush=True)
                sys.exit(1)
            except ProcessLookupError:
                pass
            except PermissionError:
                print(f"[ERROR] Another monitor (PID {existing_pid}) is already running", flush=True)
                sys.exit(1)
        except (ValueError, OSError):
            pass

    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except OSError:
        lock.write_text(str(os.getpid()))
    return lock


def remove_lockfile(lock: Path):
    try:
        lock.unlink(missing_ok=True)
    except OSError:
        pass


def main():
    args = parse_args()

    config = MonitorConfig(
        soft_threshold=args.soft,
        hard_threshold=args.hard,
        include_429=args.include_429,
        verbosity=VERBOSITY_MAP[args.verbosity],
        poll_interval=args.poll,
        team_name=args.team_name or "",
    )

    sp = resolve_session_paths(session_id=args.session_id, cwd=args.cwd)
    if not sp.jsonl and args.target in ("main", "all"):
        print("[WARN] No session JSONL found — waiting for session to start", flush=True)

    lock = create_lockfile(sp.session_id or "unknown", args.target)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while not SHUTDOWN:
            if args.target in ("subagent", "all", "team"):
                sp = resolve_session_paths(session_id=args.session_id, cwd=args.cwd)

            events = []
            if args.target in ("main", "all"):
                events.extend(check_main_agent(sp, config))
            if args.target in ("subagent", "all"):
                events.extend(check_subagents(sp, config))
            if args.target in ("team", "all"):
                events.extend(check_team_agents(sp, config))

            for ev in events:
                emit(ev, config.verbosity)

            time.sleep(config.poll_interval)
    finally:
        remove_lockfile(lock)


if __name__ == "__main__":
    main()
