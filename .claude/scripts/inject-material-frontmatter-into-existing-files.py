"""Inject MAT-compliant YAML frontmatter into existing material .md files.

Usage:
    python3 inject-material-frontmatter-into-existing-files.py [--dry-run] [--character SLUG]

Scans docs/materials/{character}/ for .md files without frontmatter,
infers metadata from filename/content, and injects standardized frontmatter.
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from platform_lib.paths import MATERIALS, ALL_CHARS, CHAR_DISPLAY
from platform_lib.materials_classifier import detect_material_type, estimate_evidence_tier

TODAY = date.today().isoformat()
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

MATERIAL_TYPE_PATTERNS = {
    "conversation_log": ["log-", "chat-", "tin nhắn", "messenger", "conversation"],
    "letter": ["letter", "thư", "recommendation"],
    "interview": ["interview", "phỏng vấn", "hồ sơ phỏng vấn"],
    "news_article": ["báo", "tsđt", "news", "tuổi trẻ"],
    "clinical_note": ["analysis", "phân tích", "psychological", "framework", "prognosis"],
    "observation": ["observation", "nhận xét"],
    "document": ["cv", "reference", "hồ sơ nhân vật", "report", "báo cáo"],
    "screenshot": ["screenshot"],
}

SOURCE_CATEGORY_PATTERNS = {
    "primary": ["log-", "chat-", "self-reflection", "tin nhắn", "letter", "thư"],
    "secondary": ["analysis", "phân tích", "psychological", "framework", "prognosis", "clinical"],
    "tertiary": ["báo", "tsđt", "news", "gemini", "gg ai studio"],
    "contextual": ["recommendation", "reference", "giới thiệu"],
}


def infer_material_type(filepath: Path) -> str:
    name_lower = filepath.name.lower()
    stem_lower = filepath.stem.lower()
    for mtype, patterns in MATERIAL_TYPE_PATTERNS.items():
        for p in patterns:
            if p in name_lower or p in stem_lower:
                return mtype
    return "document"


def infer_source_category(filepath: Path) -> str:
    name_lower = filepath.name.lower()
    for cat, patterns in SOURCE_CATEGORY_PATTERNS.items():
        for p in patterns:
            if p in name_lower:
                return cat
    return "tertiary"


def infer_date_from_filename(filepath: Path) -> str | None:
    m = re.search(r"(\d{2})(\d{4})", filepath.stem)
    if m:
        month, year = m.group(1), m.group(2)
        return f"{year}-{month}-01"
    m = re.search(r"(\d{4})-(\d{2})", filepath.stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-01"
    m = re.search(r"(\d{2})-(\d{4})", filepath.stem)
    if m:
        return f"{m.group(2)}-{m.group(1)}-01"
    return None


def extract_character_from_path(filepath: Path) -> str:
    parts = filepath.relative_to(MATERIALS).parts
    return parts[0] if parts else "unknown"


def generate_material_id(character: str, index: int) -> str:
    slug = character.upper().replace("-", "_")
    return f"{slug}_MAT_{index:03d}"


def has_frontmatter(text: str) -> bool:
    return bool(FRONTMATTER_RE.match(text))


def build_frontmatter(filepath: Path, character: str, index: int) -> str:
    mat_type = infer_material_type(filepath)
    source_cat = infer_source_category(filepath)
    captured = infer_date_from_filename(filepath) or TODAY
    title = filepath.stem.replace("-", " ").replace("_", " ")

    reliability = {"primary": "high", "secondary": "high", "tertiary": "medium", "contextual": "low", "auxiliary": "low"}

    fm = f"""---
material_id: {generate_material_id(character, index)}
character: {character}
material_type: {mat_type}
title: "{title}"
source_category: {source_cat}
source_reliability: {reliability.get(source_cat, "medium")}
source_creator: unknown
captured_date: {captured}
processing_status: raw
confidentiality: private
last_updated: {TODAY}
updated_by: mat:injector
content_tags: []
psychology_constructs: []
references: []
cross_characters: []
---

"""
    return fm


def inject_character(character: str, dry_run: bool = False) -> dict:
    mdir = MATERIALS / character
    if not mdir.exists():
        return {"injected": 0, "skipped": 0}

    stats = {"injected": 0, "skipped": 0}
    md_files = sorted(mdir.rglob("*.md"))

    for i, filepath in enumerate(md_files, start=1):
        text = filepath.read_text(encoding="utf-8")
        if has_frontmatter(text):
            print(f"  SKIP (has frontmatter): {filepath.relative_to(MATERIALS)}")
            stats["skipped"] += 1
            continue

        fm = build_frontmatter(filepath, character, i)
        if not dry_run:
            filepath.write_text(fm + text, encoding="utf-8")
        print(f"  INJECT: {filepath.relative_to(MATERIALS)}")
        stats["injected"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Inject MAT frontmatter into material files")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--character", default=None)
    args = parser.parse_args()

    chars = [args.character] if args.character else ALL_CHARS
    total = {"injected": 0, "skipped": 0}

    for slug in chars:
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n{'='*60}")
        print(f"  {display} ({slug})")
        print(f"{'='*60}")
        stats = inject_character(slug, dry_run=args.dry_run)
        for k in total:
            total[k] += stats.get(k, 0)

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{prefix}Done: {total['injected']} injected, {total['skipped']} skipped")


if __name__ == "__main__":
    main()
