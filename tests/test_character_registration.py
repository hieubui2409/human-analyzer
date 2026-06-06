"""New-character registration + roster↔profile drift — roster_io contract.

NAME-FREE BY CONTRACT: ships in the pack, contains ZERO real names. Every input is a coined synthetic
slug/display ("test-zeta", "Zếta", ...). The rules are verified by PROPERTY on synthetic data.
"""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR / "platform_lib"))
sys.path.insert(0, str(SCRIPTS_DIR))

import paths  # noqa: E402
import roster_io  # noqa: E402


# (a) register() round-trips: synthetic entry → tmp yaml → paths._load_roster returns it
def test_register_roundtrips(tmp_path):
    roster_io.register("test-zeta", "Zếta", ["Zếta", "Zeta", "zêta", "Zeta Full"], tmp_path)
    characters, all_chars, char_display, char_aliases = paths._load_roster(tmp_path)
    assert all_chars == ["test-zeta"]
    assert char_display["test-zeta"] == "Zếta"
    assert char_aliases["test-zeta"] == ["Zếta", "Zeta", "zêta", "Zeta Full"]
    # resolution map = canonical forms only
    assert characters["test-zeta"] == "test-zeta"
    assert characters["zếta"] == "test-zeta"       # display.lower()
    assert characters["zeta"] == "test-zeta"        # asciifold(display)
    assert "zeta full" not in characters            # alias form is NOT a resolution key


# (b) idempotent — re-register the same slug never duplicates
def test_register_idempotent(tmp_path):
    roster_io.register("test-zeta", "Zếta", ["Zếta"], tmp_path)
    roster_io.register("test-zeta", "Zếta", ["Zếta"], tmp_path)  # again
    mapping = roster_io.load_mapping(tmp_path)
    assert list(mapping.keys()) == ["test-zeta"]  # one key, no dup
    # second register replaces, never appends a clone
    roster_io.register("test-omega", "Ómega", ["Ómega"], tmp_path)
    assert list(roster_io.load_mapping(tmp_path).keys()) == ["test-zeta", "test-omega"]


# (c) suggest_typo_variants ⊇ {ascii-folded, tone-dropped} — by property on a coined diacritic display
def test_suggest_typo_variants_rule(tmp_path):
    variants = roster_io.suggest_typo_variants("Zếta")  # ế = e+circumflex+acute
    assert "zeta" in variants     # full ASCII fold
    assert "zêta" in variants     # tone dropped, circumflex kept
    # the display form itself is not echoed back as a "typo"
    assert "zếta" not in variants


# (d) ensure_registered writes a stub only when absent; idempotent
def test_ensure_registered_stub_then_idempotent(tmp_path):
    assert roster_io.ensure_registered("test-zeta", "Zếta", tmp_path) is True
    mapping = roster_io.load_mapping(tmp_path)
    assert mapping["test-zeta"]["display"] == "Zếta"
    assert "Zếta" in mapping["test-zeta"]["aliases"]
    assert "zeta" in mapping["test-zeta"]["aliases"]  # folded typo suggestion folded in
    # re-run: slug present → no write, returns False, no clobber
    assert roster_io.ensure_registered("test-zeta", "DIFFERENT", tmp_path) is False
    assert roster_io.load_mapping(tmp_path)["test-zeta"]["display"] == "Zếta"


# (e) scaffold-then-load: scaffolding a throwaway char makes it appear in ALL_CHARS via auto-register
def test_scaffold_auto_registers(tmp_path):
    profiles = tmp_path / "docs" / "profiles"
    profiles.mkdir(parents=True)
    script = SCRIPTS_DIR / "init-universal-profile-skeleton.py"
    result = subprocess.run(
        [sys.executable, str(script), "test-zeta", "--display-name", "Zếta",
         "--project-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # roster entry was written by the scaffolder's auto-register
    _chars, all_chars, _disp, _al = paths._load_roster(profiles)
    assert "test-zeta" in all_chars


# (f) drift detector: a profile dir with no roster entry → flagged
def test_drift_dir_without_entry(tmp_path):
    (tmp_path / "test-zeta").mkdir()
    (tmp_path / "test-zeta" / "INDEX.md").write_text("# x", encoding="utf-8")
    dirs_without_entry, entries_without_dir = roster_io.roster_profile_drift(tmp_path, all_chars=[])
    assert dirs_without_entry == {"test-zeta"}
    assert entries_without_dir == set()


# (g) drift detector: a roster entry with no profile dir → flagged (other direction)
def test_drift_entry_without_dir(tmp_path):
    dirs_without_entry, entries_without_dir = roster_io.roster_profile_drift(
        tmp_path, all_chars=["test-ghost"]
    )
    assert dirs_without_entry == set()
    assert entries_without_dir == {"test-ghost"}


# (h) drift detector: aligned corpus → both empty
def test_drift_aligned(tmp_path):
    for slug in ("test-zeta", "test-omega"):
        (tmp_path / slug).mkdir()
        (tmp_path / slug / "INDEX.md").write_text("# x", encoding="utf-8")
    drift = roster_io.roster_profile_drift(tmp_path, all_chars=["test-zeta", "test-omega"])
    assert drift == (set(), set())
