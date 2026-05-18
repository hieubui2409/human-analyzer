"""Extract PSY profile data into CRE-ready translation context for cre:post-writer."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import PROFILES, ALL_CHARS, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections

FORMULATION_5P = {
    "Presenting": "vulnerability — content angles showing current struggles",
    "Predisposing": "narrative — backstory explaining why patterns formed",
    "Precipitating": "trigger — recent events that activated patterns",
    "Perpetuating": "cycle — what keeps patterns alive today",
    "Protective": "resilience — what provides hope and strength",
}

DEFENSE_TO_VOICE = {
    "intellectualization": "analytical, abstract, theory-heavy tone",
    "rationalization": "justifying, logic-forward, self-explaining",
    "projection": "other-focused, externalized attribution",
    "sublimation": "creative, transformed expression",
    "humor": "self-deprecating, wit as shield",
    "displacement": "redirected intensity, misplaced emotion",
    "denial": "metaphor-heavy, indirect expression",
    "acting out": "raw, unfiltered emotional expression",
    "isolation of affect": "detached, clinical, emotion-stripped",
    "suppression": "understated, controlled emotional expression",
}


def extract_translation_context(slug: str) -> dict:
    """Extract PSY→CRE translation data for a character."""
    char_dir = PROFILES / slug
    display = CHAR_DISPLAY.get(slug, slug)

    context = {
        "character": slug,
        "display_name": display,
        "formulation_5p": {},
        "defense_voice_filter": [],
        "archetype_narrative_stance": "",
        "writing_voice_summary": "",
    }

    formulation_file = char_dir / "psychology" / "formulation.md"
    if formulation_file.exists():
        sections = extract_sections(formulation_file, level=2)
        for p_key, cre_hint in FORMULATION_5P.items():
            for section_name, content in sections.items():
                if p_key.lower() in section_name.lower():
                    context["formulation_5p"][p_key] = {
                        "content_angle": cre_hint,
                        "summary": content[:300].strip(),
                    }
                    break

    defense_file = char_dir / "psychology" / "defense-mechanisms.md"
    if defense_file.exists():
        try:
            text = defense_file.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        for mechanism, voice in DEFENSE_TO_VOICE.items():
            if mechanism in text:
                context["defense_voice_filter"].append({
                    "mechanism": mechanism,
                    "voice_filter": voice,
                })

    archetype_file = char_dir / "psychology" / "archetype.md"
    if archetype_file.exists():
        sections = extract_sections(archetype_file, level=2)
        for name, content in sections.items():
            if any(kw in name.lower() for kw in ["archetype", "narrative", "primary"]):
                context["archetype_narrative_stance"] = content[:200].strip()
                break

    voice_file = char_dir / "identity" / "writing-voice.md"
    if voice_file.exists():
        sections = extract_sections(voice_file, level=2)
        for name, content in sections.items():
            if any(kw in name.lower() for kw in ["tone", "style", "voice", "summary"]):
                context["writing_voice_summary"] = content[:300].strip()
                break

    return context


def main():
    parser = argparse.ArgumentParser(description="Extract PSY→CRE translation context")
    parser.add_argument("--character", "-c", help="Character slug (default: all)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [args.character] if args.character else ALL_CHARS
    results = {}
    for slug in chars:
        results[slug] = extract_translation_context(slug)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    for slug, ctx in results.items():
        print(f"\n{'='*60}")
        print(f"  {ctx['display_name']} ({slug}) — PSY→CRE Translation")
        print(f"{'='*60}")

        print(f"\n  ## 5P Formulation → Content Angles")
        for p_key, data in ctx["formulation_5p"].items():
            print(f"    {p_key}: {data['content_angle']}")
            print(f"      → {data['summary'][:100]}...")

        print(f"\n  ## Defense Mechanisms → Voice Filter")
        for df in ctx["defense_voice_filter"]:
            print(f"    {df['mechanism']}: {df['voice_filter']}")

        if ctx["archetype_narrative_stance"]:
            print(f"\n  ## Archetype → Narrative Stance")
            print(f"    {ctx['archetype_narrative_stance'][:150]}...")

        if ctx["writing_voice_summary"]:
            print(f"\n  ## Writing Voice")
            print(f"    {ctx['writing_voice_summary'][:150]}...")


if __name__ == "__main__":
    main()
