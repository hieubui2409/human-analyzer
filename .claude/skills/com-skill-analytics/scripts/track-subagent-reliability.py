"""M3 — Subagent reliability tracker (deterministic, post-hoc forensics).

GOLDEN RULE #4: deterministic gather only. Classifies each subagent transcript's
final outcome (success / api_error / timeout / incomplete) by REUSING the
project-owned com:health-check core (classify_error, extract_error_text,
read_tail_jsonl_lines) — never reimplements error taxonomy. Aggregates success
rate + top failure modes per agent type. It surfaces reliability signal; the LLM
decides whether an agent type needs a different model/prompt. READ-ONLY.

Data source: ~/.claude/projects/{encoded-root}/**/subagents/agent-*.jsonl
(historical transcripts). Empty until subagents have run — degrades gracefully.

Usage:
  track-subagent-reliability.py [--days N] [--agent-type TYPE]
                                [--json] [--format md|json]

Env: CK_SESSIONS_DIR overrides session-root discovery (tests point it at tmp).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

# Reused project-owned health-check core (hyphenated filename → importlib load).
CORE = paths.SKILLS / "com-health-check" / "scripts" / "monitor-session-health-core.py"
_core_cache = None


def _core():
    global _core_cache
    if _core_cache is None:
        spec = importlib.util.spec_from_file_location("hc_core", CORE)
        _core_cache = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_core_cache)
    return _core_cache


def _sessions_dir() -> Path:
    env = os.environ.get("CK_SESSIONS_DIR")
    if env:
        return Path(env)
    return Path.home() / ".claude" / "projects" / str(paths.ROOT).replace("/", "-")


# Module-level, monkeypatchable in tests.
SESSIONS_DIR = _sessions_dir()


def _agent_type(path: Path) -> str:
    """Type = the alpha segments after 'agent-' up to the first id-like segment.

    Subagent files look like agent-{type}-{id}.jsonl; the id segment carries a
    digit (hex/uuid/index), so we keep leading pure-alpha tokens. This preserves
    hyphenated type names ('code-reviewer') while dropping the trailing id.
    """
    parts = path.stem.split("-")
    if parts and parts[0] == "agent":
        parts = parts[1:]
    type_parts = []
    for p in parts:
        if any(ch.isdigit() for ch in p):  # id-like segment → stop
            break
        type_parts.append(p)
    return "-".join(type_parts) or "unknown"


def classify_outcome(path: Path) -> tuple[str, str]:
    """Return (outcome, failure_mode). outcome in success|api_error|timeout|incomplete."""
    core = _core()
    lines = core.read_tail_jsonl_lines(path)
    if not lines:
        return "incomplete", ""
    last = lines[-1]
    msg = last.get("message", {}) if isinstance(last.get("message"), dict) else {}
    if msg.get("stop_reason") in ("end_turn", "stop_sequence"):
        if not any(isinstance(c, dict) and c.get("type") == "tool_use"
                   for c in msg.get("content", [])):
            return "success", ""
    err = core.classify_error(core.extract_error_text(last))
    if err in (core.ErrorClass.RETRYABLE, core.ErrorClass.NON_RETRYABLE):
        mode = " ".join(core.extract_error_text(last))[:60].strip()
        return "api_error", mode or err.value
    # No clean stop and no terminal error → process likely died/abandoned.
    return "timeout", ""


def gather(days: int, agent_type: str | None) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    by_type: dict[str, dict] = defaultdict(
        lambda: {"total": 0, "success": 0, "api_error": 0, "timeout": 0, "incomplete": 0})
    failure_modes: dict[str, int] = defaultdict(int)
    files = sorted(SESSIONS_DIR.glob("**/subagents/agent-*.jsonl")) if SESSIONS_DIR.exists() else []
    for f in files:
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        atype = _agent_type(f)
        if agent_type and atype != agent_type:
            continue
        outcome, mode = classify_outcome(f)
        agg = by_type[atype]
        agg["total"] += 1
        agg[outcome] += 1
        if mode:
            failure_modes[mode] += 1
    rows = []
    for atype, a in sorted(by_type.items(), key=lambda kv: -kv[1]["total"]):
        rows.append({
            "agent_type": atype, **a,
            "success_rate": round(100 * a["success"] / a["total"]) if a["total"] else 0,
        })
    return {
        "days": days,
        "total": sum(a["total"] for a in by_type.values()),
        "rows": rows,
        "top_failure_modes": sorted(failure_modes.items(), key=lambda kv: -kv[1])[:8],
    }


def render_md(data: dict) -> str:
    if data["total"] == 0:
        return ("# Subagent Reliability\n\n_No subagent transcripts yet — "
                "the tracker classifies them post-hoc as subagents run._")
    rows = [[r["agent_type"], str(r["total"]), f"{r['success_rate']}%",
             str(r["api_error"]), str(r["timeout"]), str(r["incomplete"])]
            for r in data["rows"]]
    out = [f"# Subagent Reliability (last {data['days']} days, N={data['total']})\n",
           markdown_table(["Agent Type", "Total", "Success", "API Err", "Timeout", "Incompl"], rows)]
    if data["top_failure_modes"]:
        out.append("\n**Top failure modes:** " +
                   ", ".join(f"{m} ({n})" for m, n in data["top_failure_modes"]))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Subagent reliability tracker (M3)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--agent-type", help="restrict to one agent type")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    data = gather(args.days, args.agent_type)
    print(json_output(data) if (args.json or args.format == "json") else render_md(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
