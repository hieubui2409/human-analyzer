"""CE-02 Progressive-Disclosure conformance audit (C3-ext, Tiers 0-2 + verdict).

GOLDEN RULE #4: deterministic gather only. Scores every PROJECT-OWNED skill against
the CE-02 "200-line rule" + Anthropic skill-creator structural rules, then emits a
verdict (KEEP | ENHANCE-CE02 | REFACTOR-PD | BLOCK). The LLM adjudicates wording and
"complementary != duplicate"; this script never edits SKILL.md and never applies a
refactor. READ-ONLY.

Scope (Tier 0, triple-guarded against the no-ck boundary):
  dir prefix in {orc,psy,cre,gro,mat,com}-  OR  dir == "test-orchestrator"
  AND frontmatter `name:` does NOT start with "ck:"
  AND no ClaudeKit license / $id marker in SKILL.md
ck-origin skills (cook, plan, scout, skill-creator, ...) are HARD-EXCLUDED — the
excluded set is asserted in the output so the guard is auditable.

Reuse (DRY, no fork): description-format scoring is delegated to the sibling
score-skill-description.py via importlib (same loader pattern as scan_skills.py).

Usage:
  audit-skill-progressive-disclosure.py [SKILLS_DIR] [--scope project-owned|all]
                                        [--json] [--strict]
  --strict  exit 1 if any skill verdict == BLOCK (CI gate).
"""
from __future__ import annotations

import argparse
import importlib.util as _ilu
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.markdown_parser import extract_frontmatter  # noqa: E402

FRAMEWORKS = ("orc", "psy", "cre", "gro", "mat", "com")
EXTRA_PROJECT_DIRS = {"test-orchestrator"}

# ── Tiered thresholds (PD-1/CM-1: 200 = WARN, 300 = FAIL) ─────────────────────
ENTRY_WARN = 200
ENTRY_FAIL = 300
REF_FAIL = 300          # PD-2 each references/*.md
COLD_START_WARN = 500   # PD-5 entry + largest ref
DESC_MAX = 1024         # DS-1
DUP_JACCARD_WARN = 0.30  # DUP-1 SKILL.md <-> references shingle overlap

# ── Section / trigger detection ───────────────────────────────────────────────
_WHEN_TO_USE = re.compile(r"^#{1,4}\s*When to Use\b", re.I | re.M)
_ANTIPATTERN = re.compile(r"anti[- ]?pattern", re.I)
_NAV_HINT = re.compile(r"references/|^#{1,4}\s*(Navigation|Reference|See Also)\b", re.I | re.M)
_TRIGGER_DESC = re.compile(r"use when|triggers?\b|invoke (when|for)", re.I)
_SCOPE_DECL = re.compile(r"\bnot\b.{0,40}(handle|do|cover|for)|handles?.{0,40}\bnot\b|does not", re.I)
_CK_LICENSE = re.compile(r"claudekit\.cc|ClaudeKit Skill|license:\s*ClaudeKit", re.I)


