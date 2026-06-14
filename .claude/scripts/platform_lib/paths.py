"""Project path constants and discovery utilities for PMC framework."""
import itertools
import os
import unicodedata
from pathlib import Path


def find_project_root() -> Path:
    """Walk up from CWD or env var to find CLAUDE.md."""
    root = os.environ.get("PMC_PROJECT_ROOT")
    if root:
        return Path(root)
    p = Path.cwd()
    for _ in range(10):
        # CLAUDE.md alone is ambiguous (a nested checkout or tool dir may carry a stray one), so it
        # must be paired with a second structural marker. Either marker disambiguates the real root:
        #   - docs/profiles  → a populated source repo (the character corpus), OR
        #   - .claude/skills/_framework-shared → a toolkit-only deployment (public repo / consumer
        #     pack) where the corpus is intentionally absent.
        if (p / "CLAUDE.md").exists() and (
            (p / "docs" / "profiles").exists()
            or (p / ".claude" / "skills" / "_framework-shared").exists()
        ):
            return p
        if p.parent == p:
            break
        p = p.parent
    raise FileNotFoundError("Cannot find project root (no CLAUDE.md + corpus/toolkit marker found)")


ROOT = find_project_root()
PROFILES = ROOT / "docs" / "profiles"
MATERIALS = ROOT / "docs" / "materials"
REFERENCES = ROOT / "docs" / "references"
RUBRICS = ROOT / "docs" / "rubrics"  # EVL shared rubric library (versioned, character-agnostic)
GRAPH = ROOT / "docs" / "graph"
RULES = ROOT / "docs" / "rules"
SCHEMAS = ROOT / ".claude" / "schemas"
ASSETS = ROOT / "assets"
PLANS = ROOT / "plans"
REPORTS = PLANS / "reports"
SKILLS = ROOT / ".claude" / "skills"
PLATFORM_LIB = ROOT / ".claude" / "scripts" / "platform_lib"  # shared utility package dir
SESSION_STATE = ROOT / ".claude" / "session-state"  # mutable session STATE (json), not event sinks
# Consolidated observability sink root (all JSONL streams). CK_TELEMETRY_DIR env
# overrides it (tests point it at a tmp dir to isolate sink writes).
TELEMETRY = Path(os.environ["CK_TELEMETRY_DIR"]) if os.environ.get("CK_TELEMETRY_DIR") else ROOT / ".claude" / "telemetry"
DECISIONS = ROOT / ".claude" / "decisions"

# --- Consolidated cache root (one home for cache LOCATION; split by durability) ---
# Debated decision (user-confirmed): a single cache root, two subtrees by durability class:
#   committed/ — reproducible, content-addressed verdict/judgment caches. TRACKED + committed
#                (key = content hash → stable for identical content; reuse + audit trail). Stores
#                verdict labels/scores/refs ONLY — never raw profile text (confidentiality).
#   runtime/   — telemetry-adjacent + cheap-to-rebuild caches (profile-lite). GITIGNORED
#                (machine-local, high-churn; never committed).
# CK_CACHE_DIR overrides the root (tests point it at a tmp dir to isolate cache writes).
CACHE_ROOT = Path(os.environ["CK_CACHE_DIR"]) if os.environ.get("CK_CACHE_DIR") else ROOT / ".claude" / "cache"


def cache_root() -> Path:
    """The single cache root. Callers prefer committed_cache_dir / runtime_cache_dir."""
    return CACHE_ROOT


def committed_cache_dir(name: str) -> Path:
    """A tracked, committed cache subtree (reproducible content-addressed caches, no PII).

    Created on demand. Commit policy lives in .gitignore (committed/ is tracked)."""
    d = CACHE_ROOT / "committed" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def runtime_cache_dir(name: str) -> Path:
    """A gitignored runtime cache subtree (cheap-rebuild / machine-local caches)."""
    d = CACHE_ROOT / "runtime" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def project_dir() -> Path:
    """Claude Code's per-project runtime dir: ~/.claude/projects/{encoded-root}.

    The slug is the absolute project root with '/' → '-' (Claude Code's project-id convention),
    so it resolves dynamically per checkout — never a hardcoded machine path. One home for the
    slug derivation; memory_dir / session-forensics derive off this."""
    enc = str(ROOT).replace("/", "-")
    return Path.home() / ".claude" / "projects" / enc


