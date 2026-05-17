"""Migrate legacy flat profile files to new nested universal structure.

Usage:
    python3 pmc-migrate-flat-profiles-to-nested-structure.py [--dry-run] [--character SLUG]

Handles:
  - Moves flat files to nested paths per LEGACY_TO_NEW_MAP
  - Merges IDENTITY.md + CHARACTERISTIC.md → identity/core.md
  - Generates skeleton for files that don't exist in legacy
  - Injects/updates YAML frontmatter on migrated files
  - Creates CURRENT-STATE.md and state-timeline.md as new files
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from platform_lib.paths import (
    PROFILES,
    ALL_CHARS,
    CHAR_DISPLAY,
    LEGACY_TO_NEW_MAP,
    PROFILE_FILES,
)

TODAY = date.today().isoformat()

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

DOMAIN_MAP = {
    "INDEX.md": "root",
    "CURRENT-STATE.md": "root",
    "milestones.md": "root",
    "identity/core.md": "identity",
    "identity/writing-voice.md": "identity",
    "identity/achievements.md": "identity",
    "identity/media-coverage.md": "identity",
    "psychology/core-wounds.md": "psychology",
    "psychology/defense-mechanisms.md": "psychology",
    "psychology/attachment-style.md": "psychology",
    "psychology/growth-edges.md": "psychology",
    "psychology/formulation.md": "psychology",
    "psychology/diagnostics.md": "psychology",
    "psychology/cultural-formulation.md": "psychology",
    "psychology/archetype.md": "psychology",
    "relationships/family.md": "relationships",
    "timeline/overview.md": "timeline",
    "timeline/state-timeline.md": "timeline",
    "darkness/traumas.md": "darkness",
    "light/strengths-hope.md": "light",
    "evidence/conversations.md": "evidence",
}

TYPE_MAP = {
    "INDEX.md": "index",
    "CURRENT-STATE.md": "snapshot",
    "milestones.md": "data",
    "identity/core.md": "narrative",
    "identity/writing-voice.md": "analysis",
    "identity/achievements.md": "data",
    "identity/media-coverage.md": "data",
    "psychology/core-wounds.md": "analysis",
    "psychology/defense-mechanisms.md": "analysis",
    "psychology/attachment-style.md": "analysis",
    "psychology/growth-edges.md": "analysis",
    "psychology/formulation.md": "analysis",
    "psychology/diagnostics.md": "analysis",
    "psychology/cultural-formulation.md": "analysis",
    "psychology/archetype.md": "analysis",
    "relationships/family.md": "narrative",
    "timeline/overview.md": "data",
    "timeline/state-timeline.md": "analysis",
    "darkness/traumas.md": "analysis",
    "light/strengths-hope.md": "analysis",
    "evidence/conversations.md": "data",
}

MERGE_TARGETS = {
    "identity/core.md": ["IDENTITY.md", "CHARACTERISTIC.md"],
}

SKELETON_TEMPLATE = """---
character: {slug}
domain: {domain}
type: {ftype}
tags: []
references: []
cross_characters: []
last_updated: {today}
updated_by: pmc:migrate
confidence: unverified
---

# {title}

> Empty skeleton — awaiting content.
"""


def inject_frontmatter(content: str, slug: str, relpath: str) -> str:
    domain = DOMAIN_MAP.get(relpath, "root")
    ftype = TYPE_MAP.get(relpath, "analysis")

    fm_block = f"""---
character: {slug}
domain: {domain}
type: {ftype}
tags: []
references: []
cross_characters: []
last_updated: {TODAY}
updated_by: pmc:migrate
confidence: medium
---

"""
    stripped = FRONTMATTER_RE.sub("", content).lstrip("\n")
    return fm_block + stripped


def merge_files(sources: list[Path], slug: str, relpath: str) -> str:
    parts = []
    for src in sources:
        if src.exists():
            text = src.read_text(encoding="utf-8")
            text = FRONTMATTER_RE.sub("", text).strip()
            parts.append(f"<!-- Source: {src.name} -->\n{text}")
    merged = "\n\n---\n\n".join(parts)
    return inject_frontmatter(merged, slug, relpath)


def title_from_path(relpath: str) -> str:
    name = relpath.split("/")[-1]
    return name.replace(".md", "").replace("-", " ").title()


def migrate_character(slug: str, dry_run: bool = False) -> dict:
    display = CHAR_DISPLAY.get(slug, slug)
    char_dir = PROFILES / slug
    stats = {"moved": 0, "merged": 0, "skeleton": 0, "skipped": 0}

    if not char_dir.exists():
        print(f"  ERROR: {char_dir} not found")
        return stats

    print(f"\n{'='*60}")
    print(f"  Migrating {display} ({slug})")
    print(f"{'='*60}")

    handled_sources = set()

    for relpath in PROFILE_FILES:
        target = char_dir / relpath

        if target.exists() and "/" in relpath:
            print(f"  SKIP (exists): {relpath}")
            stats["skipped"] += 1
            continue

        target.parent.mkdir(parents=True, exist_ok=True)

        if relpath in MERGE_TARGETS:
            sources = [char_dir / s for s in MERGE_TARGETS[relpath]]
            existing = [s for s in sources if s.exists()]
            if existing:
                content = merge_files(existing, slug, relpath)
                if not dry_run:
                    target.write_text(content, encoding="utf-8")
                for s in existing:
                    handled_sources.add(s.name)
                print(f"  MERGE: {' + '.join(s.name for s in existing)} → {relpath}")
                stats["merged"] += 1
                continue

        reverse_map = {v: k for k, v in LEGACY_TO_NEW_MAP.items() if v == relpath}
        legacy_names = list(reverse_map.values())
        moved = False
        for legacy_name in legacy_names:
            if legacy_name in handled_sources:
                continue
            legacy_path = char_dir / legacy_name
            if legacy_path.exists() and not target.exists():
                content = legacy_path.read_text(encoding="utf-8")
                content = inject_frontmatter(content, slug, relpath)
                if not dry_run:
                    target.write_text(content, encoding="utf-8")
                handled_sources.add(legacy_name)
                print(f"  MOVE: {legacy_name} → {relpath}")
                stats["moved"] += 1
                moved = True
                break

        if not moved and not target.exists():
            content = SKELETON_TEMPLATE.format(
                slug=slug,
                domain=DOMAIN_MAP.get(relpath, "root"),
                ftype=TYPE_MAP.get(relpath, "analysis"),
                today=TODAY,
                title=title_from_path(relpath),
            )
            if not dry_run:
                target.write_text(content, encoding="utf-8")
            print(f"  SKELETON: {relpath}")
            stats["skeleton"] += 1

    (char_dir / "psychology" / "case-studies").mkdir(parents=True, exist_ok=True)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Migrate flat profiles to nested structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--character", default=None, help="Migrate only this character slug")
    args = parser.parse_args()

    chars = [args.character] if args.character else ALL_CHARS
    total = {"moved": 0, "merged": 0, "skeleton": 0, "skipped": 0}

    for slug in chars:
        stats = migrate_character(slug, dry_run=args.dry_run)
        for k in total:
            total[k] += stats.get(k, 0)

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{prefix}Migration complete:")
    print(f"  Moved:    {total['moved']}")
    print(f"  Merged:   {total['merged']}")
    print(f"  Skeleton: {total['skeleton']}")
    print(f"  Skipped:  {total['skipped']}")


if __name__ == "__main__":
    main()
