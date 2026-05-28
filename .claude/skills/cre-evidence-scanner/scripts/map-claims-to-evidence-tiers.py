"""Map draft claims to MAT evidence tiers + Rule-09 leak status (gather layer).

GOLDEN RULE #4 split:
  - SCRIPT (here, deterministic): segment claims, OVER-GATHER candidate materials
    per claim by keyword/entity overlap, attach tier + confidentiality, detect
    Rule-09 privacy tags + raw clinical terms in the claim text, and emit a
    FAIL-CLOSED preliminary verdict.
  - LLM (downstream, see SKILL.md): adjudicate whether a candidate material
    actually SUPPORTS the claim, then finalize PASS/WARN/FAIL.

Verdict policy (evidence_tier_permissions):
  T1/T2 → PASS · T3 → WARN · T4/T5 → FAIL · no evidence → WARN (never silent PASS)
  Rule-09 leak in claim ([PRIVATE]/[CONFIDENTIAL]/[ANONYMIZE]/raw clinical term) → FAIL.

Replaces cre-post-writer/scripts/check-evidence-tier-compliance-in-draft.py
(keeps the same --json exit-1-on-FAIL contract so post-writer/validation keep working).

Usage:
  map-claims-to-evidence-tiers.py <asset_dir> [--character <slug>] [--json] [--strict]
READ-ONLY on materials. Exit 1 on any FAIL.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import MATERIALS, ALL_CHARS, CHAR_DISPLAY, resolve_character
from platform_lib.materials_classifier import extract_frontmatter, SOURCE_TO_TIER
from platform_lib.markdown_parser import extract_tags
from platform_lib.clinical_terms import COMPILED_PATTERNS
from platform_lib.evidence_tier_permissions import (
    tier_permission, verdict_for_tier, worst_verdict, NO_EVIDENCE_VERDICT, VERDICT_ICON,
)

# Load the sibling claim extractor (hyphenated filename → load by path).
_EXTRACT = Path(__file__).with_name("extract-claims-from-draft.py")
_spec = importlib.util.spec_from_file_location("extract_claims_mod", _EXTRACT)
_ecm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ecm)

_STOP = {"này", "đó", "của", "với", "cho", "các", "một", "những", "được", "là",
         "và", "the", "and", "for", "with", "that", "this", "from"}


def _keywords(text: str) -> set[str]:
    return {w.lower().strip(".,!?:;\"'()") for w in text.split()
            if len(w) > 3 and w.lower() not in _STOP}


def load_character_materials(slug: str) -> list[dict]:
    mdir = MATERIALS / slug
    if not mdir.exists():
        return []
    out = []
    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        fm = extract_frontmatter(fpath)
        if not fm:
            continue
        out.append({
            "file": fpath.name,
            "material_id": fm.get("material_id", ""),
            "title": fm.get("title", fpath.stem),
            "tier": SOURCE_TO_TIER.get(fm.get("source_category", ""), 5),
            "confidentiality": fm.get("confidentiality", "private"),
            "_kw": _keywords(f"{fm.get('title', fpath.stem)} {fm.get('content_tags', '')}"),
        })
    return out


def detect_characters(text: str) -> dict:
    low = text.lower()
    matches = {s: CHAR_DISPLAY.get(s, s) for s in ALL_CHARS
               if CHAR_DISPLAY.get(s, s).lower() in low or s.replace("-", " ") in low}
    return matches or {ALL_CHARS[0]: CHAR_DISPLAY.get(ALL_CHARS[0], ALL_CHARS[0])}


def detect_leaks(claim: str) -> list[str]:
    """Rule-09 leak signals in a claim: privacy tags + raw clinical terms."""
    leaks = [f"tag:{t['tag']}" for t in extract_tags(claim)]
    for pat in COMPILED_PATTERNS:
        m = pat.search(claim)
        if m:
            leaks.append(f"clinical:{m.group()}")
    return leaks


def gather_candidates(claim_kw: set[str], materials: list[dict]) -> list[dict]:
    """Over-gather: any material sharing >=1 keyword is a candidate (LLM prunes later)."""
    cands = []
    for m in materials:
        overlap = claim_kw & m["_kw"]
        if overlap:
            cands.append({
                "material": m["file"], "tier": m["tier"],
                "confidentiality": m["confidentiality"],
                "matched_keywords": sorted(overlap),
            })
    return sorted(cands, key=lambda c: c["tier"])  # best (lowest tier) first


def adjudicate_claim(claim: dict, materials: list[dict], strict: bool) -> dict:
    leaks = detect_leaks(claim["claim"])
    candidates = gather_candidates(_keywords(claim["claim"]), materials)

    if leaks:
        verdict, reason = "FAIL", "rule09_leak"
        tier = None
    elif not candidates:
        verdict, reason, tier = NO_EVIDENCE_VERDICT, "no_evidence_detected", None
    else:
        best_tier = candidates[0]["tier"]
        # restricted/private material → fail-closed even if tier numerically T1-T3
        conf_block = any(c["confidentiality"] in ("private", "restricted") for c in candidates)
        verdict = verdict_for_tier(best_tier, strict=strict)
        if conf_block and verdict == "PASS":
            verdict, reason = "WARN", "confidential_material"
        else:
            reason = "tier_mapped"
        tier = best_tier
    return {
        "claim": claim["claim"], "line": claim["line"],
        "verdict": verdict, "reason": reason,
        "evidence_tier": f"T{tier}" if tier else "—",
        "permission": tier_permission(tier)["permission"] if tier else "—",
        "leaks": leaks,
        "candidates": candidates,
        "needs_llm_adjudication": bool(candidates),  # LLM confirms support
    }


def scan(asset_dir: Path, character: str | None, strict: bool) -> dict:
    loaded = _ecm.read_draft(asset_dir)
    if loaded is None:
        return {"error": f"no post.txt|post.md in {asset_dir}"}
    text, draft_path = loaded
    claims = _ecm.extract_claims(text)

    if character:
        chars = {resolve_character(character): character}
    else:
        chars = detect_characters(text)

    materials = []
    for slug in chars:
        materials.extend(load_character_materials(slug))

    results = [adjudicate_claim(c, materials, strict) for c in claims]
    overall = worst_verdict([r["verdict"] for r in results])
    return {
        "asset_dir": str(asset_dir), "draft": str(draft_path),
        "characters": list(chars.values()), "strict": strict,
        "claim_count": len(results), "overall_verdict": overall,
        "claims": results,
    }


def main():
    ap = argparse.ArgumentParser(description="Map draft claims to evidence tiers + leak status.")
    ap.add_argument("asset_dir", help="Asset dir (e.g. assets/facebook/260413-slug/)")
    ap.add_argument("--character", help="Force character slug (else auto-detect)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--strict", action="store_true", help="T3 (qualified) → FAIL")
    args = ap.parse_args()

    result = scan(Path(args.asset_dir), args.character, args.strict)
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False) if args.json else f"Error: {result['error']}",
              file=sys.stderr if not args.json else sys.stdout)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n  Asset: {result['asset_dir']}  ({', '.join(result['characters'])})")
        print(f"  Overall: {result['overall_verdict']}   claims={result['claim_count']}\n")
        for r in result["claims"]:
            icon = VERDICT_ICON.get(r["verdict"], "?")
            leak = f"  ⚠ {','.join(r['leaks'])}" if r["leaks"] else ""
            print(f"  {icon} L{r['line']:>3} [{r['evidence_tier']:>2}] {r['verdict']:<4} {r['claim'][:60]}{leak}")

    sys.exit(1 if result["overall_verdict"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
