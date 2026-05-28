"""S5 — Workflow chain analyzer (deterministic gather).

GOLDEN RULE #4: deterministic gather only. Reconstructs the actual per-session
skill chain from the I1 invocation sink (group by session, order by ts), ranks the
most common chains, and compares them against the chains DECLARED in the routing
rule docs to flag deviations. It surfaces actual-vs-recommended drift; the LLM
decides whether a deviation is a healthy shortcut or a missed step. READ-ONLY.

Needs enough invocation history to be meaningful — degrades gracefully when the
sink is thin (reports observed chains, skips deviation verdicts below min N).

Usage:
  analyze-workflow-chains.py [--days N] [--top N] [--min-sessions N]
                             [--json] [--format md|json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

# Module-level, monkeypatchable in tests.
INVOCATIONS = paths.TELEMETRY / "invocations.jsonl"
ROUTING_DOCS = [
    paths.ROOT / ".claude" / "rules" / "skill-workflow-routing.md",
    paths.ROOT / ".claude" / "rules" / "skill-domain-routing.md",
]
# A declared chain in the routing docs: "/ck:plan → /ck:cook → /ck:test".
CHAIN_RE = re.compile(r"(/?[a-z]+:[a-z-]+(?:\s*→\s*/?[a-z]+:[a-z-]+)+)")


def _parse_ts(raw: str):
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def actual_chains(days: int) -> list[list[str]]:
    """Per-session ordered skill sequences from the invocation sink."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    by_session: dict[str, list[tuple]] = defaultdict(list)
    if INVOCATIONS.exists():
        for line in INVOCATIONS.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            skill = rec.get("skill", "").replace("-", ":", 1)
            sess = rec.get("session", "")
            ts = _parse_ts(rec.get("ts", ""))
            if not skill or not sess or (ts and ts < cutoff):
                continue
            by_session[sess].append((ts or datetime.min.replace(tzinfo=timezone.utc), skill))
    chains = []
    for sess, items in by_session.items():
        items.sort(key=lambda x: x[0])
        chains.append([s for _, s in items])
    return chains


def declared_chains() -> list[list[str]]:
    out = []
    for doc in ROUTING_DOCS:
        if not doc.exists():
            continue
        for m in CHAIN_RE.findall(doc.read_text(encoding="utf-8")):
            steps = [s.strip().lstrip("/") for s in m.split("→")]
            if len(steps) >= 2:
                out.append(steps)
    return out


def _norm(chain: list[str]) -> str:
    return " → ".join(chain)


def gather(days: int, top: int, min_sessions: int) -> dict:
    actual = actual_chains(days)
    declared = declared_chains()
    declared_set = {_norm(c) for c in declared}
    chain_freq = Counter(_norm(c) for c in actual if c)
    common = chain_freq.most_common(top)
    # Deviations: an observed multi-step chain matching no declared chain.
    deviations = [(c, n) for c, n in chain_freq.items()
                  if " → " in c and c not in declared_set]
    deviations.sort(key=lambda x: -x[1])
    return {
        "days": days,
        "sessions_analyzed": len(actual),
        "sufficient": len(actual) >= min_sessions,
        "min_sessions": min_sessions,
        "common_chains": [{"chain": c, "count": n} for c, n in common],
        "declared_chains": [_norm(c) for c in declared],
        "deviations": [{"chain": c, "count": n} for c, n in deviations[:top]],
    }


def render_md(data: dict) -> str:
    out = [f"# Workflow Chains (last {data['days']} days, "
           f"{data['sessions_analyzed']} sessions)\n"]
    if not data["sufficient"]:
        out.append(f"_Thin data: {data['sessions_analyzed']} < min {data['min_sessions']} "
                   "sessions — observed chains shown, deviation verdicts withheld._\n")
    if data["common_chains"]:
        rows = [[c["chain"], str(c["count"])] for c in data["common_chains"]]
        out += ["## Most common actual chains\n", markdown_table(["Chain", "Count"], rows)]
    else:
        out.append("_No multi-skill chains observed yet._")
    if data["sufficient"] and data["deviations"]:
        rows = [[d["chain"], str(d["count"])] for d in data["deviations"]]
        out += ["\n## Deviations from routing docs\n", markdown_table(["Chain", "Count"], rows)]
    out.append(f"\n**Declared chains in routing docs:** {len(data['declared_chains'])}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Workflow chain analyzer (S5)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-sessions", type=int, default=5,
                    help="min sessions before emitting deviation verdicts")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    data = gather(args.days, args.top, args.min_sessions)
    print(json_output(data) if (args.json or args.format == "json") else render_md(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
