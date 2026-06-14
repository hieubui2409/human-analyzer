"""Quick Scan — enumerate the project skill catalog + cross-check CLAUDE.md (C3).

GOLDEN RULE #4: deterministic gather only. Counts project-owned skills per framework,
checks SKILL.md frontmatter completeness, and reconciles the live catalog against the
CLAUDE.md skill tables + the declared total. No overlap/retire judgment here (that is
analyze-skill-overlap-and-gaps.py + LLM). READ-ONLY.

Project-owned scope = dir prefix in {orc,psy,cre,gro,mat,com}- (ck-origin skills like
cook/plan/scout/skill-creator are excluded — no-ck boundary).

Usage:
  scan-skill-catalog-metadata.py [--framework orc|psy|cre|gro|mat|com] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.markdown_parser import extract_frontmatter
from platform_lib import paths

SKILLS_DIR = paths.ROOT / ".claude" / "skills"
CLAUDE_MD = paths.ROOT / "CLAUDE.md"
FRAMEWORKS = ["orc", "psy", "cre", "gro", "mat", "com", "evl"]

# CLAUDE.md catalog table rows look like:  | `orc:bootstrap` | ... |
_CATALOG_ROW = re.compile(r"\|\s*`([a-z]{3}):([a-z0-9-]+)`")


def _prefix(skill_dir: str) -> str | None:
    p = skill_dir.split("-", 1)[0]
    return p if p in FRAMEWORKS else None


def scan_catalog() -> list[dict]:
    """One record per project-owned skill: name, prefix, metadata completeness flags."""
    out = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        pfx = _prefix(d.name)
        if pfx is None:
            continue
        sk = d / "SKILL.md"
        rec = {"dir": d.name, "framework": pfx, "has_skill_md": sk.exists(),
               "name": None, "has_description": False, "has_triggers": False,
               "has_when_to_use": False, "has_category": False, "gaps": []}
        if not sk.exists():
            rec["gaps"].append("missing SKILL.md")
            out.append(rec)
            continue
        fm = extract_frontmatter(sk)
        text = sk.read_text(encoding="utf-8")
        rec["name"] = fm.get("name")
        desc = fm.get("description", "")
        rec["has_description"] = bool(desc)
        rec["has_triggers"] = "rigger" in desc or "rigger" in text  # Triggers: / triggers
        rec["has_when_to_use"] = bool(re.search(r"##\s*When to Use", text, re.I)) or "when_to_use" in fm
        rec["has_category"] = "category" in fm or bool(fm.get("metadata"))
        if not rec["name"]:
            rec["gaps"].append("missing name")
        if not rec["has_description"]:
            rec["gaps"].append("missing description")
        if not rec["has_triggers"]:
            rec["gaps"].append("missing Triggers")
        if not rec["has_when_to_use"]:
            rec["gaps"].append("missing ## When to Use")
        out.append(rec)
    return out


def catalog_in_claude_md() -> set[str]:
    """Skill names (prefix:slug) declared in CLAUDE.md tables."""
    if not CLAUDE_MD.exists():
        return set()
    text = CLAUDE_MD.read_text(encoding="utf-8")
    return {f"{m.group(1)}:{m.group(2)}" for m in _CATALOG_ROW.finditer(text)
            if m.group(1) in FRAMEWORKS}


def declared_total() -> int | None:
    """The 'NN framework skills' count line in CLAUDE.md Skills Catalog, if present.

    Matches both forms:
      59 framework skills (ORC 17 ...)   ← current CLAUDE.md format
      59 skills (orc/mat/...)            ← alternate format
    """
    if not CLAUDE_MD.exists():
        return None
    m = re.search(r"(\d+)\s+(?:framework\s+)?skills?\b", CLAUDE_MD.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def reconcile(records: list[dict]) -> dict:
    live = {(r["name"] or f"{r['framework']}:{r['dir'].split('-',1)[1]}") for r in records}
    # normalize live names to prefix:slug (name frontmatter is e.g. "orc:bootstrap")
    live_names = {r["name"] for r in records if r["name"]}
    declared = catalog_in_claude_md()
    return {
        "live_count": len(records),
        "claude_md_count": len(declared),
        "declared_total": declared_total(),
        "in_catalog_not_in_claude_md": sorted(live_names - declared),
        "in_claude_md_not_in_catalog": sorted(declared - live_names),
    }


def main():
    ap = argparse.ArgumentParser(description="Quick Scan project skill catalog (READ-ONLY).")
    ap.add_argument("--framework", choices=FRAMEWORKS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    records = scan_catalog()
    if args.framework:
        records = [r for r in records if r["framework"] == args.framework]
    by_fw = {fw: sum(1 for r in records if r["framework"] == fw) for fw in FRAMEWORKS}
    gaps = [r for r in records if r["gaps"]]
    rec = reconcile(scan_catalog())

    out = {"by_framework": by_fw, "total": len(records),
           "reconcile": rec, "metadata_gaps": gaps}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print(f"\nSkill catalog — {len(records)} project-owned skills")
    print("  " + "  ".join(f"{fw}={by_fw[fw]}" for fw in FRAMEWORKS))
    print(f"\n  CLAUDE.md tables list: {rec['claude_md_count']} | declared total: {rec['declared_total']}")
    if rec["in_catalog_not_in_claude_md"]:
        print("  ⚠ in catalog, NOT in CLAUDE.md:", rec["in_catalog_not_in_claude_md"])
    if rec["in_claude_md_not_in_catalog"]:
        print("  ⚠ in CLAUDE.md, NOT in catalog:", rec["in_claude_md_not_in_catalog"])
    if gaps:
        print(f"\n  Metadata gaps ({len(gaps)} skills):")
        for r in gaps:
            print(f"    {r['name'] or r['dir']}: {', '.join(r['gaps'])}")


if __name__ == "__main__":
    main()
