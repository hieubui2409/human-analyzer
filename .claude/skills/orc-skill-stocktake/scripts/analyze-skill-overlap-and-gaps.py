"""Full Stocktake gather — overlap candidates + usage signal (C3).

GOLDEN RULE #4: deterministic OVER-GATHER only. Computes pairwise description/trigger
token overlap (Jaccard) and a usage signal (event-log mentions + git recency) per skill.
It DOES NOT decide duplicate-vs-complementary or keep/retire — that is the LLM's job
(the 260523 audit proved "complementary ≠ duplicate"). Emits candidate pairs + usage for
LLM adjudication. READ-ONLY.

Red-team R-cross: a freshly-created skill has no event history yet — "no usage" must NOT
read as "unused". New skills (few git commits / recent first commit) are tagged NEW and
their usage signal is flagged not-meaningful so they are never recommended for retirement.

Usage:
  analyze-skill-overlap-and-gaps.py [--min-overlap 0.30] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.markdown_parser import extract_frontmatter
from platform_lib import paths

SKILLS_DIR = paths.ROOT / ".claude" / "skills"
FRAMEWORKS = ["orc", "psy", "cre", "gro", "mat", "com"]

_STOP = {"the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with", "use",
         "when", "via", "vs", "from", "by", "is", "are", "be", "this", "that", "it",
         "skill", "content", "character", "profile", "framework", "triggers", "across"}
_TOKEN = re.compile(r"[a-z][a-z0-9-]{2,}")

# A skill with fewer than this many commits touching it is treated as NEW.
_NEW_SKILL_COMMIT_THRESHOLD = 3


def _prefix(name: str) -> str | None:
    p = name.split("-", 1)[0]
    return p if p in FRAMEWORKS else None


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP}


def _git_commit_count(skill_dir: Path) -> int:
    try:
        r = subprocess.run(["git", "-C", str(paths.ROOT), "log", "--oneline", "--",
                            str(skill_dir.relative_to(paths.ROOT))],
                           capture_output=True, text=True, timeout=15)
        return len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception:
        return 0


def _event_log_mentions(skill_name: str) -> int:
    """Count references to this skill as an event `source` across telemetry event streams.

    Reads the canonical TELEMETRY event sinks (paths.EVENT_STREAMS + invocations.jsonl),
    NOT session-state/ which holds mutable JSON state — not JSONL event logs.
    """
    if skill_name is None:
        return 0
    # Gather all real JSONL sinks: framework partitions + invocations (written by I1 hook).
    sinks = list(paths.EVENT_STREAMS.values()) + [paths.TELEMETRY / "invocations.jsonl"]
    n = 0
    for jl in sinks:
        if not jl.exists():
            continue
        try:
            n += sum(1 for line in jl.read_text(encoding="utf-8").splitlines()
                     if skill_name in line)
        except Exception:
            continue
    return n


def gather() -> dict:
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir() or _prefix(d.name) is None:
            continue
        sk = d / "SKILL.md"
        if not sk.exists():
            continue
        fm = extract_frontmatter(sk)
        name = fm.get("name") or d.name
        desc = fm.get("description", "")
        commits = _git_commit_count(d)
        skills.append({
            "name": name, "framework": _prefix(d.name), "dir": d.name,
            "tokens": _tokens(desc), "desc": desc[:120],
            "commits": commits,
            "is_new": commits < _NEW_SKILL_COMMIT_THRESHOLD,
            "event_mentions": _event_log_mentions(name),
        })
    return {"skills": skills}


def overlap_pairs(skills: list[dict], min_overlap: float) -> list[dict]:
    pairs = []
    for a, b in combinations(skills, 2):
        ta, tb = a["tokens"], b["tokens"]
        if not ta or not tb:
            continue
        jac = len(ta & tb) / len(ta | tb)
        if jac >= min_overlap:
            pairs.append({
                "a": a["name"], "b": b["name"],
                "same_framework": a["framework"] == b["framework"],
                "jaccard": round(jac, 3),
                "shared_terms": sorted(ta & tb)[:12],
                "note": "candidate only — LLM judges duplicate vs complementary",
            })
    return sorted(pairs, key=lambda p: -p["jaccard"])


def usage_table(skills: list[dict]) -> list[dict]:
    out = []
    for s in skills:
        out.append({
            "name": s["name"], "commits": s["commits"],
            "event_mentions": s["event_mentions"],
            "is_new": s["is_new"],
            "usage_signal": ("not-meaningful (NEW skill)" if s["is_new"]
                             else ("active" if s["event_mentions"] > 0 else "low")),
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="Full Stocktake overlap + usage gather (READ-ONLY).")
    ap.add_argument("--min-overlap", type=float, default=0.30,
                    help="Min Jaccard to flag a candidate pair (default 0.30)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = gather()
    skills = data["skills"]
    pairs = overlap_pairs(skills, args.min_overlap)
    usage = usage_table(skills)

    out = {"skill_count": len(skills), "overlap_candidates": pairs, "usage": usage}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print(f"\nFull Stocktake — {len(skills)} skills, {len(pairs)} overlap candidate(s) "
          f"(Jaccard ≥ {args.min_overlap})\n")
    for p in pairs:
        tag = "same-fw" if p["same_framework"] else "cross-fw"
        print(f"  [{p['jaccard']:.2f}] {tag}  {p['a']} ~ {p['b']}")
        print(f"          shared: {', '.join(p['shared_terms'])}")
    new = [u["name"] for u in usage if u["is_new"]]
    if new:
        print(f"\n  NEW skills (usage signal NOT used for retire): {', '.join(new)}")
    print("\n  → LLM adjudicates each pair: duplicate (CONSOLIDATE) vs complementary (KEEP).")


if __name__ == "__main__":
    main()
