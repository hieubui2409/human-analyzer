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
DECISIONS = ROOT / ".claude" / "decisions"
PROFILE_CACHE = ROOT / ".claude" / "profile-cache"

# Framework-partitioned event streams (B2 memory persistence lifecycle)
CHARACTER_EVENTS = SESSION_STATE / "character-events.jsonl"  # PSY
MATERIAL_EVENTS = SESSION_STATE / "material-events.jsonl"  # MAT
CONTENT_EVENTS = SESSION_STATE / "content-events.jsonl"  # CRE
GROWTH_SIGNALS = SESSION_STATE / "growth-signals.jsonl"  # GRO
CASCADE_EVENTS = SESSION_STATE / "cascade-events.jsonl"  # ORC
GOVERNANCE_AUDIT = SESSION_STATE / "governance-audit.jsonl"  # COM

# Route an event to a stream by its event-type prefix (e.g. "PSY.refresh" → PSY).
# Unknown prefixes fall back to CASCADE_EVENTS.
EVENT_STREAMS = {
    "PSY": CHARACTER_EVENTS,
    "MAT": MATERIAL_EVENTS,
    "CRE": CONTENT_EVENTS,
    "GRO": GROWTH_SIGNALS,
    "ORC": CASCADE_EVENTS,
    "COM": GOVERNANCE_AUDIT,
}

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

# Universal profile schema — nested structure (25 base files, same for all characters).
# Per-character relationship files (e.g. relationships/character-a.md) are NOT listed
# here — use list_relationship_files() or list_all_profile_files() for those.
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
    "growth/career-path.md",
    "growth/competencies.md",
    "growth/learning-profile.md",
    "growth/mentoring-map.md",
]

GRO_PROFILE_FILES = [
    "growth/career-path.md",
    "growth/competencies.md",
    "growth/learning-profile.md",
    "growth/mentoring-map.md",
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

# Semantic key → nested profile path (single source of truth for all skills)
PROFILE_BY_CONCEPT = {
    "identity": "identity/core.md",
    "writing_voice": "identity/writing-voice.md",
    "achievements": "identity/achievements.md",
    "media_coverage": "identity/media-coverage.md",
    "formulation": "psychology/formulation.md",
    "defense_mechanisms": "psychology/defense-mechanisms.md",
    "attachment_style": "psychology/attachment-style.md",
    "growth_edges": "psychology/growth-edges.md",
    "core_wounds": "psychology/core-wounds.md",
    "diagnostics": "psychology/diagnostics.md",
    "cultural_formulation": "psychology/cultural-formulation.md",
    "archetype": "psychology/archetype.md",
    "family": "relationships/family.md",
    "timeline": "timeline/overview.md",
    "state_timeline": "timeline/state-timeline.md",
    "traumas": "darkness/traumas.md",
    "strengths_hope": "light/strengths-hope.md",
    "conversations": "evidence/conversations.md",
    "milestones": "milestones.md",
    "index": "INDEX.md",
    "current_state": "CURRENT-STATE.md",
    "career_path": "growth/career-path.md",
    "competencies": "growth/competencies.md",
    "learning_profile": "growth/learning-profile.md",
    "mentoring_map": "growth/mentoring-map.md",
}

# Legacy flat filenames → primary new nested path
LEGACY_TO_NEW_MAP = {
    "INDEX.md": "INDEX.md",
    "CURRENT-STATE.md": "CURRENT-STATE.md",
    "IDENTITY.md": "identity/core.md",
    "SOUL.md": "psychology/formulation.md",
    "DARKNESS.md": "darkness/traumas.md",
    "LIGHT.md": "light/strengths-hope.md",
    "CHARACTERISTIC.md": "psychology/defense-mechanisms.md",
    "TIMELINE.md": "timeline/overview.md",
    "RELATIONSHIPS.md": "relationships/family.md",
    "MILESTONES.md": "milestones.md",
    "WRITING-VOICE.md": "identity/writing-voice.md",
    "ACHIEVEMENTS.md": "identity/achievements.md",
    "MEDIA-COVERAGE.md": "identity/media-coverage.md",
    "INSPIRATION.md": "psychology/growth-edges.md",
    "CONVERSATION.md": "evidence/conversations.md",
}

# Old files that split into multiple new files (for skills needing both)
LEGACY_SPLIT_MAP = {
    "SOUL.md": ["psychology/formulation.md", "psychology/core-wounds.md"],
    "CHARACTERISTIC.md": ["psychology/defense-mechanisms.md", "psychology/attachment-style.md"],
    "TIMELINE.md": ["timeline/overview.md", "timeline/state-timeline.md"],
    "RELATIONSHIPS.md": [
        "relationships/family.md",
        "relationships/character-a.md",
        "relationships/character-b.md",
        "relationships/character-c.md",
        "relationships/network.md",
    ],
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
    """List all existing universal profile files for a character (25 base)."""
    cdir = character_dir(name)
    return [cdir / f for f in PROFILE_FILES if (cdir / f).exists()]


def list_relationship_files(name: str) -> list[Path]:
    """Discover per-character relationship files beyond family.md.

    Only includes .md files in relationships/ that have 'relationship:'
    in their YAML frontmatter (first 500 bytes).
    """
    rel_dir = character_dir(name) / "relationships"
    if not rel_dir.exists():
        return []
    results = []
    for f in sorted(rel_dir.glob("*.md")):
        if f.name == "family.md":
            continue
        head = f.read_text(encoding="utf-8")[:500]
        if "relationship:" in head:
            results.append(f)
    return results


def list_all_profile_files(name: str) -> list[Path]:
    """List universal profile files + per-character relationship files."""
    return list_profile_files(name) + list_relationship_files(name)