def _load_sibling(filename: str, module_name: str):
    """Load a kebab-case sibling module (mirrors scan_skills.py loader)."""
    path = Path(__file__).resolve().parents[3] / "scripts" / filename
    spec = _ilu.spec_from_file_location(module_name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_scorer = _load_sibling("score-skill-description.py", "score_skill_description")


def _is_project_owned(d: Path) -> bool:
    if d.name in EXTRA_PROJECT_DIRS:
        return True
    prefix = d.name.split("-", 1)[0]
    return prefix in FRAMEWORKS


def _line_count(p: Path) -> int:
    return len(p.read_text(encoding="utf-8").splitlines())


def _shingles(text: str, n: int = 5) -> set:
    words = re.findall(r"\w+", text.lower())
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)} if len(words) >= n else set()


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def audit_skill(d: Path) -> dict:
    """One conformance record for a project-owned skill dir."""
    sk = d / "SKILL.md"
    rec = {
        "dir": d.name, "name": None, "entry_lines": 0,
        "findings": [], "verdict": "KEEP",
        "metrics": {}, "ck_excluded": False,
    }
    if not sk.exists():
        rec["findings"].append(("FAIL", "FM-1", "missing SKILL.md"))
        rec["verdict"] = "BLOCK"
        return rec

    text = sk.read_text(encoding="utf-8")
    fm = extract_frontmatter(sk)
    rec["name"] = fm.get("name")

    # Tier-0 second/third guard: ck name or ClaudeKit license → exclude.
    if (rec["name"] or "").startswith("ck:") or _CK_LICENSE.search(text):
        rec["ck_excluded"] = True
        return rec

    f = rec["findings"]

    # ── PD-1 entry-point length (tiered) ──
    entry = _line_count(sk)
    rec["entry_lines"] = entry
    if entry > ENTRY_FAIL:
        f.append(("FAIL", "PD-1", f"SKILL.md {entry} lines > {ENTRY_FAIL}"))
    elif entry > ENTRY_WARN:
        f.append(("WARN", "PD-1", f"SKILL.md {entry} lines > {ENTRY_WARN} (REFACTOR-PD candidate)"))

    # ── references/ structure (PD-2/3/4/5) ──
    refs_dir = d / "references"
    ref_files = sorted(refs_dir.rglob("*.md")) if refs_dir.is_dir() else []
    largest_ref = 0
    for rf in ref_files:
        rl = _line_count(rf)
        largest_ref = max(largest_ref, rl)
        if rl > REF_FAIL:
            f.append(("FAIL", "PD-2", f"references/{rf.name} {rl} lines > {REF_FAIL}"))
        # PD-3 depth: file deeper than references/<file>.md
        if rf.parent != refs_dir:
            f.append(("FAIL", "PD-3", f"nested reference {rf.relative_to(d)} (depth > 1)"))
    has_refs = bool(ref_files)
    rec["metrics"]["ref_count"] = len(ref_files)

    if entry > ENTRY_WARN and not has_refs:
        f.append(("WARN", "PD-4", f"entry {entry}>{ENTRY_WARN} but no references/ (progressive disclosure)"))
    if entry + largest_ref > COLD_START_WARN:
        f.append(("WARN", "PD-5", f"cold-start budget {entry}+{largest_ref} > {COLD_START_WARN}"))

    # ── description (DS-1/DS-2) ──
    desc = (fm.get("description") or "").strip()
    if not desc:
        f.append(("FAIL", "DS-1", "description missing"))
    elif len(desc) > DESC_MAX:
        f.append(("FAIL", "DS-1", f"description {len(desc)} chars > {DESC_MAX}"))
    if desc and not _TRIGGER_DESC.search(desc):
        f.append(("WARN", "DS-2", "description lacks trigger context ('use when ...')"))

    # ── sections (WU-1 / NV-1 / AP-1) ──
    has_wtu = bool(_WHEN_TO_USE.search(text)) or "when_to_use" in fm
    rec["metrics"]["has_when_to_use"] = has_wtu
    if not has_wtu:
        f.append(("WARN", "WU-1", "no '## When to Use' / when_to_use:"))
    if entry > ENTRY_WARN and not _NAV_HINT.search(text):
        f.append(("WARN", "NV-1", "entry > 200 but no navigation map to references/"))
    if not _ANTIPATTERN.search(text):
        f.append(("INFO", "AP-1", "no anti-patterns section"))

    # ── SEC-1 scope declaration ──
    if not _SCOPE_DECL.search(text):
        f.append(("WARN", "SEC-1", "no explicit scope declaration ('handles X, NOT Y')"))

    # ── DUP-1 SKILL.md <-> references shingle overlap ──
    if ref_files:
        body_sh = _shingles(text)
        for rf in ref_files:
            sim = _jaccard(body_sh, _shingles(rf.read_text(encoding="utf-8")))
            if sim > DUP_JACCARD_WARN:
                f.append(("WARN", "DUP-1", f"SKILL.md ~ references/{rf.name} overlap {sim:.2f}"))

    # ── verdict (BLOCK > REFACTOR-PD > ENHANCE-CE02 > KEEP) ──
    sev = {s for s, _, _ in f}
    refactor = any(c in ("PD-1", "PD-4") and s == "WARN" for s, c, _ in f)
    if "FAIL" in sev:
        rec["verdict"] = "BLOCK"
    elif refactor:
        rec["verdict"] = "REFACTOR-PD"
    elif "WARN" in sev:
        rec["verdict"] = "ENHANCE-CE02"
    else:
        rec["verdict"] = "KEEP"
    return rec


