"""Classify and inventory materials by type and processing state."""
import hashlib
import re
from pathlib import Path

from platform_lib.paths import MATERIALS, SCHEMAS, ALL_CHARS, CHAR_DISPLAY
# Canonical frontmatter parser lives in markdown_parser; import here so callers that do
# `from platform_lib.materials_classifier import extract_frontmatter` get the single impl.
from platform_lib.markdown_parser import extract_frontmatter as _mp_extract_frontmatter

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

# Canonical pipeline states ordered from ingestion to retirement.
PROCESSING_STATES = ["raw", "extracted", "analyzed", "validated", "integrated", "archived"]

SCHEMA_PATH = SCHEMAS / "material-schema.yaml"

REQUIRED_FIELDS = [
    "material_id", "character", "material_type", "title",
    "source_category", "source_reliability", "source_creator",
    "captured_date", "processing_status", "confidentiality",
    "last_updated", "updated_by",
]

VALID_MATERIAL_TYPES = [
    "conversation_log", "letter", "interview", "news_article",
    "screenshot", "clinical_note", "observation", "document",
]

VALID_SOURCE_CATEGORIES = ["primary", "secondary", "tertiary", "contextual", "auxiliary"]
VALID_RELIABILITIES = ["high", "medium", "low"]
VALID_CONFIDENTIALITIES = ["public", "shared", "private", "restricted"]

SOURCE_TO_TIER = {
    "primary": 1, "secondary": 2, "tertiary": 3,
    "contextual": 4, "auxiliary": 5,
}


def extract_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a material file. Returns None if absent.

    Delegates to the canonical `markdown_parser.extract_frontmatter` (single home — recursive
    date-stringify + missing-file/non-dict guards) and normalizes its `{}`-on-absent to this
    module's historical `None`-on-absent contract so existing `if fm is None` callers stay stable.
    """
    return _mp_extract_frontmatter(filepath) or None


def tier_for_material(fm: dict) -> int:
    """Canonical evidence tier from a material's frontmatter (MAT-05: tier derives from
    source_category, NOT the authored evidence_tier field). Unknown/missing → T5 (fail-closed).
    Single source so mat:archive, mat:indexer and cre:evidence-scanner can never disagree."""
    return SOURCE_TO_TIER.get((fm or {}).get("source_category", ""), 5)


def validate_material_frontmatter(filepath: Path) -> list[str]:
    """Validate material frontmatter against schema. Returns list of errors."""
    fm = extract_frontmatter(filepath)
    if fm is None:
        return ["no valid YAML frontmatter found"]

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"missing required field: {field}")

    if "material_type" in fm and fm["material_type"] not in VALID_MATERIAL_TYPES:
        errors.append(f"invalid material_type: {fm['material_type']}")
    if "source_category" in fm and fm["source_category"] not in VALID_SOURCE_CATEGORIES:
        errors.append(f"invalid source_category: {fm['source_category']}")
    if "source_reliability" in fm and fm["source_reliability"] not in VALID_RELIABILITIES:
        errors.append(f"invalid source_reliability: {fm['source_reliability']}")
    if "confidentiality" in fm and fm["confidentiality"] not in VALID_CONFIDENTIALITIES:
        errors.append(f"invalid confidentiality: {fm['confidentiality']}")
    if "processing_status" in fm and fm["processing_status"] not in PROCESSING_STATES:
        errors.append(f"invalid processing_status: {fm['processing_status']}")
    if "captured_date" in fm:
        val = str(fm["captured_date"])
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            errors.append(f"captured_date must be ISO date (YYYY-MM-DD), got: {val}")
    if "last_updated" in fm:
        val = str(fm["last_updated"])
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            errors.append(f"last_updated must be ISO date (YYYY-MM-DD), got: {val}")
    if "content_tags" in fm and not isinstance(fm["content_tags"], list):
        errors.append("content_tags must be a list")
    if "psychology_constructs" in fm and not isinstance(fm["psychology_constructs"], list):
        errors.append("psychology_constructs must be a list")

    return errors


def inventory_character_with_frontmatter(slug: str) -> list[dict]:
    """Inventory materials with full frontmatter data."""
    mdir = MATERIALS / slug
    if not mdir.exists():
        return []

    results = []
    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        fm = extract_frontmatter(fpath) or {}
        entry = {
            "path": str(fpath.relative_to(MATERIALS)),
            "name": fpath.name,
            "type": fm.get("material_type", detect_material_type(fpath)),
            "evidence_tier": SOURCE_TO_TIER.get(fm.get("source_category", ""), estimate_evidence_tier(fpath)),
            "processing_status": fm.get("processing_status", "unknown"),
            "source_category": fm.get("source_category", "unknown"),
            "confidentiality": fm.get("confidentiality", "unknown"),
            "has_frontmatter": bool(fm),
            "size_kb": round(fpath.stat().st_size / 1024, 1),
        }
        results.append(entry)
    return results


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
