"""Tests for file_sensitivity.py — sensitivity classification module (Batch 2 B6)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from platform_lib.file_sensitivity import classify_file, classify_all_profiles, load_config


class TestClassifyFile:
    def test_classify_critical_darkness(self):
        r = classify_file("docs/profiles/character-a/darkness/traumas.md")
        assert r["level"] == "CRITICAL"
        assert r["zone"] == "PSY-darkness"
        assert len(r["checks"]) > 0

    def test_classify_high_psychology_formulation(self):
        r = classify_file("docs/profiles/character-a/psychology/formulation.md")
        assert r["level"] == "HIGH"
        assert r["zone"] == "PSY-clinical"

    def test_classify_high_psychology_generic(self):
        r = classify_file("docs/profiles/character-b/psychology/archetype.md")
        assert r["level"] == "HIGH"
        assert r["zone"] == "PSY-clinical"

    def test_classify_medium_relationships(self):
        r = classify_file("docs/profiles/character-a/relationships/family.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "PSY-relationship"

    def test_classify_medium_growth(self):
        r = classify_file("docs/profiles/character-a/growth/career-path.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "GRO-growth"

    def test_classify_medium_materials(self):
        r = classify_file("docs/materials/character-a/some-transcript.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "MAT-materials"

    def test_classify_medium_rules(self):
        r = classify_file("docs/rules/01-profile-structure.md")
        assert r["level"] == "MEDIUM"
        assert r["zone"] == "ORC-rules"

    def test_classify_low_identity(self):
        r = classify_file("docs/profiles/character-a/identity/core.md")
        assert r["level"] == "LOW"

    def test_classify_low_timeline(self):
        r = classify_file("docs/profiles/character-c/timeline/overview.md")
        assert r["level"] == "LOW"

    def test_classify_none_random_file(self):
        r = classify_file("README.md")
        assert r["level"] == "NONE"
        assert r["zone"] == "none"
        assert r["pattern_matched"] is None

    def test_first_match_priority(self):
        specific = classify_file("docs/profiles/character-a/psychology/formulation.md")
        generic = classify_file("docs/profiles/character-a/psychology/archetype.md")
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
        return str(Path.home() / ".claude" / "skills" / ".venv" / "bin" / "python3")

    @pytest.fixture(scope="class")
    def script_path(self):
        return str(SCRIPTS_DIR / "platform_lib" / "file_sensitivity.py")

    def test_cli_path(self, python_bin, script_path):
        result = subprocess.run(
            [python_bin, script_path, "--path", "docs/profiles/character-a/darkness/traumas.md"],
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