def memory_dir() -> Path:
    """Claude Code's per-project persistent memory dir: {project_dir}/memory.

    CK_MEMORY_DIR overrides it (tests point it at a tmp dir to isolate memory writes)."""
    env = os.environ.get("CK_MEMORY_DIR")
    if env:
        return Path(env)
    return project_dir() / "memory"


def sessions_dir() -> Path:
    """Claude Code's per-project session-JSONL dir (== project_dir).

    CK_SESSIONS_DIR overrides it (tests point it at a tmp dir)."""
    env = os.environ.get("CK_SESSIONS_DIR")
    if env:
        return Path(env)
    return project_dir()


# profile-lite is a cheap-to-rebuild compression cache → runtime subtree.
PROFILE_CACHE = CACHE_ROOT / "runtime" / "profile-lite"

# Framework-partitioned event streams (B2 memory persistence lifecycle).
# Files stay SEPARATE (partition preserved); the directory is consolidated under
# TELEMETRY so the dashboard + forensics parser read one root.
CHARACTER_EVENTS = TELEMETRY / "character-events.jsonl"  # PSY
MATERIAL_EVENTS = TELEMETRY / "material-events.jsonl"  # MAT
CONTENT_EVENTS = TELEMETRY / "content-events.jsonl"  # CRE
GROWTH_SIGNALS = TELEMETRY / "growth-signals.jsonl"  # GRO
CASCADE_EVENTS = TELEMETRY / "cascade-events.jsonl"  # ORC
GOVERNANCE_AUDIT = TELEMETRY / "governance-audit.jsonl"  # COM
EVAL_EVENTS = TELEMETRY / "evl-events.jsonl"  # EVL

# Other consolidated JSONL sinks (signals + audits), same root.
INSTINCTS = TELEMETRY / "instincts.jsonl"  # continuous-learning store (B3)
OBSERVATIONS = TELEMETRY / "observations.jsonl"  # passive cross-framework signals (B3)
GATEGUARD_AUDIT = TELEMETRY / "gateguard-audit.jsonl"  # profile-protection audit trail
PRIVACY_AUDIT = TELEMETRY / "privacy-audit.jsonl"  # cre:privacy-guard audit trail

# Route an event to a stream by its event-type prefix (e.g. "PSY.refresh" → PSY).
# Unknown prefixes fall back to CASCADE_EVENTS.
EVENT_STREAMS = {
    "PSY": CHARACTER_EVENTS,
    "MAT": MATERIAL_EVENTS,
    "CRE": CONTENT_EVENTS,
    "GRO": GROWTH_SIGNALS,
    "ORC": CASCADE_EVENTS,
    "COM": GOVERNANCE_AUDIT,
    "EVL": EVAL_EVENTS,
}

# --- Character roster: DATA, not code. Loaded from docs/profiles/characters.yaml ---------------
# The roster names are real-character PII, so they live in characters.yaml (under docs/profiles/,
# which the pack's safety_filter excludes from every release). The shipped paths.py carries ZERO
# names; the running repo resolves characters from the yaml. Public API is byte-identical to the
# pre-externalization literals (CHARACTERS / ALL_CHARS / CHAR_DISPLAY / CHAR_SEARCH_ALIASES).


