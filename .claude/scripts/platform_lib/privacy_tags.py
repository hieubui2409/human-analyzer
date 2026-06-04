"""Privacy-tag scanning shared between cre:privacy-guard scripts.

Single source for the Rule-09 tag grammar ([PRIVATE], [CONFIDENTIAL: {person}], [ANONYMIZE])
so the name-extractor and the asset scanner cannot drift on tag syntax. Walks the nested
profile tree (rglob) — confidential tags live in identity/, relationships/, darkness/, etc.,
not just the 3 root files.
"""
import re
from pathlib import Path

from .paths import PROFILES, ALL_CHARS, CHAR_DISPLAY, character_dir

# [CONFIDENTIAL: SomeName] / [CONFIDENTIAL:SomeName] — captures the restricted person name.
CONFIDENTIAL_TAG_RE = re.compile(r"\[CONFIDENTIAL:\s*([^\]]+)\]", re.IGNORECASE)
# Bare privacy markers with no name payload.
PRIVATE_TAG_RE = re.compile(r"\[(PRIVATE|ANONYMIZE)\]", re.IGNORECASE)


def scan_privacy_tags(filepath: Path, char_slug: str) -> list[dict]:
    """Scan one profile file → list of {character, file, line_no, tag_type, restricted_name, context}."""
    if not filepath.exists():
        return []
    display = CHAR_DISPLAY.get(char_slug, char_slug)
    results = []
    for i, line in enumerate(filepath.read_text(encoding="utf-8").splitlines(), 1):
        for m in CONFIDENTIAL_TAG_RE.finditer(line):
            results.append({
                "character": display, "file": filepath.name, "line_no": i,
                "tag_type": "CONFIDENTIAL", "restricted_name": m.group(1).strip(),
                "context": line.strip()[:100],
            })
        for m in PRIVATE_TAG_RE.finditer(line):
            results.append({
                "character": display, "file": filepath.name, "line_no": i,
                "tag_type": m.group(1).upper(), "restricted_name": "(unlabeled private content)",
                "context": line.strip()[:100],
            })
    return results


def load_confidential_names(characters: list[str] | None = None) -> set[str]:
    """Collect every [CONFIDENTIAL: {name}] person across the nested profile tree.

    These are the names that MUST NOT appear verbatim in published assets (Rule 09).
    """
    names: set[str] = set()
    for slug in (characters or ALL_CHARS):
        cdir = character_dir(slug)
        if not cdir.exists():
            continue
        for md in cdir.rglob("*.md"):
            for entry in scan_privacy_tags(md, slug):
                if entry["tag_type"] == "CONFIDENTIAL":
                    names.add(entry["restricted_name"])
    return names
