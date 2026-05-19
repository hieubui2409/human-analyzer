"""Extract a specific profile dimension from multiple characters for side-by-side comparison."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character

# Maps dimension arg → relative file path in profile
DIMENSION_MAP = {
    "defense-mechanisms": "psychology/defense-mechanisms.md",
    "attachment-style": "psychology/attachment-style.md",
    "core-wounds": "psychology/core-wounds.md",
    "formulation": "psychology/formulation.md",
    "diagnostics": "psychology/diagnostics.md",
    "archetype": "psychology/archetype.md",
    "growth-edges": "psychology/growth-edges.md",
    "cultural-formulation": "psychology/cultural-formulation.md",
    "traumas": "darkness/traumas.md",
    "strengths-hope": "light/strengths-hope.md",
    "family": "relationships/family.md",
    "timeline": "timeline/overview.md",
    "writing-voice": "identity/writing-voice.md",
    "current-state": "CURRENT-STATE.md",
    "index": "INDEX.md",
}


def extract_sections(text: str, max_sections: int = 6) -> dict[str, str]:
    """Extract H2 sections from markdown text. Returns {heading: first 200 chars}."""
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current = None
    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            if len(sections) > max_sections:
                break
        elif current and line.strip():
            sections[current].append(line.strip())

    result = {}
    for heading, body in sections.items():
        snippet = " ".join(body)[:200]
        if len(" ".join(body)) > 200:
            snippet += "..."
        result[heading] = snippet
    return result


def load_dimension(slug: str, file_path: str) -> dict:
    fp = PROFILES / slug / file_path
    if not fp.exists():
        return {"exists": False, "lines": 0, "sections": {}, "raw_preview": ""}
    text = fp.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.strip()]
    sections = extract_sections(text)
    # Also grab a top-level summary (first non-frontmatter, non-heading content)
    preview_lines = []
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            continue
        if line.startswith("#"):
            continue
        if line.strip():
            preview_lines.append(line.strip())
        if len(preview_lines) >= 3:
            break
    return {
        "exists": True,
        "lines": len(lines),
        "sections": sections,
        "raw_preview": " ".join(preview_lines)[:300],
    }


def build_comparison_table(chars: list[str], dim_data: dict[str, dict]) -> list[str]:
    """Build a markdown comparison table from section data across characters."""
    # Collect all section headings across all characters
    all_headings: list[str] = []
    seen = set()
    for slug in chars:
        for h in dim_data[slug].get("sections", {}).keys():
            if h not in seen:
                all_headings.append(h)
                seen.add(h)

    displays = [CHAR_DISPLAY.get(c, c) for c in chars]
    col_w = 28

    rows = []
    header = f"| {'Aspect':<30s} | " + " | ".join(f"{d:<{col_w}s}" for d in displays) + " |"
    sep = f"|{'-'*32}|" + "|".join(f"{'-'*(col_w+2)}" for _ in displays) + "|"
    rows.append(header)
    rows.append(sep)

    for heading in all_headings[:8]:  # Limit to 8 rows for readability
        cells = []
        for slug in chars:
            val = dim_data[slug].get("sections", {}).get(heading, "—")
            cell = val[:col_w - 1] if val != "—" else "—"
            cells.append(f"{cell:<{col_w}s}")
        rows.append(f"| {heading[:30]:<30s} | " + " | ".join(cells) + " |")

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Extract a profile dimension from multiple characters for comparison"
    )
    parser.add_argument("--dimension", "-d", required=True,
                        help=f"Dimension to compare. Options: {', '.join(DIMENSION_MAP.keys())}")
    parser.add_argument("--characters", "-c",
                        help="Comma-separated character slugs/aliases (default: all three)")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Resolve dimension
    dim_key = args.dimension.lower().strip()
    if dim_key not in DIMENSION_MAP:
        # Try partial match
        matches = [k for k in DIMENSION_MAP if dim_key in k]
        if len(matches) == 1:
            dim_key = matches[0]
        else:
            print(f"ERROR: Unknown dimension '{args.dimension}'")
            print(f"Available: {', '.join(DIMENSION_MAP.keys())}")
            sys.exit(1)
    file_path = DIMENSION_MAP[dim_key]

    # Resolve characters
    if args.characters:
        chars = [resolve_character(c.strip()) for c in args.characters.split(",")]
    else:
        chars = ALL_CHARS

    # Load data
    dim_data = {slug: load_dimension(slug, file_path) for slug in chars}

    if args.json_out:
        out = {
            "dimension": dim_key,
            "file_path": file_path,
            "characters": {
                slug: {**dim_data[slug], "display": CHAR_DISPLAY.get(slug, slug)}
                for slug in chars
            },
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    displays = [CHAR_DISPLAY.get(c, c) for c in chars]
    print(f"\n{'='*70}")
    print(f"  Profile Comparison: {dim_key}")
    print(f"{'='*70}")
    print(f"  File: {file_path}")
    print(f"  Characters: {' | '.join(displays)}")
    print()

    # Source file metadata
    print(f"  {'Character':<12s} {'File':<35s} {'Lines':<7s} {'Status'}")
    print(f"  {'-'*12} {'-'*35} {'-'*7} {'-'*10}")
    for slug in chars:
        d = dim_data[slug]
        status = "Present" if d["exists"] else "MISSING"
        lines = str(d["lines"]) if d["exists"] else "—"
        print(f"  {CHAR_DISPLAY.get(slug, slug):<12s} {file_path:<35s} {lines:<7s} {status}")

    # Content overview
    print()
    for slug in chars:
        d = dim_data[slug]
        display = CHAR_DISPLAY.get(slug, slug)
        if not d["exists"]:
            print(f"  {display}: FILE MISSING — create with psy:wave")
            continue
        if d["raw_preview"]:
            print(f"  {display} preview: {d['raw_preview'][:120]}...")

    # Comparison table
    has_content = any(dim_data[s]["exists"] and dim_data[s]["sections"] for s in chars)
    if has_content:
        print(f"\n  {'─'*60}")
        print(f"  Side-by-Side: {dim_key}")
        print(f"  {'─'*60}")
        table_rows = build_comparison_table(chars, dim_data)
        for row in table_rows:
            print(f"  {row}")

    # Clinical observations
    missing = [CHAR_DISPLAY.get(s, s) for s in chars if not dim_data[s]["exists"]]
    present = [CHAR_DISPLAY.get(s, s) for s in chars if dim_data[s]["exists"]]
    print(f"\n  Clinical Observations:")
    if missing:
        print(f"  - Missing data: {', '.join(missing)} — comparison incomplete")
    if len(present) >= 2:
        print(f"  - Compare patterns between {' and '.join(present)} for clinical contrast")
    print(f"  - Use psy:crossref to validate consistency after comparison")


if __name__ == "__main__":
    main()
