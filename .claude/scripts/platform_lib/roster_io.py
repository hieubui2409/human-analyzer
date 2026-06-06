"""roster_io — read/write helpers for docs/profiles/characters.yaml (the character roster DATA).

paths.py is the READ side (derives the in-memory roster structures, import-time, yaml-guarded). This module
is the WRITE side used by character onboarding: register a new entry, suggest IME-typo alias variants, and
compute roster↔profile drift. It is a dev-time tool (scaffolding / CI invariant), so it may require pyyaml —
unlike paths.py it is never on the foundational 100-importer path.

NAME-FREE BY CONTRACT: this file ships in the pack and contains ZERO real-character names. All names live in
the (pack-excluded) characters.yaml it reads/writes.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

from paths import _asciifold  # DRY: one diacritic fold for the whole roster subsystem

# Header re-emitted on every write so characters.yaml stays self-documenting after registration.
_HEADER = """\
# Character roster — the SINGLE source of real-character names for the toolkit.
#
# Backs paths.py's roster (CHARACTERS / ALL_CHARS / CHAR_DISPLAY / CHAR_SEARCH_ALIASES). Lives under
# docs/profiles/, so the pack safety_filter drops it from every release tarball — shipped code stays
# name-free while the running repo resolves characters from here.
#
# Schema per entry:
#   <slug>:
#     display: "<diacritic-exact short name>"
#     aliases: ["<display>", "<ascii-folded>", "<IME-typo variants>", "<full name>"]
#
# CHARACTERS (resolution map) = {slug, display.lower(), asciifold(display).lower()} ONLY; alias forms are
# free-text SEARCH terms, never resolution keys. Managed by roster_io.register() — edits here are fine too.
"""

# Vietnamese tone marks (combining) an IME slip commonly drops while KEEPING the letter-modifier marks
# (circumflex U+0302, breve U+0306, horn U+031B): grave, acute, tilde, hook-above, dot-below.
_TONE_MARKS = {"̀", "́", "̃", "̉", "̣"}


def _characters_yaml(profiles_dir: Path) -> Path:
    return profiles_dir / "characters.yaml"


def load_mapping(profiles_dir: Path) -> dict:
    """Return the raw ``characters:`` mapping (slug -> {display, aliases}); {} if absent/empty."""
    import yaml

    path = _characters_yaml(profiles_dir)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("characters") or {}


def _dump(profiles_dir: Path, mapping: dict) -> None:
    import yaml

    body = yaml.safe_dump(
        {"characters": mapping},
        allow_unicode=True,    # keep diacritics, never \uXXXX escapes
        sort_keys=False,       # preserve insertion order (roster order is meaningful)
        default_flow_style=False,
        width=4096,
    )
    _characters_yaml(profiles_dir).write_text(_HEADER + body, encoding="utf-8")


def drop_tones(display: str) -> str:
    """Strip only VN tone marks, keeping circumflex/breve/horn (e.g. 'ế' -> 'ê', 'ọ' -> 'ô' base kept)."""
    stripped = "".join(c for c in unicodedata.normalize("NFD", display) if c not in _TONE_MARKS)
    return unicodedata.normalize("NFC", stripped)


def suggest_typo_variants(display: str) -> list[str]:
    """Advisory IME-slip alias candidates for ``display`` (deterministic GATHER — operator confirms).

    Returns lowercased candidates: the full ASCII fold and the tone-dropped form (which keeps letter
    modifiers). The display form itself is excluded. Order stable, de-duplicated.
    """
    folded = _asciifold(display).lower()
    tone_drop = drop_tones(display).lower()
    out: list[str] = []
    for cand in (folded, tone_drop):
        if cand and cand != display.lower() and cand not in out:
            out.append(cand)
    return out


def register(slug: str, display: str, aliases: list[str], profiles_dir: Path) -> dict:
    """Upsert one roster entry, writing characters.yaml. Idempotent by slug (a dict cannot duplicate keys).

    Returns the full mapping after the write. An existing entry is replaced (used by the enrich flow);
    callers wanting stub-only-if-absent use ``ensure_registered``.
    """
    mapping = load_mapping(profiles_dir)
    mapping[slug] = {"display": display, "aliases": list(aliases)}
    _dump(profiles_dir, mapping)
    return mapping


def ensure_registered(slug: str, display: str, profiles_dir: Path) -> bool:
    """Register a STUB entry only if ``slug`` is absent — so a scaffolded character is never unregistered.

    Stub aliases = [display] + suggested typo variants (deduped). Idempotent: returns False (no write)
    when the slug already has an entry, so re-scaffolding never clobbers an enriched roster row.
    """
    if slug in load_mapping(profiles_dir):
        return False
    aliases = [display] + [a for a in suggest_typo_variants(display) if a != display]
    register(slug, display, aliases, profiles_dir)
    return True


def roster_profile_drift(profiles_dir: Path, all_chars) -> tuple[set, set]:
    """Return (dirs_without_entry, entries_without_dir) — both empty ⇒ roster and corpus agree.

    A profile dir counts only when it holds an INDEX.md (skips _template / scratch dirs).
    """
    profile_dirs = {
        d.name for d in profiles_dir.iterdir() if d.is_dir() and (d / "INDEX.md").exists()
    } if profiles_dir.exists() else set()
    roster = set(all_chars)
    return profile_dirs - roster, roster - profile_dirs
