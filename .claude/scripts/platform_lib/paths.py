"""Project path constants and discovery utilities for PMC framework."""
import os
from pathlib import Path


def find_project_root() -> Path:
    """Walk up from CWD or env var to find CLAUDE.md."""
    root = os.environ.get("PMC_PROJECT_ROOT")
    if root:
        return Path(root)
    p = Path.cwd()
    for _ in range(10):
        if (p / "CLAUDE.md").exists() and (p / "docs" / "profiles").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    raise FileNotFoundError("Cannot find project root (no CLAUDE.md + docs/profiles found)")


ROOT = find_project_root()
PROFILES = ROOT / "docs" / "profiles"
MATERIALS = ROOT / "docs" / "materials"
REFERENCES = ROOT / "docs" / "references"
GRAPH = ROOT / "docs" / "graph"
RULES = ROOT / "docs" / "rules"
SCHEMAS = ROOT / ".claude" / "schemas"
ASSETS = ROOT / "assets"
PLANS = ROOT / "plans"
REPORTS = PLANS / "reports"
SKILLS = ROOT / ".claude" / "skills"
SESSION_STATE = ROOT / ".claude" / "session-state"
PROFILE_CACHE = ROOT / ".claude" / "profile-cache"

CHARACTERS = {
    "hieu": "character-a",
    "hiếu": "character-a",
    "character-a": "character-a",
    "hoa": "character-b",
    "hòa": "character-b",
    "character-b": "character-b",
    "chien": "character-c",
    "chiến": "character-c",
    "character-c": "character-c",
}

ALL_CHARS = ["character-a", "character-b", "character-c"]
CHAR_DISPLAY = {"character-a": "Nhân vật A", "character-b": "Nhân vật B", "character-c": "Nhân vật C"}

# Universal profile schema — nested structure
PROFILE_FILES = [
    "INDEX.md",
    "CURRENT-STATE.md",
    "milestones.md",
    "identity/core.md",
    "identity/writing-voice.md",
    "identity/achievements.md",
    "identity/media-coverage.md",
    "psychology/core-wounds.md",
    "psychology/defense-mechanisms.md",
    "psychology/attachment-style.md",
    "psychology/growth-edges.md",
    "psychology/formulation.md",
    "psychology/diagnostics.md",
    "psychology/cultural-formulation.md",
    "psychology/archetype.md",
    "relationships/family.md",
    "timeline/overview.md",
    "timeline/state-timeline.md",
    "darkness/traumas.md",
    "light/strengths-hope.md",
    "evidence/conversations.md",
]

CLINICAL_PROFILE_FILES = [
    "psychology/core-wounds.md",
    "psychology/defense-mechanisms.md",
    "psychology/attachment-style.md",
    "psychology/formulation.md",
    "psychology/diagnostics.md",
    "psychology/cultural-formulation.md",
    "darkness/traumas.md",
    "light/strengths-hope.md",
    "relationships/family.md",
]

# Maps legacy flat filenames → new nested paths (used by migration script)
LEGACY_TO_NEW_MAP = {
    "INDEX.md": "INDEX.md",
    "IDENTITY.md": "identity/core.md",
    "SOUL.md": "psychology/core-wounds.md",
    "CHARACTERISTIC.md": "identity/core.md",
    "TIMELINE.md": "timeline/overview.md",
    "RELATIONSHIPS.md": "relationships/family.md",
    "DARKNESS.md": "darkness/traumas.md",
    "LIGHT.md": "light/strengths-hope.md",
    "MILESTONES.md": "milestones.md",
    "ACHIEVEMENTS.md": "identity/achievements.md",
    "MEDIA-COVERAGE.md": "identity/media-coverage.md",
    "WRITING-VOICE.md": "identity/writing-voice.md",
    "INSPIRATION.md": "psychology/growth-edges.md",
    "CONVERSATION.md": "evidence/conversations.md",
}


def resolve_character(name: str) -> str:
    """Resolve alias to canonical directory name."""
    key = name.lower().strip()
    if key in CHARACTERS:
        return CHARACTERS[key]
    raise ValueError(f"Unknown character: {name!r}. Known: {list(CHARACTERS.keys())}")


def character_dir(name: str) -> Path:
    return PROFILES / resolve_character(name)


def materials_dir(name: str) -> Path:
    return MATERIALS / resolve_character(name)


def list_profile_files(name: str) -> list[Path]:
    """List all existing profile files for a character."""
    cdir = character_dir(name)
    return [cdir / f for f in PROFILE_FILES if (cdir / f).exists()]