def _asciifold(s: str) -> str:
    """Strip Vietnamese/Latin diacritics to ASCII (e.g. ế→e, ò→o, đ→d). stdlib-only."""
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _load_roster(profiles_dir: Path):
    """Resolve the roster structures from ``profiles_dir``. Pure, side-effect-free, NEVER raises.

    Returns ``(CHARACTERS, ALL_CHARS, CHAR_DISPLAY, CHAR_SEARCH_ALIASES)``.

    Resolution chain:
      1. ``profiles_dir/characters.yaml`` — the curated roster (real repo + ALT projects that ship one).
      2. discovery from ``profiles_dir/*/INDEX.md`` dirs (slug=display, identity aliases) when the yaml
         is missing / empty / corrupt — keeps any synthetic corpus (e2e fixtures) working code-free.
      3. empty dicts — toolkit-only consumer pack with no live corpus.

    The resolution map (CHARACTERS) is derived from ``{slug, display.lower(), asciifold(display).lower()}``
    ONLY — never from ``aliases``. Alias forms (IME-typo / full name) are free-text SEARCH terms in
    CHAR_SEARCH_ALIASES; adding them as resolution keys would make resolve_character() accept inputs that
    today raise, silently widening the frozen API. The ``import yaml`` is guarded: paths.py is imported by
    100+ scripts with no base pyyaml dependency, so a missing yaml must fall through, not crash.
    """
    try:
        import yaml  # guarded — base import path has no pyyaml dependency
    except ImportError:
        yaml = None

    yaml_path = profiles_dir / "characters.yaml"
    if yaml is not None and yaml_path.exists():
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            chars = data.get("characters") or {}
            if chars:
                characters, char_display, char_aliases = {}, {}, {}
                for slug, info in chars.items():
                    info = info or {}
                    display = info.get("display", slug)
                    aliases = list(info.get("aliases", [display]))
                    char_display[slug] = display
                    char_aliases[slug] = aliases
                    # R1: resolution keys = canonical forms ONLY, never the alias list.
                    characters[slug] = slug
                    characters[display.lower()] = slug
                    characters[_asciifold(display).lower()] = slug
                return characters, list(chars.keys()), char_display, char_aliases
        except Exception:
            pass  # corrupt / malformed yaml → fall through to discovery

    # Fallback #2 — discover slugs from INDEX.md-bearing profile dirs (no curated VN aliases available).
    if profiles_dir.exists():
        discovered = sorted(d.name for d in profiles_dir.iterdir() if d.is_dir() and (d / "INDEX.md").exists())
        if discovered:
            return (
                {slug: slug for slug in discovered},
                discovered,
                {slug: slug for slug in discovered},
                {slug: [slug] for slug in discovered},
            )

    # Fallback #3 — no roster at all (toolkit-only pack).
    return {}, [], {}, {}


CHARACTERS, ALL_CHARS, CHAR_DISPLAY, CHAR_SEARCH_ALIASES = _load_roster(PROFILES)

# All unordered dyad pairs, derived (never hand-listed — hand-lists drifted to 2/3 pairs).
CHARACTER_PAIRS = list(itertools.combinations(ALL_CHARS, 2))

# Universal profile schema — nested structure (25 base files, same for all characters).
# Per-character relationship files (e.g. relationships/<slug>.md) are NOT listed
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
    # Per-character relationship files are derived from the roster (never hand-listed) so paths.py
    # source carries no character slugs; family.md + network.md bracket the per-character split.
    "RELATIONSHIPS.md": (
        ["relationships/family.md"]
        + [f"relationships/{slug}.md" for slug in ALL_CHARS]
        + ["relationships/network.md"]
    ),
}


# Synthetic positional placeholder prefix (character-a → 1st roster slug, character-b → 2nd, …).
# Name-FREE by construction: shipped docs illustrate CLI usage with these neutral tokens instead of
# real slugs, so a reader can copy-paste an example and have it resolve against whatever roster the
# local repo declares (in roster order) without any real name appearing in the docs.
_PLACEHOLDER_PREFIX = "character-"


def resolve_character(name: str) -> str:
    """Resolve alias to canonical directory name.

    Accepts real slugs / display names / ASCII folds (the CHARACTERS map) AND the synthetic
    positional placeholders ``character-a``..``character-z`` (a→1st roster slug, …). The placeholder
    branch only fires for inputs that the canonical map does not already claim, so it is purely
    additive to the frozen API — every input that resolved before resolves identically.
    """
    key = name.lower().strip()
    if key in CHARACTERS:
        return CHARACTERS[key]
    if key.startswith(_PLACEHOLDER_PREFIX):
        suffix = key[len(_PLACEHOLDER_PREFIX):]
        if len(suffix) == 1 and "a" <= suffix <= "z":
            idx = ord(suffix) - ord("a")
            if idx < len(ALL_CHARS):
                return ALL_CHARS[idx]
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
