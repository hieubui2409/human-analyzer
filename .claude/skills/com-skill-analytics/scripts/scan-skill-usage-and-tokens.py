"""S1 — Skill usage analytics + token attribution (deterministic gather).

GOLDEN RULE #4: deterministic gather only. Counts framework-skill invocations from
the consolidated sink (.claude/telemetry/invocations.jsonl, written by the I1 hook)
and, with --tokens, attributes per-skill token spend by walking the project's
Claude Code session JSONL. It NEVER judges whether usage is "good" — it surfaces
counts, never-used skills, and token weight for the LLM to adjudicate. READ-ONLY.

Token attribution model: walk a session transcript chronologically; a Skill
tool_use opens a span credited to that skill; sum assistant `message.usage` of
that and following assistant turns until the next Skill tool_use. Approximate
(spans include reasoning between skills) — directional, not billing-exact.

Usage:
  scan-skill-usage-and-tokens.py [--days N] [--tokens] [--framework FW]
                                 [--top N] [--json] [--format md|json]

Env: CK_SESSIONS_DIR overrides session-JSONL discovery (tests point it at a tmp dir).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

FRAMEWORKS = ["mat", "psy", "cre", "gro", "orc", "com"]
# Module-level, monkeypatchable in tests (point at a tmp fixture tree).
INVOCATIONS = paths.TELEMETRY / "invocations.jsonl"
SKILLS_DIR = paths.SKILLS


def _framework_of(skill: str) -> str:
    return skill.split("-", 1)[0].split(":", 1)[0]


def all_framework_skills() -> set[str]:
    """Catalog of project-owned framework skills as dir-name ids (e.g. 'com-git')."""
    out = set()
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and _framework_of(d.name) in FRAMEWORKS and (d / "SKILL.md").exists():
            out.add(d.name)
    return out


def _parse_ts(rec: dict) -> datetime | None:
    raw = rec.get("ts", "")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def gather_invocations(days: int, framework: str | None) -> dict:
    counts: dict[str, int] = defaultdict(int)
    by_day: dict[str, int] = defaultdict(int)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if INVOCATIONS.exists():
        for line in INVOCATIONS.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            skill = rec.get("skill", "").replace(":", "-")
            if not skill:
                continue
            ts = _parse_ts(rec)
            if ts and ts < cutoff:
                continue
            if framework and _framework_of(skill) != framework:
                continue
            counts[skill] += 1
            if ts:
                by_day[ts.date().isoformat()] += 1
    return {"counts": dict(counts), "by_day": dict(sorted(by_day.items()))}


def _sessions_dir() -> Path:
    env = os.environ.get("CK_SESSIONS_DIR")
    if env:
        return Path(env)
    # Claude Code encodes the project path by replacing every '/' with '-'.
    enc = str(paths.ROOT).replace("/", "-")
    return Path.home() / ".claude" / "projects" / enc


def gather_tokens() -> dict[str, int]:
    """Per-skill token attribution across all session transcripts (best-effort)."""
    sdir = _sessions_dir()
    tokens: dict[str, int] = defaultdict(int)
    if not sdir.exists():
        return {}
    for sf in sorted(sdir.glob("*.jsonl")):
        current: str | None = None
        try:
            fh = sf.open(encoding="utf-8")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content")
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
                            sk = (b.get("input") or {}).get("skill", "")
                            if sk:
                                current = sk.replace(":", "-")
                usage = msg.get("usage")
                if current and isinstance(usage, dict):
                    tokens[current] += int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))
    return dict(tokens)


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def gather(days: int, framework: str | None, with_tokens: bool) -> dict:
    inv = gather_invocations(days, framework)
    counts = inv["counts"]
    catalog = all_framework_skills()
    if framework:
        catalog = {s for s in catalog if _framework_of(s) == framework}
    tokens = gather_tokens() if with_tokens else {}
    never_used = sorted(s for s in catalog if s not in counts)
    rows = []
    for skill in catalog | set(counts):
        rows.append({
            "skill": skill,
            "count": counts.get(skill, 0),
            "tokens": tokens.get(skill, 0),
            "framework": _framework_of(skill).upper(),
        })
    rows.sort(key=lambda r: (-r["count"], -r["tokens"], r["skill"]))
    return {
        "days": days,
        "total_invocations": sum(counts.values()),
        "skills_used": len([c for c in counts.values() if c]),
        "never_used": never_used,
        "by_day": inv["by_day"],
        "with_tokens": with_tokens,
        "rows": rows,
    }


def render_md(data: dict, top: int | None) -> str:
    if data["total_invocations"] == 0 and not any(r["tokens"] for r in data["rows"]):
        return (f"# Skill Usage (last {data['days']} days)\n\n"
                "_No invocation data yet — the I1 hook records skills as they run._\n\n"
                f"Never used (full catalog): {len(data['never_used'])} skills.")
    rows = [r for r in data["rows"] if r["count"] or r["tokens"]]
    if top:
        rows = rows[:top]
    headers = ["#", "Skill", "Count", "Framework"]
    if data["with_tokens"]:
        headers.insert(3, "Tokens")
    table_rows = []
    for i, r in enumerate(rows, 1):
        row = [str(i), r["skill"], str(r["count"]), r["framework"]]
        if data["with_tokens"]:
            row.insert(3, _fmt_tokens(r["tokens"]))
        table_rows.append(row)
    out = [f"# Skill Usage (last {data['days']} days)\n",
           f"Total invocations: **{data['total_invocations']}** across "
           f"**{data['skills_used']}** skills.\n",
           markdown_table(headers, table_rows)]
    out.append(f"\n**Never used (last {data['days']} days):** {len(data['never_used'])}")
    if data["never_used"]:
        out.append(", ".join(data["never_used"]))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill usage analytics + token attribution (S1)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--tokens", action="store_true", help="attribute tokens from session JSONL")
    ap.add_argument("--framework", choices=FRAMEWORKS)
    ap.add_argument("--top", type=int, help="limit table to top N skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    data = gather(args.days, args.framework, args.tokens)
    if args.json or args.format == "json":
        print(json_output(data))
    else:
        print(render_md(data, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
