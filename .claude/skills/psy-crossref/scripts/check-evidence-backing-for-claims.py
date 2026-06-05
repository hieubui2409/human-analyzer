"""Dimension 5: Gather profile psychological claims and their material evidence signals.

GATHER-ONLY (Golden Rule): this script emits deterministic signals — claim extraction,
material keyword matching, tier lookup. It does NOT emit severity verdicts (MAJOR/MINOR).
LLM adjudication is required to decide whether a claim is adequately evidenced.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_frontmatter

CLAIM_FILES = [
    "psychology/formulation.md",
    "psychology/defense-mechanisms.md",
    "psychology/attachment-style.md",
    "psychology/core-wounds.md",
    "psychology/growth-edges.md",
    "psychology/diagnostics.md",
    "psychology/archetype.md",
]

CLAIM_PATTERNS = [
    re.compile(r"\*\*([^*]+)\*\*", re.IGNORECASE),
    re.compile(r"^[-*]\s+(.+?)(?:\s*[—–:]\s)", re.MULTILINE),
    re.compile(r"(?:exhibits?|displays?|shows?|demonstrates?|characterized by)\s+(.+?)(?:\.|,|;)", re.IGNORECASE),
]


def extract_claims(text: str) -> list[str]:
    """Extract psychological claim phrases from profile text."""
    claims = set()
    for pattern in CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            claim = match.group(1).strip()
            if len(claim) > 5 and len(claim) < 120:
                claims.add(claim)
    return sorted(claims)


def get_material_tiers(slug: str) -> dict[str, str]:
    """Map material filenames to their evidence tiers."""
    mat_dir = MATERIALS / slug
    tiers = {}
    if not mat_dir.exists():
        return tiers
    for f in mat_dir.rglob("*.md"):
        fm = extract_frontmatter(f) or {}
        tier = fm.get("evidence_tier", "")
        tiers[f.name] = tier
    return tiers


def search_claim_in_materials(claim: str, slug: str) -> list[dict]:
    """Search for claim keywords in materials, return matches with tiers."""
    mat_dir = MATERIALS / slug
    if not mat_dir.exists():
        return []
    keywords = [w.lower() for w in claim.split() if len(w) > 3]
    if not keywords:
        return []
    matches = []
    for f in sorted(mat_dir.rglob("*.md")):
        text = f.read_text(encoding="utf-8").lower()
        fm = extract_frontmatter(f) or {}
        hit_count = sum(1 for kw in keywords if kw in text)
        if hit_count >= max(1, len(keywords) // 2):
            matches.append({
                "file": f.name,
                "tier": fm.get("evidence_tier", "?"),
                "hit_ratio": f"{hit_count}/{len(keywords)}",
            })
    return matches


def gather_character(slug: str) -> list[dict]:
    """Gather evidence signals for all claims in a character's profile."""
    profile_dir = PROFILES / slug
    signals = []
    for rel_path in CLAIM_FILES:
        fpath = profile_dir / rel_path
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        claims = extract_claims(text)
        for claim in claims[:30]:
            matches = search_claim_in_materials(claim, slug)
            best_tier = None
            for m in matches:
                t = m["tier"]
                if t and t.startswith("T"):
                    try:
                        tier_num = int(t[1])
                        if best_tier is None or tier_num < best_tier:
                            best_tier = tier_num
                    except ValueError:
                        pass
            keyword_list = [w.lower() for w in claim.split() if len(w) > 3]
            signals.append({
                "file": rel_path,
                "claim": claim[:80],
                "best_tier": f"T{best_tier}" if best_tier else "none",
                "material_matches": len(matches),
                "keyword_hit_ratio": f"{len(matches)}/{max(1, len(keyword_list))}",
                "needs_llm_adjudication": True,
            })
    return signals


def main():
    parser = argparse.ArgumentParser(
        description="Gather evidence signals for profile claims (Dim 5) — LLM adjudicates verdicts"
    )
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    all_signals: dict[str, list[dict]] = {}
    for slug in chars:
        all_signals[slug] = gather_character(slug)

    if args.json_out:
        print(json.dumps(all_signals, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*70}")
    print("  Dimension 5: Evidence Backing Signals (GATHER-ONLY)")
    print("  NOTE: Verdict (adequate/inadequate) requires LLM adjudication.")
    print(f"{'='*70}")

    for slug, signals in all_signals.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n  {display} ({slug})")
        if not signals:
            print("    No claims extracted.")
            continue
        no_match = [s for s in signals if s["material_matches"] == 0]
        low_tier = [s for s in signals if s["material_matches"] > 0 and s["best_tier"] not in ("T1", "T2", "T3")]
        print(f"    Total signals: {len(signals)} | No material match: {len(no_match)} | Tier>T3: {len(low_tier)}")
        print(f"\n    {'File':<35s} {'Best Tier':<10s} {'Matches':<8s} Claim")
        print(f"    {'-'*35} {'-'*10} {'-'*8} {'-'*40}")
        for s in signals:
            print(f"    {s['file']:<35s} {s['best_tier']:<10s} {s['material_matches']:<8d} {s['claim']}")

    print(f"\n  All signals require LLM adjudication before verdict assignment.")


if __name__ == "__main__":
    main()
