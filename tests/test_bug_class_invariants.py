"""Bug-class regression invariants — the named guard for CLASSES of bug the review cycles closed.

These are not feature tests; each asserts that a previously-closed bug class stays closed. Run as their
own CI gate (`pytest -m bug_class`). Closed classes guarded here:
  - missing-module: a test (or skill) imports a platform_lib module that no longer exists (the KG-minimize
    orphan that broke pytest collection).
  - registry-redefinition: a skill script re-declares a constant centralized in platform_lib (the event-
    registry drift class — ORC-08/09).
  - glob-scope: a profile/material scan uses non-recursive glob (the nested-files-missed class — MAT-02/PSY-05).
  - audit/schema/skill-count: the deterministic gates the manual cycles ran by hand.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLATFORM_LIB = ROOT / ".claude" / "scripts" / "platform_lib"
SKILLS = ROOT / ".claude" / "skills"
VENV = ROOT / ".claude" / "skills" / ".venv" / "bin" / "python3"
PY = str(VENV) if VENV.exists() else sys.executable

pytestmark = pytest.mark.bug_class

FRAMEWORKS = ("orc", "psy", "cre", "gro", "mat", "com")


def _framework_script_files():
    files = []
    for fw in FRAMEWORKS:
        for d in sorted(SKILLS.glob(f"{fw}-*/scripts")):
            files += [p for p in d.glob("*.py") if p.name != "__init__.py"]
    return files


def _platform_lib_modules():
    return {p.stem for p in PLATFORM_LIB.glob("*.py") if p.stem != "__init__"}


# --- missing-module: no test imports a platform_lib module that doesn't exist ---
def test_no_test_imports_missing_platform_lib_module():
    mods = _platform_lib_modules()
    pat = re.compile(r"from platform_lib import (\w+)|import platform_lib\.(\w+)")
    offenders = []
    for tf in (ROOT / "tests").glob("*.py"):
        text = tf.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            name = m.group(1) or m.group(2)
            # names may be a module OR a symbol re-exported from a module; only flag when neither.
            if name not in mods and name not in {"paths", "__init__"}:
                # symbol import (from platform_lib import resolve_character) is fine if it's in __init__/any module
                if not _symbol_exists_anywhere(name, mods):
                    offenders.append(f"{tf.name}: {name}")
    assert not offenders, "tests import non-existent platform_lib modules: " + "; ".join(offenders)


def _symbol_exists_anywhere(name, mods):
    # cheap check: a re-exported symbol appears as a def/class/assignment in some module or __init__
    for p in PLATFORM_LIB.glob("*.py"):
        t = p.read_text(encoding="utf-8")
        if re.search(rf"\b(def|class)\s+{re.escape(name)}\b|\b{re.escape(name)}\s*=", t):
            return True
    return name in mods


# --- registry-redefinition: skill scripts must not re-declare a centralized constant ---
def test_no_skill_script_redefines_centralized_constant():
    centralized = ["EVENT_ROUTING", "DOMAIN_PATH_RULES", "CHARACTER_PAIRS", "ALL_PLATFORMS"]
    assign = re.compile(r"^\s*(" + "|".join(centralized) + r")\s*[:=]", re.M)
    offenders = []
    for f in _framework_script_files():
        text = f.read_text(encoding="utf-8")
        for m in assign.finditer(text):
            offenders.append(f"{f.relative_to(SKILLS)}: redeclares {m.group(1)}")
    assert not offenders, "skill scripts redeclare platform_lib constants (import them): " + "; ".join(offenders)


# --- glob-scope: profile/material scans must be recursive (rglob) ---
def test_no_nonrecursive_glob_on_profile_or_material_dirs():
    # A `.glob("*.md")` chained off a profile/material dir handle misses nested files.
    bad = re.compile(r"(PROFILES|MATERIALS|character_dir\([^)]*\)|materials_dir\([^)]*\)|cdir|char_dir|mat_dir)"
                     r"[^\n]*\.glob\(")
    offenders = []
    for f in _framework_script_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if bad.search(line) and "rglob" not in line:
                offenders.append(f"{f.relative_to(SKILLS)}:{i}")
    assert not offenders, "non-recursive glob on profile/material dirs (use rglob): " + "; ".join(offenders)


# --- memory-dir-redefinition: the project memory slug lives once in paths.memory_dir ---
def test_no_skill_script_rerolls_memory_dir_slug():
    # Computing the ~/.claude/projects/{slug}/memory path inline (slug = root.replace("/","-"))
    # is the "centralized fact, reader scrapes its own copy" class — orc-dream once hardcoded a
    # stale machine slug. Framework scripts must call paths.memory_dir() instead.
    slug = re.compile(r'replace\(\s*["\']/["\']\s*,\s*["\']-["\']\s*\)')
    offenders = []
    for f in _framework_script_files():
        text = f.read_text(encoding="utf-8")
        if slug.search(text) and "projects" in text and "memory" in text:
            offenders.append(str(f.relative_to(SKILLS)))
    assert not offenders, "skill scripts re-roll the memory-dir slug (use paths.memory_dir()): " + "; ".join(offenders)


# --- stale-project-name: live skill/agent docs must not carry the old project name ---
def test_no_stale_project_name_in_live_docs():
    stale = "ck-marketing"
    docs = list(SKILLS.glob("[a-z][a-z][a-z]-*/**/*.md")) + list((ROOT / ".claude" / "agents").glob("*.md"))
    offenders = [str(d.relative_to(ROOT)) for d in docs
                 if "/.venv/" not in str(d) and stale in d.read_text(encoding="utf-8", errors="replace")]
    assert not offenders, f"live docs reference the old project name '{stale}': " + "; ".join(offenders)


# --- deterministic gates the manual cycles ran by hand ---
def test_orc_audit_zero_hard_violations():
    r = subprocess.run([PY, str(SKILLS / "orc-audit/scripts/audit-cross-domain-event-consistency.py")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"orc:audit reported hard violations (exit {r.returncode}):\n{r.stdout[-1500:]}"


def test_schema_validation_passes():
    r = subprocess.run([PY, str(ROOT / ".claude/scripts/validate-all-against-schemas.py")],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"schema validation failed (exit {r.returncode}):\n{r.stdout[-1500:]}"


def test_skill_count_matches_claude_md():
    counts = {fw: len(list(SKILLS.glob(f"{fw}-*"))) for fw in FRAMEWORKS}
    total = sum(counts.values())
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+framework skills", claude)
    assert m, "CLAUDE.md does not state '<N> framework skills'"
    assert total == int(m.group(1)), f"skill count {total} ({counts}) != CLAUDE.md {m.group(1)}"


# --- roster-drift: characters.yaml roster ⇔ profile dirs must never diverge (bidirectional) ---
# Closes the onboarding-gap class: a scaffolded profile dir with no roster entry (unresolvable character)
# or a roster entry whose profile dir was deleted (dangling alias). Scoped to the REAL corpus — runs with
# no PMC_PROJECT_ROOT, so paths.ALL_CHARS is the yaml roster and PROFILES is the live docs/profiles.
def test_roster_matches_profile_dirs():
    sys.path.insert(0, str(PLATFORM_LIB))
    import paths
    import roster_io

    dirs_without_entry, entries_without_dir = roster_io.roster_profile_drift(paths.PROFILES, paths.ALL_CHARS)
    assert not dirs_without_entry and not entries_without_dir, (
        f"roster↔profile drift — dirs missing a characters.yaml entry: {sorted(dirs_without_entry)}; "
        f"roster entries missing a profile dir: {sorted(entries_without_dir)}"
    )
