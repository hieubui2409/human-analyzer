"""S4 — Skill coverage, trigger-overlap + SKILL.md context budget (deterministic).

GOLDEN RULE #4: deterministic gather only. Across project-owned framework skills it
(1) measures each SKILL.md context budget (tokens ≈ chars/4), (2) detects trigger
keyword overlap between skills, (3) cross-references the two routing docs to flag
skills undocumented in routing, and (4) with --decommission lists never-used skills
(joined against invocations.jsonl). It surfaces candidates; the LLM decides. READ-ONLY.

Usage:
  analyze-skill-coverage-and-budget.py [--budget-only] [--gaps-only]
                                       [--decommission] [--json] [--format md|json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.markdown_parser import extract_frontmatter  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402
from platform_lib.skill_ids import to_dir_id  # noqa: E402

FRAMEWORKS = ["mat", "psy", "cre", "gro", "orc", "com"]
# Where framework skills are actually cataloged. The two skill-*-routing.md rule
# files only route ck:* utility skills, so framework skills live in CLAUDE.md's
# Skills Catalog + docs/MODULES.md — a skill absent from ALL of these is a real gap.
ROUTING_DOCS = [
    paths.ROOT / "CLAUDE.md",
    paths.ROOT / "docs" / "MODULES.md",
    paths.ROOT / ".claude" / "rules" / "skill-workflow-routing.md",
    paths.ROOT / ".claude" / "rules" / "skill-domain-routing.md",
]
INVOCATIONS = paths.TELEMETRY / "invocations.jsonl"
SKILLS_DIR = paths.SKILLS  # module-level, monkeypatchable in tests
BUDGET_WARN_TOKENS = 2000  # SKILL.md heavier than this is flagged for review
# Generic words excluded from trigger-overlap signal (too common to discriminate).
# Two tiers: English function words + project-structural boilerplate that appears
# in nearly every SKILL.md (triggers/framework/character/...) and would bury signal.
STOPWORDS = set("""the a an and or for to of in on with from into per via use using
when user wants this that skill agent task work file files code create build add
purpose then your you it is are be new across over each only not
triggers trigger framework frameworks character characters check checks profile
profiles content analysis cross data report reports event events skills domain
generate scan audit update across detect""".split())
KEYWORD = re.compile(r"[a-z][a-z-]{3,}")


def _framework_of(name: str) -> str:
    return name.split("-", 1)[0]


def _est_tokens(text: str) -> int:
    return round(len(text) / 4)


def _keywords(text: str) -> set[str]:
    return {w for w in KEYWORD.findall(text.lower()) if w not in STOPWORDS}


def gather_skills() -> list[dict]:
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not (d.is_dir() and _framework_of(d.name) in FRAMEWORKS):
            continue
        md = d / "SKILL.md"
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        fm = extract_frontmatter(md)
        desc = fm.get("description", "")
        subcommands = sorted(set(re.findall(r"(?<![\w-])--[a-z][a-z-]+", text)))
        skills.append({
            "skill": d.name,
            "framework": _framework_of(d.name).upper(),
            "tokens": _est_tokens(text),
            "desc_keywords": sorted(_keywords(desc)),
            "subcommands": subcommands,
        })
    return skills


def trigger_overlaps(skills: list[dict]) -> list[dict]:
    """Keywords appearing in >1 skill description — potential routing ambiguity."""
    kw_to_skills: dict[str, list[str]] = defaultdict(list)
    for s in skills:
        for kw in s["desc_keywords"]:
            kw_to_skills[kw].append(s["skill"])
    overlaps = [{"keyword": k, "skills": sorted(v)}
                for k, v in kw_to_skills.items() if len(v) > 1]
    overlaps.sort(key=lambda o: (-len(o["skills"]), o["keyword"]))
    return overlaps


def routing_gaps(skills: list[dict]) -> list[str]:
    corpus = ""
    for doc in ROUTING_DOCS:
        if doc.exists():
            corpus += doc.read_text(encoding="utf-8")
    missing = []
    for s in skills:
        colon_id = s["skill"].replace("-", ":", 1)
        if s["skill"] not in corpus and colon_id not in corpus:
            missing.append(s["skill"])
    return sorted(missing)


def never_used(skills: list[dict]) -> list[str]:
    used = set()
    if INVOCATIONS.exists():
        for line in INVOCATIONS.read_text(encoding="utf-8").splitlines():
            try:
                used.add(to_dir_id(json.loads(line).get("skill", "")))
            except json.JSONDecodeError:
                continue
    return sorted(s["skill"] for s in skills if s["skill"] not in used)


def gather() -> dict:
    skills = gather_skills()
    total = sum(s["tokens"] for s in skills)
    return {
        "skill_count": len(skills),
        "total_tokens": total,
        "skills": sorted(skills, key=lambda s: -s["tokens"]),
        "over_budget": sorted([s for s in skills if s["tokens"] > BUDGET_WARN_TOKENS],
                              key=lambda s: -s["tokens"]),
        "trigger_overlaps": trigger_overlaps(skills),
        "routing_gaps": routing_gaps(skills),
        "never_used": never_used(skills),
    }


def render_budget(data: dict) -> str:
    rows = [[s["skill"], str(s["tokens"]), str(len(s["subcommands"])),
             "OVER" if s["tokens"] > BUDGET_WARN_TOKENS else ""]
            for s in data["skills"]]
    return "\n".join([
        f"# SKILL.md Context Budget ({data['skill_count']} skills, "
        f"~{_human(data['total_tokens'])} tokens total)\n",
        markdown_table(["Skill", "Tokens", "Subcmds", "Flag"], rows),
        f"\n**Over budget (>{BUDGET_WARN_TOKENS} tok):** {len(data['over_budget'])}",
    ])


def render_gaps(data: dict) -> str:
    out = ["# Coverage Gaps & Trigger Overlap\n",
           f"**Skills undocumented in routing docs:** {len(data['routing_gaps'])}"]
    if data["routing_gaps"]:
        out.append(", ".join(data["routing_gaps"]))
    out.append(f"\n**Trigger-keyword overlaps:** {len(data['trigger_overlaps'])} keywords")
    top = data["trigger_overlaps"][:12]
    if top:
        out.append(markdown_table(["Keyword", "Skills sharing it"],
                                  [[o["keyword"], ", ".join(o["skills"])] for o in top]))
    return "\n".join(out)


def _human(n: int) -> str:
    return f"{n / 1000:.0f}K" if n >= 1000 else str(n)


def render_md(data: dict) -> str:
    return render_budget(data) + "\n\n" + render_gaps(data)


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill coverage + context budget (S4)")
    ap.add_argument("--budget-only", action="store_true")
    ap.add_argument("--gaps-only", action="store_true")
    ap.add_argument("--decommission", action="store_true", help="list never-used skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    data = gather()
    if args.json or args.format == "json":
        print(json_output(data))
    elif args.decommission:
        print("\n".join(data["never_used"]) or "(all skills used at least once)")
    elif args.budget_only:
        print(render_budget(data))
    elif args.gaps_only:
        print(render_gaps(data))
    else:
        print(render_md(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
