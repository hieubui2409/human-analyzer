"""Classify and inventory materials by type and processing state."""
import hashlib
import re
from pathlib import Path

from platform_lib.paths import MATERIALS, ALL_CHARS, CHAR_DISPLAY

MATERIAL_TYPES = {
    ".md": "markdown",
    ".txt": "text",
    ".pdf": "pdf",
    ".docx": "document",
    ".xlsx": "spreadsheet",
    ".csv": "data",
    ".json": "data",
    ".yaml": "config",
    ".yml": "config",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".webp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".mp4": "video",
    ".mhtml": "web-archive",
    ".html": "web-page",
}

EVIDENCE_TIERS = {
    1: {"label": "Primary", "patterns": ["interview", "testimony", "letter", "diary", "journal"]},
    2: {"label": "Secondary", "patterns": ["assessment", "evaluation", "report", "clinical"]},
    3: {"label": "Tertiary", "patterns": ["news", "article", "social", "messenger", "facebook", "chat"]},
    4: {"label": "Contextual", "patterns": ["third-party", "hearsay", "rumor", "account"]},
    5: {"label": "Auxiliary", "patterns": ["metadata", "timestamp", "log", "inference"]},
}

PROCESSING_STATES = ["raw", "preprocessed", "extracted", "analyzed", "integrated"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def detect_material_type(filepath: Path) -> str:
    return MATERIAL_TYPES.get(filepath.suffix.lower(), "unknown")


def estimate_evidence_tier(filepath: Path) -> int:
    name_lower = filepath.name.lower()
    stem_lower = filepath.stem.lower()
    for tier, info in EVIDENCE_TIERS.items():
        for pattern in info["patterns"]:
            if pattern in name_lower or pattern in stem_lower:
                return tier
    return 5


def file_hash(filepath: Path) -> str:
    h = hashlib.md5()
    h.update(filepath.read_bytes())
    return h.hexdigest()[:12]


def inventory_character(slug: str) -> list[dict]:
    mdir = MATERIALS / slug
    if not mdir.exists():
        return []

    results = []
    for fpath in sorted(mdir.rglob("*")):
        if fpath.is_dir():
            continue
        entry = {
            "path": str(fpath.relative_to(MATERIALS)),
            "name": fpath.name,
            "type": detect_material_type(fpath),
            "size_kb": round(fpath.stat().st_size / 1024, 1),
            "evidence_tier": estimate_evidence_tier(fpath),
            "hash": file_hash(fpath),
        }
        results.append(entry)
    return results


def inventory_all() -> dict:
    report = {}
    for slug in ALL_CHARS:
        report[slug] = inventory_character(slug)
    return report


def print_inventory(report: dict):
    total_files = 0
    total_size = 0

    for slug, items in report.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n{'='*60}")
        print(f"  {display} ({slug}) — {len(items)} files")
        print(f"{'='*60}")

        for item in items:
            total_files += 1
            total_size += item["size_kb"]
            tier_label = EVIDENCE_TIERS.get(item["evidence_tier"], {}).get("label", "?")
            print(f"  [{item['type']:12s}] T{item['evidence_tier']}({tier_label:9s}) {item['size_kb']:8.1f}KB  {item['name']}")

    print(f"\n{'='*60}")
    print(f"  TOTAL: {total_files} files | {total_size:.1f} KB")
    print(f"{'='*60}")


if __name__ == "__main__":
    import sys

    if "--json" in sys.argv:
        import json
        print(json.dumps(inventory_all(), indent=2, ensure_ascii=False))
    else:
        print_inventory(inventory_all())
