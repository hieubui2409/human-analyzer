"""Dimension 5: Check profile psychological claims have evidence backing ≥T3."""
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
    for f in mat_dir.glob("*.md"):
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
    for f in sorted(mat_dir.glob("*.md")):
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


def check_character(slug: str) -> list[dict]:
    """Check evidence backing for all claims in a character's profile."""
    profile_dir = PROFILES / slug
    findings = []
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
            severity = "OK"
            if not matches:
                severity = "MAJOR"
            elif best_tier is None or best_tier > 3:
                severity = "MINOR"
            if severity != "OK":
                findings.append({
                    "file": rel_path,
                    "claim": claim[:80],
                    "best_tier": f"T{best_tier}" if best_tier else "none",
                    "material_matches": len(matches),
                    "severity": severity,
                })
    return findings


def main():
    parser = argparse.ArgumentParser(description="Check evidence backing for profile claims (Dim 5)")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    all_findings: dict[str, list[dict]] = {}
    for slug in chars:
        all_findings[slug] = check_character(slug)

    if args.json_out:
        print(json.dumps(all_findings, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*70}")
    print("  Dimension 5: Evidence Backing Check")
    print(f"{'='*70}")

    total_issues = 0
    for slug, findings in all_findings.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n  {display} ({slug})")
        if not findings:
            print("    All claims have adequate evidence backing.")
            continue
        majors = [f for f in findings if f["severity"] == "MAJOR"]
        minors = [f for f in findings if f["severity"] == "MINOR"]
        print(f"    MAJOR (no evidence): {len(majors)} | MINOR (T4+ only): {len(minors)}")
        print(f"\n    {'Severity':<8s} {'File':<35s} {'Best Tier':<10s} Claim")
        print(f"    {'-'*8} {'-'*35} {'-'*10} {'-'*40}")
        for f in findings:
            print(f"    {f['severity']:<8s} {f['file']:<35s} {f['best_tier']:<10s} {f['claim']}")
        total_issues += len(findings)

    print(f"\n  TOTAL ISSUES: {total_issues}")
    if total_issues > 0:
        print("  Recommendation: Add T1-T3 source materials or qualify claims with [UNCERTAIN] tag")


if __name__ == "__main__":
    main()
