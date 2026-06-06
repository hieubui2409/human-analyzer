"""Roster loader contract — paths._load_roster reads docs/profiles/characters.yaml.

NAME-FREE BY CONTRACT: this file ships in the pack and must contain ZERO real-character
names. Every fixture below uses coined synthetic names (Zêta / Ómega / char-one). The
loader behavior is verified by PROPERTY, never by asserting a real roster.

Covered: structural round-trip, the R1 derivation guard (resolution map excludes alias
forms), the discovery fallback, corrupt-yaml tolerance, the import-yaml guard, the empty
fallback, and diacritic preservation.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import platform_lib.paths as paths  # noqa: E402


# Synthetic roster — coined diacritic displays, no real names. "Zeeta" / the full-name form
# are deliberately NOT equal to display nor to fold(display), so they can only appear as
# resolution keys if the loader (wrongly) iterates `aliases` — that is the R1 trap.
_FIXTURE_YAML = """\
characters:
  char-one:
    display: "Zêta"
    aliases: ["Zêta", "Zeta", "Zeeta", "Char One Full"]
  char-two:
    display: "Ómega"
    aliases: ["Ómega", "Omega"]
"""


def _write_yaml(profiles_dir: Path, text: str) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "characters.yaml").write_text(text, encoding="utf-8")


def _make_profile_dirs(profiles_dir: Path, slugs) -> None:
    for slug in slugs:
        d = profiles_dir / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "INDEX.md").write_text("# index\n", encoding="utf-8")


# (a) structural round-trip from a yaml fixture
def test_load_roster_structural_roundtrip(tmp_path):
    _write_yaml(tmp_path, _FIXTURE_YAML)
    characters, all_chars, char_display, char_aliases = paths._load_roster(tmp_path)

    # ALL_CHARS preserves insertion order from the yaml mapping
    assert all_chars == ["char-one", "char-two"]
    # CHAR_DISPLAY maps slug -> display verbatim (diacritics kept)
    assert char_display == {"char-one": "Zêta", "char-two": "Ómega"}
    # CHAR_SEARCH_ALIASES == the yaml `aliases` verbatim (all forms, diacritics kept)
    assert char_aliases["char-one"] == ["Zêta", "Zeta", "Zeeta", "Char One Full"]
    assert char_aliases["char-two"] == ["Ómega", "Omega"]
    # CHARACTERS resolution map = exactly {slug, display.lower, fold(display).lower} per char
    assert characters["char-one"] == "char-one"
    assert characters["zêta"] == "char-one"   # display.lower()
    assert characters["zeta"] == "char-one"    # asciifold(display).lower()
    assert characters["char-two"] == "char-two"
    assert characters["ómega"] == "char-two"
    assert characters["omega"] == "char-two"


# (b) R1 guard — alias-only forms are in CHAR_SEARCH_ALIASES but NEVER in the resolution map
def test_r1_characters_excludes_alias_only_forms(tmp_path):
    _write_yaml(tmp_path, _FIXTURE_YAML)
    characters, _all, _disp, char_aliases = paths._load_roster(tmp_path)

    # "Zeeta" + the full-name form are real aliases (searchable)...
    assert "Zeeta" in char_aliases["char-one"]
    assert "Char One Full" in char_aliases["char-one"]
    # ...but they must NOT become resolution keys (today's resolve_character would raise on them).
    for forbidden in ("zeeta", "char one full", "char-one-full"):
        assert forbidden not in characters, f"alias form leaked into resolution map: {forbidden!r}"
    # Exactly 3 resolution keys per char (slug, display.lower, fold) → 6 total for 2 chars.
    assert len(characters) == 6


# (c) missing characters.yaml → discovery from INDEX.md dirs
def test_missing_yaml_falls_back_to_discovery(tmp_path):
    _make_profile_dirs(tmp_path, ["char-x", "char-y"])  # no characters.yaml
    characters, all_chars, char_display, char_aliases = paths._load_roster(tmp_path)
    assert all_chars == ["char-x", "char-y"]  # sorted discovery
    assert characters == {"char-x": "char-x", "char-y": "char-y"}  # identity aliases
    assert char_display == {"char-x": "char-x", "char-y": "char-y"}
    assert char_aliases == {"char-x": ["char-x"], "char-y": ["char-y"]}


# (d) corrupt yaml → graceful fallback (discovery here), never raises
def test_corrupt_yaml_does_not_raise(tmp_path):
    _write_yaml(tmp_path, "characters: [this is : not valid : yaml")
    _make_profile_dirs(tmp_path, ["char-z"])
    characters, all_chars, _disp, _al = paths._load_roster(tmp_path)  # must not raise
    assert all_chars == ["char-z"]
    assert characters == {"char-z": "char-z"}


# (e) import yaml ImportError simulated → skip yaml branch, use discovery, no crash
def test_import_yaml_guard(tmp_path, monkeypatch):
    _write_yaml(tmp_path, _FIXTURE_YAML)        # a valid yaml IS present...
    _make_profile_dirs(tmp_path, ["char-x", "char-y"])
    monkeypatch.setitem(sys.modules, "yaml", None)  # ...but `import yaml` now raises ImportError
    characters, all_chars, _disp, _al = paths._load_roster(tmp_path)
    # yaml unreadable ⇒ loader must ignore characters.yaml and discover from dirs instead
    assert all_chars == ["char-x", "char-y"]
    assert characters == {"char-x": "char-x", "char-y": "char-y"}


# (f) empty profiles dir (no yaml, no dirs) → all empties (toolkit-only pack)
def test_empty_profiles_returns_empties(tmp_path):
    characters, all_chars, char_display, char_aliases = paths._load_roster(tmp_path)
    assert characters == {}
    assert all_chars == []
    assert char_display == {}
    assert char_aliases == {}


# (g) diacritics survive the yaml round-trip — asserted by PROPERTY, not by naming a real char
def test_diacritics_preserved(tmp_path):
    _write_yaml(tmp_path, _FIXTURE_YAML)
    _characters, _all, char_display, _al = paths._load_roster(tmp_path)
    display = char_display["char-one"]
    assert display == "Zêta"
    assert paths._asciifold(display).lower() == "zeta"
    assert display != paths._asciifold(display)  # the fold genuinely strips diacritics