def collect(skills_dir: Path, scope: str) -> tuple[list[dict], list[str], list[str]]:
    records, excluded, orphans = [], [], []
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        owned = _is_project_owned(d)
        if scope == "project-owned" and not owned:
            excluded.append(d.name)
            continue
        # A dir with no SKILL.md is not a skill (e.g. orphan __pycache__ residue
        # left after a source removal). Cataloging "missing SKILL.md" belongs to
        # C3 stocktake; the conformance gate must not BLOCK on a non-skill.
        if not (d / "SKILL.md").exists():
            orphans.append(d.name)
            continue
        rec = audit_skill(d)
        if rec.get("ck_excluded"):
            excluded.append(d.name)
            continue
        records.append(rec)
    return records, excluded, orphans


def main() -> None:
    ap = argparse.ArgumentParser(description="CE-02 progressive-disclosure conformance audit (READ-ONLY).")
    ap.add_argument("skills_dir", nargs="?", default=None)
    ap.add_argument("--scope", choices=["project-owned", "all"], default="project-owned")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any verdict == BLOCK")
    args = ap.parse_args()

    skills_dir = Path(args.skills_dir) if args.skills_dir \
        else Path(__file__).resolve().parents[3] / "skills"
    if not skills_dir.is_dir():
        raise SystemExit(f"Error: {skills_dir} not found")

    records, excluded, orphans = collect(skills_dir, args.scope)

    verdicts = {v: sum(1 for r in records if r["verdict"] == v)
                for v in ("KEEP", "ENHANCE-CE02", "REFACTOR-PD", "BLOCK")}
    blocks = [r for r in records if r["verdict"] == "BLOCK"]
    refactors = [r for r in records if r["verdict"] == "REFACTOR-PD"]
    wtu_cov = sum(1 for r in records if r["metrics"].get("has_when_to_use"))

    out = {
        "scope": args.scope, "total": len(records),
        "verdicts": verdicts, "when_to_use_coverage": f"{wtu_cov}/{len(records)}",
        "excluded_ck_or_foreign": excluded,
        "orphan_dirs_no_skill_md": orphans, "skills": records,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"\nCE-02 Conformance — {len(records)} project-owned skills "
              f"(excluded {len(excluded)} ck/foreign)")
        print(f"  verdicts: " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))
        print(f"  When-to-Use coverage: {wtu_cov}/{len(records)}")
        if orphans:
            print(f"  orphan dirs (no SKILL.md — recommend cleanup): {', '.join(orphans)}")
        if blocks:
            print(f"\n  ✗ BLOCK ({len(blocks)}):")
            for r in blocks:
                fails = [f"{c}: {m}" for s, c, m in r["findings"] if s == "FAIL"]
                print(f"    {r['name'] or r['dir']} — {'; '.join(fails)}")
        if refactors:
            print(f"\n  ⟳ REFACTOR-PD ({len(refactors)}):")
            for r in sorted(refactors, key=lambda x: -x["entry_lines"]):
                print(f"    {r['name'] or r['dir']} ({r['entry_lines']} lines)")

    if args.strict and blocks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
