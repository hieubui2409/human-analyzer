"""P1 — Session JSONL forensics parser (deterministic, streaming).

GOLDEN RULE #4: deterministic gather only. Reconstructs a Claude Code session
from its transcript JSONL with zero instrumentation — skills invoked, tool-call
counts, token usage (input/output/cache), files touched, subagent spawns, and
duration. Streams line-by-line so 50MB+ transcripts never load whole into memory.
It surfaces the activity timeline; the LLM interprets it. READ-ONLY.

Usage:
  parse-session-jsonl-forensics.py [--session ID | --all-sessions]
                                   [--since YYYY-MM-DD] [--tool-breakdown]
                                   [--json] [--format md|json]

Env: CK_SESSIONS_DIR overrides session discovery (tests point it at a tmp dir).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402
from platform_lib.errors import emit_error  # noqa: E402


def _sessions_dir() -> Path:
    env = os.environ.get("CK_SESSIONS_DIR")
    if env:
        return Path(env)
    return Path.home() / ".claude" / "projects" / str(paths.ROOT).replace("/", "-")


# Module-level, monkeypatchable in tests.
SESSIONS_DIR = _sessions_dir()
_TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens")


def _parse_ts(raw: str):
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def parse_session(path: Path) -> dict:
    """Stream one transcript; never holds the whole file in memory."""
    tools: dict[str, int] = defaultdict(int)
    skills: list[str] = []
    files: set[str] = set()
    subagents = 0
    tokens = {k: 0 for k in _TOKEN_KEYS}
    first_ts = last_ts = None
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return {}
    with fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = _parse_ts(rec.get("timestamp", "")) or _parse_ts(
                (rec.get("message") or {}).get("timestamp", "") if isinstance(rec.get("message"), dict) else "")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if isinstance(usage, dict):
                for k in _TOKEN_KEYS:
                    tokens[k] += int(usage.get(k, 0) or 0)
            for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                    continue
                name = b.get("name", "?")
                tools[name] += 1
                inp = b.get("input") or {}
                if name == "Skill":
                    skills.append(inp.get("skill", "?"))
                elif name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                    if inp.get("file_path"):
                        files.add(inp["file_path"])
                elif name in ("Task", "Agent"):
                    subagents += 1
    dur = int((last_ts - first_ts).total_seconds()) if first_ts and last_ts else 0
    return {
        "session": path.stem,
        "skills": skills,
        "tool_counts": dict(sorted(tools.items(), key=lambda kv: -kv[1])),
        "tool_calls": sum(tools.values()),
        "files_modified": sorted(files),
        "subagents": subagents,
        "tokens": tokens,
        "total_tokens": tokens["input_tokens"] + tokens["output_tokens"],
        "duration_s": dur,
        "last_ts": last_ts.date().isoformat() if last_ts else None,
    }


def gather(session: str | None, all_sessions: bool, since: date | None) -> dict:
    if not SESSIONS_DIR.exists():
        return {"sessions": [], "count": 0}
    if session:
        files = [SESSIONS_DIR / f"{session}.jsonl"]
    else:
        files = sorted(SESSIONS_DIR.glob("*.jsonl"))
        if not all_sessions:
            files = files[-1:]  # default: most recent session only
    parsed = []
    for f in files:
        if not f.exists():
            continue
        p = parse_session(f)
        if not p:
            continue
        if since and p["last_ts"] and date.fromisoformat(p["last_ts"]) < since:
            continue
        parsed.append(p)
    agg_tokens = sum(p["total_tokens"] for p in parsed)
    agg_tools: dict[str, int] = defaultdict(int)
    for p in parsed:
        for t, c in p["tool_counts"].items():
            agg_tools[t] += c
    return {
        "count": len(parsed),
        "sessions": parsed,
        "agg_total_tokens": agg_tokens,
        "agg_tool_counts": dict(sorted(agg_tools.items(), key=lambda kv: -kv[1])),
    }


def _fmt_tok(n: int) -> str:
    return f"{n / 1_000_000:.1f}M" if n >= 1_000_000 else (f"{n / 1_000:.0f}K" if n >= 1000 else str(n))


def render_md(data: dict, tool_breakdown: bool) -> str:
    if data["count"] == 0:
        return "# Session Forensics\n\n_No session transcripts found._"
    rows = [[p["session"][:8], str(len(p["skills"])), str(p["tool_calls"]),
             str(p["subagents"]), _fmt_tok(p["total_tokens"]),
             f"{p['duration_s'] // 60}m", str(len(p["files_modified"]))]
            for p in data["sessions"]]
    out = [f"# Session Forensics ({data['count']} session(s), "
           f"{_fmt_tok(data['agg_total_tokens'])} tokens)\n",
           markdown_table(["Session", "Skills", "Tools", "Subagents", "Tokens", "Dur", "Files"], rows)]
    if tool_breakdown and data["agg_tool_counts"]:
        trows = [[t, str(c)] for t, c in data["agg_tool_counts"].items()]
        out += ["\n## Tool breakdown\n", markdown_table(["Tool", "Calls"], trows)]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Session JSONL forensics parser (P1)")
    ap.add_argument("--session", help="parse one session by id")
    ap.add_argument("--all-sessions", action="store_true", help="aggregate across all sessions")
    ap.add_argument("--since", help="only sessions on/after YYYY-MM-DD")
    ap.add_argument("--tool-breakdown", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    since = None
    if args.since:
        try:
            since = date.fromisoformat(args.since)
        except ValueError:
            emit_error("validation", f"bad --since: {args.since!r}")
            print(f"error: --since must be YYYY-MM-DD, got {args.since!r}", file=sys.stderr)
            return 2
    data = gather(args.session, args.all_sessions, since)
    print(json_output(data) if (args.json or args.format == "json")
          else render_md(data, args.tool_breakdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
