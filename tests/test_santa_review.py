"""Tests for run-santa-review.py — deterministic pre-check report for dual-review gate (Batch 4 A1).

Scope: script I/O correctness only. Round-limit/escalation/anti-anchoring are LLM
workflow concerns in SKILL.md, not unit-testable.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from venv_python import VENV_PYTHON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SANTA_SCRIPT = PROJECT_ROOT / ".claude" / "skills" / "orc-santa" / "scripts" / "run-santa-review.py"
PYTHON = VENV_PYTHON


def _load_santa():
    spec = importlib.util.spec_from_file_location("santa_mod", SANTA_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def santa(tmp_path, monkeypatch):
    """Load santa script with ROOT redirected to tmp_path (functions read module global ROOT)."""
    mod = _load_santa()
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    return mod


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestFileInventory:
    def test_file_inventory(self, santa, tmp_path):
        target = tmp_path / "profiles" / "alpha"
        _write(target / "core.md", "# Core\nsome text")
        _write(target / "voice.md", "# Voice\nmore text")
        files = santa._inventory_dir(target)
        names = sorted(f["name"] for f in files)
        assert names == ["core.md", "voice.md"]

    def test_empty_target_dir(self, santa, tmp_path):
        target = tmp_path / "empty"
        target.mkdir()
        assert santa._inventory_dir(target) == []

    def test_inventory_single_file(self, santa, tmp_path):
        f = tmp_path / "one.md"
        _write(f, "# One")
        files = santa._inventory_dir(f)
        assert len(files) == 1
        assert files[0]["name"] == "one.md"


class TestSchemaValidation:
    def test_schema_validation(self, santa, tmp_path):
        good = tmp_path / "good.md"
        bad = tmp_path / "bad.md"
        _write(good, "---\ntitle: x\n---\n# Body")
        _write(bad, "# No frontmatter")
        files = [santa._file_info(good), santa._file_info(bad)]
        result = santa.validate_schema(files)
        assert result["valid_count"] == 1
        assert result["total"] == 2
        assert "bad.md" in result["invalid_files"][0]


class TestWordCount:
    def test_word_count(self, santa, tmp_path):
        f = tmp_path / "wc.md"
        _write(f, "one two three four five")
        info = santa._file_info(f)
        assert info["words"] == 5

    def test_line_count(self, santa, tmp_path):
        f = tmp_path / "lc.md"
        _write(f, "line1\nline2\nline3")
        info = santa._file_info(f)
        assert info["lines"] == 3


class TestCrossReferenceDetection:
    def test_cross_reference_detection(self, santa, tmp_path):
        # changed file: docs/profiles/alpha/formulation.md
        changed = tmp_path / "docs" / "profiles" / "alpha" / "formulation.md"
        referencing = tmp_path / "docs" / "profiles" / "alpha" / "defense-mechanisms.md"
        _write(changed, "# Formulation\nclinical core")
        _write(referencing, "See formulation for details")
        refs = santa._find_cross_refs(changed, {"docs/profiles/alpha/formulation.md"})
        ref_paths = {r["path"] for r in refs}
        assert "docs/profiles/alpha/defense-mechanisms.md" in ref_paths
        assert "docs/profiles/alpha/formulation.md" not in ref_paths


class TestBuildReport:
    def test_build_report_full_scope(self, santa, tmp_path):
        target = tmp_path / "profiles" / "alpha"
        _write(target / "core.md", "hello world")
        report = santa.build_report(target, "psy", "full", 1)
        assert report["framework"] == "psy"
        assert report["scope"] == "full"
        assert report["round"] == 1
        assert report["file_count"] == 1
        assert report["total_words"] == 2


class TestCLI:
    def test_cli_output_json(self, tmp_path):
        target = PROJECT_ROOT / "docs" / "profiles" / "character-a" / "identity"
        result = subprocess.run(
            [str(PYTHON), str(SANTA_SCRIPT), "--target", str(target),
             "--framework", "psy", "--scope", "full"],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["framework"] == "psy"
        assert "files" in data

    def test_cli_missing_args(self):
        result = subprocess.run(
            [str(PYTHON), str(SANTA_SCRIPT), "--framework", "psy"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode != 0

    def test_cli_nonexistent_target(self):
        result = subprocess.run(
            [str(PYTHON), str(SANTA_SCRIPT), "--target", "/no/such/path",
             "--framework", "psy"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 1
        assert "not found" in (result.stderr + result.stdout).lower()

    def test_cli_invalid_round_rejected(self):
        """--round only accepts 1 or 2 (max 2 rounds, escalate after)."""
        result = subprocess.run(
            [str(PYTHON), str(SANTA_SCRIPT), "--target", str(PROJECT_ROOT / "docs"),
             "--framework", "psy", "--round", "3"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode != 0
