"""Check voice consistency against defense mechanism profile for cre:voice-audit."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import PROFILES, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections

DEFENSE_VOICE_INDICATORS = {
    "intellectualization": {
        "expected": ["phân tích", "lý thuyết", "nghiên cứu", "framework", "systematic", "logic",
                     "abstract", "theory", "analyze", "mechanism"],
        "misaligned": ["tức giận", "ghét", "điên", "raw", "scream", "rage", "fury"],
    },
    "rationalization": {
        "expected": ["bởi vì", "lý do", "giải thích", "justify", "reason", "because", "logic"],
        "misaligned": ["không biết tại sao", "vô lý", "irrational"],
    },
    "sublimation": {
        "expected": ["sáng tạo", "creative", "art", "viết", "write", "transform", "channel"],
        "misaligned": ["phá hủy", "destroy", "aggressive"],
    },
    "humor": {
        "expected": ["cười", "haha", "đùa", "joke", "laugh", "irony", "witty"],
        "misaligned": ["nghiêm túc", "serious", "solemn", "grave"],
    },
    "denial": {
        "expected": ["metaphor", "ẩn dụ", "như là", "as if", "imagine", "indirect"],
        "misaligned": ["trực tiếp", "blunt", "direct confrontation"],
    },
    "isolation of affect": {
        "expected": ["khách quan", "objective", "clinical", "detached", "neutral"],
        "misaligned": ["cảm xúc mãnh liệt", "overwhelming", "passionate"],
    },
}


def detect_active_defenses(slug: str) -> list[str]:
    """Detect which defense mechanisms are active for a character."""
    defense_file = PROFILES / slug / "psychology" / "defense-mechanisms.md"
    if not defense_file.exists():
        return []

    try:
        text = defense_file.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return []

    active = []
    for mechanism in DEFENSE_VOICE_INDICATORS:
        if mechanism.replace("_", " ") in text or mechanism in text:
            active.append(mechanism)
    return active


def check_voice_consistency(asset_dir: Path, slug: str) -> dict:
    """Check if content voice aligns with defense hierarchy."""
    post_file = asset_dir / "post.txt"
    if not post_file.exists():
        return {"error": f"post.txt not found in {asset_dir}"}

    try:
        content = post_file.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return {"error": f"Cannot read {post_file}"}

    active_defenses = detect_active_defenses(slug)
    display = CHAR_DISPLAY.get(slug, slug)

    checks = []
    for mechanism in active_defenses:
        indicators = DEFENSE_VOICE_INDICATORS.get(mechanism, {})
        expected_hits = sum(1 for kw in indicators.get("expected", []) if kw in content)
        misaligned_hits = sum(1 for kw in indicators.get("misaligned", []) if kw in content)

        if expected_hits > 0 and misaligned_hits == 0:
            consistency = "ALIGNED"
        elif misaligned_hits > expected_hits:
            consistency = "MISALIGNED"
        elif expected_hits == 0 and misaligned_hits == 0:
            consistency = "NEUTRAL"
        else:
            consistency = "MIXED"

        checks.append({
            "defense_active": mechanism,
            "expected_voice_hits": expected_hits,
            "misaligned_voice_hits": misaligned_hits,
            "consistency": consistency,
        })

    return {
        "asset_dir": str(asset_dir),
        "character": slug,
        "display_name": display,
        "active_defenses": active_defenses,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Check voice consistency against defense profile")
    parser.add_argument("asset_dir", help="Path to asset directory")
    parser.add_argument("--character", "-c", required=True, help="Character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = check_voice_consistency(Path(args.asset_dir), args.character)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        has_misaligned = any(c["consistency"] == "MISALIGNED" for c in result.get("checks", []))
        sys.exit(1 if has_misaligned else 0)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"\n  Character: {result['display_name']} ({result['character']})")
    print(f"  Asset: {result['asset_dir']}")
    print(f"  Active defenses: {', '.join(result['active_defenses'])}")
    print(f"\n  {'Defense':<24s} {'Expected':<10s} {'Misaligned':<12s} {'Status':<12s}")
    print(f"  {'-'*24} {'-'*10} {'-'*12} {'-'*12}")

    for check in result["checks"]:
        icon = {"ALIGNED": "✓", "MISALIGNED": "✗", "NEUTRAL": "○", "MIXED": "~"}.get(check["consistency"], "?")
        print(f"  {icon} {check['defense_active']:<22s} {check['expected_voice_hits']:<10d} {check['misaligned_voice_hits']:<12d} {check['consistency']:<12s}")


if __name__ == "__main__":
    main()
