"""Smoke tests for the 8 evl:* skill script wrappers.

Each wrapper must import cleanly and expose a working CLI (--help exits 0). The
validate wrapper additionally proves the reference rubrics pass end-to-end through
the real CLI path (no network, no LLM). Run via the project venv interpreter.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PY = REPO / ".claude" / "skills" / ".venv" / "bin" / "python3"
PY = str(PY if PY.exists() else sys.executable)

SCRIPTS = [
    "evl-score/scripts/run_score.py",
    "evl-standardize/scripts/run_standardize.py",
    "evl-fit/scripts/run_fit.py",
    "evl-compatibility/scripts/run_compatibility.py",
    "evl-compare/scripts/run_compare.py",
    "evl-track/scripts/run_track.py",
    "evl-validate/scripts/run_validate.py",
    "evl-rubric-import/scripts/run_import.py",
]


@pytest.mark.parametrize("rel", SCRIPTS)
def test_skill_script_help_exits_zero(rel):
    path = REPO / ".claude" / "skills" / rel
    assert path.exists(), f"missing script {rel}"
    r = subprocess.run([PY, str(path), "--help"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("rel", SCRIPTS)
def test_skill_script_under_200_lines(rel):
    path = REPO / ".claude" / "skills" / rel
    assert len(path.read_text(encoding="utf-8").splitlines()) < 200, f"{rel} exceeds 200 lines"


def test_validate_all_reference_rubrics_pass_via_cli():
    path = REPO / ".claude" / "skills" / "evl-validate" / "scripts" / "run_validate.py"
    r = subprocess.run([PY, str(path), "--all"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_all_eight_skills_have_four_doc_spine():
    skills_root = REPO / ".claude" / "skills"
    evl_dirs = sorted(d for d in skills_root.glob("evl-*") if d.is_dir())
    assert len(evl_dirs) == 8, [d.name for d in evl_dirs]
    for d in evl_dirs:
        for doc in ("SKILL.md", "README.md", "GUIDE-EN.md", "GUIDE-VI.md"):
            assert (d / doc).exists(), f"{d.name} missing {doc}"
        assert list((d / "scripts").glob("*.py")), f"{d.name} missing a script"
