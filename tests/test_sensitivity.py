"""Tests for file_sensitivity.py — sensitivity classification module.

Character-agnostic: profile paths are built from the live roster (paths.ALL_CHARS), never a
hardcoded real slug, so the shipped test tree carries no real names. The whole module skips when
the roster is empty (toolkit-only pack with no characters.yaml) — classify_file keys sensitivity
off roster membership, so a synthetic slug would not classify.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from platform_lib.file_sensitivity import classify_file, classify_all_profiles, load_config
from platform_lib.paths import ALL_CHARS
from venv_python import VENV_PYTHON

pytestmark = pytest.mark.skipif(not ALL_CHARS, reason="no character roster — toolkit-only pack")

# Two distinct real slugs (sourced dynamically) for path-pattern assertions; fall back to one
# when the roster has a single character.
_CHAR = ALL_CHARS[0] if ALL_CHARS else "x"
_CHAR2 = ALL_CHARS[1] if len(ALL_CHARS) > 1 else _CHAR


class TestClassifyFile:
    def test_classify_critical_darkness(self):
        r = classify_file(f"docs/profiles/{_CHAR}/darkness/traumas.md")
        assert r["level"] == "CRITICAL"
        assert r["zone"] == "PSY-darkness"
        assert len(r["checks"]) > 0

    def test_classify_high_psychology_formulation(self):
        r = classify_file(f"docs/profiles/{_CHAR}/psychology/formulation.md")
        assert r["level"] == "HIGH"
        assert r["zone"] == "PSY-clinical"

    def test_classify_high_psychology_generic(self):
        r = classify_file(f"docs/profiles/{_CHAR2}/psychology/archetype.md")
        assert r["level"] == "HIGH"
        assert r["zone"] == "PSY-clinical"

    def test_classify_medium_relationships(self):
        r = classify_file(f"docs/profiles/{_CHAR}/relationships/family.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "PSY-relationship"

    def test_classify_medium_growth(self):
        r = classify_file(f"docs/profiles/{_CHAR}/growth/career-path.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "GRO-growth"

    def test_classify_medium_materials(self):
        r = classify_file(f"docs/materials/{_CHAR}/some-transcript.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "MAT-materials"

    def test_classify_medium_rules(self):
        r = classify_file("docs/rules/01-profile-structure.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "ORC-rules"

    def test_classify_low_identity(self):
        r = classify_file(f"docs/profiles/{_CHAR}/identity/core.md")
        assert r["level"] == "LOW"

    def test_classify_low_timeline(self):
        r = classify_file(f"docs/profiles/{_CHAR2}/timeline/overview.md")
        assert r["level"] == "LOW"

    def test_classify_none_random_file(self):
        r = classify_file("README.md")
        assert r["level"] == "NONE"
        assert r["zone"] == "none"
        assert r["pattern_matched"] is None

    def test_first_match_priority(self):
        specific = classify_file(f"docs/profiles/{_CHAR}/psychology/formulation.md")
        generic = classify_file(f"docs/profiles/{_CHAR}/psychology/archetype.md")
        assert specific["zone"] == "PSY-clinical"
        assert generic["zone"] == "PSY-clinical"
        assert specific["pattern_matched"] == "psychology/formulation.md"
        assert generic["pattern_matched"] == "psychology/"


class TestClassifyAllProfiles:
    def test_total_count(self):
        results = classify_all_profiles()
        assert len(results) == 75

    def test_three_critical(self):
        results = classify_all_profiles()
        critical = [r for r in results if r["level"] == "CRITICAL"]
        assert len(critical) == 3
        for r in critical:
            assert "darkness/traumas.md" in r["path"]

    def test_all_levels_present(self):
        results = classify_all_profiles()
        levels = {r["level"] for r in results}
        assert "CRITICAL" in levels
        assert "HIGH" in levels
        assert "MEDIUM" in levels
        assert "LOW" in levels


class TestCLI:
    @pytest.fixture(scope="class")
    def python_bin(self):
        return str(VENV_PYTHON)

    @pytest.fixture(scope="class")
    def script_path(self):
        return str(SCRIPTS_DIR / "platform_lib" / "file_sensitivity.py")

    def test_cli_path(self, python_bin, script_path):
        result = subprocess.run(
            [python_bin, script_path, "--path", f"docs/profiles/{_CHAR}/darkness/traumas.md"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "CRITICAL" in result.stdout

    def test_cli_all_json(self, python_bin, script_path):
        result = subprocess.run(
            [python_bin, script_path, "--all", "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 75
        assert all("level" in item for item in data)
