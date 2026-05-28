"""P4 — Skill interaction (cascade/trigger) topology from SKILL.md text.

GOLDEN RULE #4: deterministic gather. Extracts framework-event references
(`FW.verb`) and arrow chains (`A.x → B.y`) declared in each SKILL.md, then maps
skill → events and the global event-chain edges. Reports orphan skills (no event
wiring) and hub skills (most event references). Distinct from orc:audit, which
checks event *consistency*; this maps *topology*. READ-ONLY.

Usage:
  build-cascade-graph.py [--json] [--dot] [--orphans]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.markdown_parser import extract_frontmatter  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

SKILLS_DIR = paths.ROOT / ".claude" / "skills"
FRAMEWORKS = ["MAT", "PSY", "CRE", "GRO", "ORC", "COM"]
EVENT = re.compile(r"\b(" + "|".join(FRAMEWORKS) + r")\.([a-z][a-z_]+)\b")
# Arrow chains like "MAT.integrated → PSY.refresh → CRE.recalibrate"
ARROW = re.compile(r"([A-Z]{3}\.[a-z_]+)\s*(?:→|->)\s*([A-Z]{3}\.[a-z_]+)")


def _skill_dirs():
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and d.name.split("-", 1)[0] in [f.lower() for f in FRAMEWORKS] \
                and (d / "SKILL.md").exists():
            yield d


def gather() -> dict:
    skill_events: dict[str, list[str]] = {}
    chain_edges: set[tuple[str, str]] = set()
    for d in _skill_dirs():
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        fm = extract_frontmatter(d / "SKILL.md")
        skill_id = fm.get("name", d.name)
        events = sorted({f"{m.group(1)}.{m.group(2)}" for m in EVENT.finditer(text)})
        skill_events[skill_id] = events
        for a, b in ARROW.findall(text):
            chain_edges.add((a, b))
    orphans = sorted([s for s, e in skill_events.items() if not e])
    hubs = sorted(skill_events.items(), key=lambda kv: -len(kv[1]))[:8]
    return {
        "skill_events": dict(sorted(skill_events.items())),
        "chain_edges": sorted(chain_edges),
        "orphans": orphans,
        "hubs": [{"skill": s, "events": len(e)} for s, e in hubs if e],
        "skill_count": len(skill_events),
    }


def render_dot(data: dict) -> str:
    lines = ["digraph cascade {", "  rankdir=LR;", "  node [shape=ellipse];"]
    for a, b in data["chain_edges"]:
        lines.append(f'  "{a}" -> "{b}";')
    lines.append("}")
    return "\n".join(lines)


def render_md(data: dict) -> str:
    out = [f"# Skill Cascade Topology ({data['skill_count']} skills)\n",
           "## Event chains (declared arrows)\n"]
    out += [f"- `{a}` → `{b}`" for a, b in data["chain_edges"]] or ["(none)"]
    out.append("\n## Hub skills (most event references)\n")
    out.append(markdown_table(["Skill", "Events"],
                              [[h["skill"], str(h["events"])] for h in data["hubs"]]))
    out.append(f"\n**Orphan skills (no event wiring):** {len(data['orphans'])}")
    if data["orphans"]:
        out.append(", ".join(data["orphans"]))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill interaction/cascade topology (P4)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dot", action="store_true")
    ap.add_argument("--orphans", action="store_true", help="only list disconnected skills")
    args = ap.parse_args()
    data = gather()
    if args.orphans:
        print(json_output({"orphans": data["orphans"]}) if args.json else "\n".join(data["orphans"]))
    elif args.dot:
        print(render_dot(data))
    elif args.json:
        print(json_output(data))
    else:
        print(render_md(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
