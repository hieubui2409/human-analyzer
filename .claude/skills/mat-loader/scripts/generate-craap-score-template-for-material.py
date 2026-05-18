"""Generate CRAAP scoring template for a material file."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.materials_classifier import (
    SOURCE_TO_TIER,
    extract_frontmatter,
    detect_material_type,
)


TIER_RECOMMENDATION = {
    "primary": "T1 — High confidence, direct testimony",
    "secondary": "T2 — High confidence, professional assessment",
    "tertiary": "T3 — Medium confidence, media/social sources",
    "contextual": "T4 — Medium-low, third-party accounts",
    "auxiliary": "T5 — Low confidence, inferred data",
}


def main():
    parser = argparse.ArgumentParser(description="Generate CRAAP scoring template")
    parser.add_argument("file", help="Path to material file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    fpath = Path(args.file)
    if not fpath.exists():
        print(f"Error: file not found: {fpath}", file=sys.stderr)
        sys.exit(1)

    fm = extract_frontmatter(fpath) or {}
    material_type = fm.get("material_type", detect_material_type(fpath))
    source_cat = fm.get("source_category", "unknown")
    captured_date = fm.get("captured_date", "unknown")
    title = fm.get("title", fpath.stem)
    creator = fm.get("source_creator", "unknown")

    template = {
        "material": str(fpath.name),
        "title": title,
        "source_category": source_cat,
        "tier_recommendation": TIER_RECOMMENDATION.get(source_cat, "Unknown — classify source_category first"),
        "craap_scores": {
            "currency": {
                "score": None,
                "notes": f"Captured: {captured_date}. How recent? Still relevant?",
            },
            "relevance": {
                "score": None,
                "notes": "How directly does this relate to character profile sections?",
            },
            "authority": {
                "score": None,
                "notes": f"Creator: {creator}. Proximity to subject? Credentials?",
            },
            "accuracy": {
                "score": None,
                "notes": "Can claims be cross-referenced? Internal consistency?",
            },
            "purpose": {
                "score": None,
                "notes": f"Material type: {material_type}. Intent: clinical/personal/media?",
            },
        },
        "overall_quality_score": None,
        "llm_notes": "Fill in scores (1-10) and notes. Overall = average of 5 dimensions.",
    }

    if args.json:
        print(json.dumps(template, indent=2, ensure_ascii=False))
        return

    print(f"# CRAAP Scoring Template: {title}")
    print(f"\nSource: {fpath.name}")
    print(f"Category: {source_cat}")
    print(f"Tier: {TIER_RECOMMENDATION.get(source_cat, 'Unknown')}")
    print()
    for dim, data in template["craap_scores"].items():
        print(f"## {dim.upper()}")
        print(f"  Score: ___/10")
        print(f"  Notes: {data['notes']}")
        print()
    print("## OVERALL QUALITY SCORE: ___/10")


if __name__ == "__main__":
    main()
