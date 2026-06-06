"""Detect which connected characters and profile sections need review after a profile change."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, GRAPH, PROFILES, resolve_character, list_relationship_files
from platform_lib.markdown_parser import parse_table_rows

# Section → affected sections in connected characters (by connection strength)
PROPAGATION_MAP = {
    "relationships/family.md": {
        "high": ["relationships/family.md", "CURRENT-STATE.md"],
        "medium": ["relationships/family.md"],
        "low": [],
    },
    "timeline/overview.md": {
        "high": ["timeline/overview.md", "milestones.md"],
        "medium": ["timeline/overview.md"],
        "low": ["timeline/overview.md"],
    },
    "timeline/state-timeline.md": {
        "high": ["timeline/state-timeline.md", "CURRENT-STATE.md"],
        "medium": ["CURRENT-STATE.md"],
        "low": [],
    },
    "psychology/attachment-style.md": {
        "high": ["relationships/family.md", "psychology/attachment-style.md"],
        "medium": ["relationships/family.md"],
        "low": [],
    },
    "psychology/core-wounds.md": {
        "high": ["relationships/family.md", "psychology/formulation.md"],
        "medium": ["relationships/family.md"],
        "low": [],
    },
    "CURRENT-STATE.md": {
        "high": ["relationships/family.md", "CURRENT-STATE.md"],
        "medium": ["CURRENT-STATE.md"],
        "low": [],
    },
    "identity/core.md": {
        "high": ["INDEX.md", "identity/core.md"],
        "medium": ["INDEX.md"],
        "low": ["INDEX.md"],
    },
    "darkness/traumas.md": {
        "high": ["relationships/family.md", "psychology/formulation.md"],
        "medium": ["relationships/family.md"],
        "low": [],
    },
}

def _load_connections() -> dict:
    """Derive the source→{target: strength} map from the dyad-strength table in the KG
    (`docs/graph/relational-dynamics.md`) — the single source of relational truth — instead of a
    hand-maintained literal that drifts from it. Table rows contain display-name pairs separated
    by a U+2194 (↔) character and a strength column (high/medium/low).
    Symmetric (a↔b). Falls back to an empty map (no cross-char propagation) if the graph is absent.
    """
    graph_file = GRAPH / "relational-dynamics.md"
    if not graph_file.exists():
        return {}
    display_to_slug = {disp: slug for slug, disp in CHAR_DISPLAY.items()}
    strengths = {"high", "medium", "low"}
    conn: dict = {}
    for cells in parse_table_rows(graph_file.read_text(encoding="utf-8")):
        if "↔" not in cells[0]:
            continue
        strength = next((c.strip().lower() for c in reversed(cells) if c.strip().lower() in strengths), None)
        if not strength:
            continue
        parts = [p.strip() for p in cells[0].split("↔")]
        if len(parts) != 2:
            continue
        # Display names in table cells resolve via the roster-derived map — corpus-agnostic.
        a, b = display_to_slug.get(parts[0]), display_to_slug.get(parts[1])
        if a and b:
            conn.setdefault(a, {})[b] = strength
            conn.setdefault(b, {})[a] = strength
    return conn


# Connection map: source → {target: strength}, derived from the KG (single source of truth).
CONNECTIONS = _load_connections()


def _mirror_relationship_targets(source_slug: str, section: str | None) -> list[dict]:
    """When a cross-relationship file changes, propagate to the mirror file in the other character."""
    targets = []
    if section and section.startswith("relationships/") and section != "relationships/family.md":
        target_slug_hint = section.replace("relationships/", "").replace(".md", "")
        if target_slug_hint in ALL_CHARS:
            mirror_file = f"relationships/{source_slug}.md"
            mirror_path = PROFILES / target_slug_hint / mirror_file
            targets.append({
                "priority": "HIGH",
                "target_character": target_slug_hint,
                "target_display": CHAR_DISPLAY.get(target_slug_hint, target_slug_hint),
                "file": mirror_file,
                "file_exists": mirror_path.exists(),
                "source_section": section,
                "connection_strength": "high",
                "reason": f"{CHAR_DISPLAY.get(source_slug, source_slug)} {section} changed → review mirror {mirror_file}",
            })
    elif section is None:
        # Check all cross-relationship files for this character
        for rel_file in list_relationship_files(source_slug):
            rel_name = rel_file.stem  # e.g. "character-b"
            if rel_name in ALL_CHARS:
                mirror_file = f"relationships/{source_slug}.md"
                mirror_path = PROFILES / rel_name / mirror_file
                targets.append({
                    "priority": "HIGH",
                    "target_character": rel_name,
                    "target_display": CHAR_DISPLAY.get(rel_name, rel_name),
                    "file": mirror_file,
                    "file_exists": mirror_path.exists(),
                    "source_section": f"relationships/{rel_name}.md",
                    "connection_strength": "high",
                    "reason": f"{CHAR_DISPLAY.get(source_slug, source_slug)} relationships/{rel_name}.md → review mirror {mirror_file}",
                })
    return targets


def get_targets(source_slug: str, section: str | None) -> list[dict]:
    """Return propagation targets for a source character and optional section."""
    connections = CONNECTIONS.get(source_slug, {})
    targets = []

    sections_to_check = [section] if section else list(PROPAGATION_MAP.keys())

    for target_slug, strength in connections.items():
        target_dir = PROFILES / target_slug
        for sec in sections_to_check:
            affected = PROPAGATION_MAP.get(sec, {}).get(strength, [])
            for affected_file in affected:
                target_file = target_dir / affected_file
                exists = target_file.exists()
                priority = "HIGH" if strength == "high" else ("MEDIUM" if strength == "medium" else "LOW")
                targets.append({
                    "priority": priority,
                    "target_character": target_slug,
                    "target_display": CHAR_DISPLAY.get(target_slug, target_slug),
                    "file": affected_file,
                    "file_exists": exists,
                    "source_section": sec,
                    "connection_strength": strength,
                    "reason": f"{CHAR_DISPLAY.get(source_slug, source_slug)} {sec} changed → review {affected_file}",
                })

    # Cross-relationship mirror propagation
    targets.extend(_mirror_relationship_targets(source_slug, section))

    # Deduplicate by (target, file)
    seen = set()
    deduped = []
    for t in targets:
        key = (t["target_character"], t["file"])
        if key not in seen:
            seen.add(key)
            deduped.append(t)

    # Sort by priority
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    deduped.sort(key=lambda x: order[x["priority"]])
    return deduped


def main():
    parser = argparse.ArgumentParser(
        description="Detect propagation targets after profile change"
    )
    parser.add_argument("--character", "-c", required=True, help="Source character slug or alias")
    parser.add_argument("--section", "-s", help="Specific section that changed (optional)")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    source_slug = resolve_character(args.character)
    source_display = CHAR_DISPLAY.get(source_slug, source_slug)

    section = args.section
    # Normalize section argument to file path format
    if section and not section.endswith(".md"):
        # Try to match partial name
        for known in PROPAGATION_MAP:
            if section.replace("-", "_") in known.replace("/", "_").replace(".md", ""):
                section = known
                break
        else:
            section = None  # Unknown section — check all

    targets = get_targets(source_slug, section)

    if args.json_out:
        print(json.dumps({
            "source": source_slug,
            "section": args.section,
            "targets": targets,
        }, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*70}")
    print(f"  Propagation Analysis: {source_display} ({source_slug})")
    print(f"{'='*70}")
    print(f"  Changed section: {args.section or 'unspecified — checking all sections'}")
    print()

    if not targets:
        print("  No propagation targets found.")
        return

    print(f"  {'Priority':<8s} {'Target':<12s} {'File':<35s} {'Reason'}")
    print(f"  {'-'*8} {'-'*12} {'-'*35} {'-'*35}")
    for t in targets:
        exists_marker = "" if t["file_exists"] else " [MISSING]"
        print(f"  {t['priority']:<8s} {t['target_display']:<12s} {t['file'] + exists_marker:<35s} {t['reason']}")

    print(f"\n  TOTAL: {len(targets)} propagation target(s)")

    # Group recommended actions
    print("\n  Recommended Actions:")
    for i, t in enumerate(targets, 1):
        action = "Update" if t["file_exists"] else "Create"
        print(f"  {i}. {action} {t['target_display']}/{t['file']} — {t['reason']}")

    # Use CHAR_DISPLAY for the slug label — safe for any slug length (avoids IndexError on 2-word slugs)
    source_label = CHAR_DISPLAY.get(source_slug, source_slug)
    print(f"\n  Next step: run `psy:crossref --pair {source_label} <target>` after updates")


if __name__ == "__main__":
    main()
