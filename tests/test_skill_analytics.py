"""B12 Monitoring Phase 2 — com:skill-analytics (S2 health, P3 deps, P4 cascade).

Isolated: each script module is loaded from its file and its module-level SKILLS_DIR /
PLATFORM_LIB globals are monkeypatched at a tmp fixture tree, so no real repo dependency.
"""
import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "com-skill-analytics" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_skill(root: Path, name: str, *, scripts: dict | None = None, frontmatter=True, md_extra=""):
    d = root / name
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    fm = ('---\nname: "%s"\ndescription: "test skill desc"\n---\n' % name.replace("-", ":", 1)) if frontmatter else ""
    (d / "SKILL.md").write_text(fm + "# " + name + "\n" + md_extra, encoding="utf-8")
    for fn, body in (scripts or {}).items():
        (d / "scripts" / fn).write_text(body, encoding="utf-8")
    return d


@pytest.fixture
def fake_tree(tmp_path):
    skills = tmp_path / "skills"
    lib = tmp_path / "platform_lib"
    lib.mkdir(parents=True)
    (lib / "paths.py").write_text("ROOT=1\n", encoding="utf-8")
    (lib / "lonely.py").write_text("x=1\n", encoding="utf-8")  # unused module
    _make_skill(skills, "psy-good", scripts={"ok.py": "from platform_lib.paths import ROOT\n"})
    _make_skill(skills, "cre-broken", scripts={"bad.py": "def (:\n"})  # syntax error
    _make_skill(skills, "orc-prompt")  # prompt-only, no scripts
    _make_skill(skills, "zztop-ignored", scripts={"x.py": "y=1\n"})  # non-framework prefix → ignored
    return skills, lib


def test_s2_detects_broken_and_classifies(fake_tree, tmp_path):
    skills, lib = fake_tree
    mod = _load("check-skill-and-lib-health")
    mod.SKILLS_DIR = skills
    mod.PLATFORM_LIB = lib
    data = mod.gather(None, perf=False)
    assert set(data["frameworks"]) == {"psy", "cre", "orc"}  # zztop ignored
    statuses = {s["skill"]: s["status"] for s in data["skills"]}
    assert statuses["cre-broken"] == "BROKEN"
    assert statuses["psy-good"] == "OK"
    types = {s["skill"]: s["type"] for s in data["skills"]}
    assert types["orc-prompt"] == "prompt-only"
    assert data["platform_lib"]["paths"] == 1   # imported by psy-good
    assert data["platform_lib"]["lonely"] == 0  # unused


def test_p3_fanin_and_unused(fake_tree):
    skills, lib = fake_tree
    mod = _load("build-dependency-graph")
    mod.SKILLS_DIR = skills
    mod.PLATFORM_LIB = lib
    data = mod.gather()
    assert data["fanin"].get("paths") == 1
    assert "lonely" in data["unused_modules"]
    assert data["cycles"] == []  # no platform_lib cycles in fixture


def test_p4_extracts_events_and_orphans(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(skills, "mat-loader", md_extra="Pipeline: MAT.integrated → PSY.refresh\n")
    _make_skill(skills, "com-rules", md_extra="No events here.\n")
    mod = _load("build-cascade-graph")
    mod.SKILLS_DIR = skills
    data = mod.gather()
    assert ("MAT.integrated", "PSY.refresh") in [tuple(e) for e in data["chain_edges"]]
    assert "com:rules" in data["orphans"]
    assert "MAT.integrated" in data["skill_events"]["mat:loader"]
