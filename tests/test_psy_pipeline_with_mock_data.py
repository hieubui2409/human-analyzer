"""Test PSY framework scripts with mock data."""
import subprocess
import os
from pathlib import Path

import pytest
from venv_python import VENV_PYTHON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(VENV_PYTHON)
MOCK_DATA = PROJECT_ROOT / "tests" / "mock-data"
ENV = {
    **os.environ,
    "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts"),
    "MOCK_DATA_DIR": str(MOCK_DATA),
}


def run_script(skill, script, args=None):
    path = PROJECT_ROOT / ".claude" / "skills" / skill / "scripts" / script
    cmd = [PYTHON, str(path)] + (args or [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=ENV)


class TestWaveGates:
    def test_check_wave_gates_with_character(self):
        r = run_script("psy-wave", "check-wave-gates.py", ["--character", "character-a", "--wave", "1"])
        assert r.returncode == 0 or r.stdout.strip()

    def test_track_wave_progress(self):
        r = run_script("psy-wave", "track-wave-progress-from-index.py", ["--character", "character-a"])
        assert r.returncode == 0 or r.stdout.strip()


class TestCrisis:
    def test_scan_crisis_keywords(self):
        r = run_script("psy-crisis-assess", "scan-crisis-keywords-in-profile.py", ["--character", "character-a"])
        assert r.returncode == 0

    def test_extract_protective_factors(self):
        r = run_script("psy-crisis-assess", "extract-protective-factors-from-light-md.py", ["--character", "character-a"])
        assert r.returncode == 0

    def test_dsm5_checklist_template(self):
        r = run_script("psy-crisis-assess", "generate-dsm5-mdd-checklist-template.py", ["--character", "character-a"])
        assert r.returncode == 0
        assert "DSM" in r.stdout or "MDD" in r.stdout or "checklist" in r.stdout.lower()


class TestCrossref:
    def test_timeline_date_consistency(self):
        r = run_script("psy-crossref", "check-timeline-date-consistency.py")
        assert r.returncode == 0

    def test_bidirectional_references(self):
        r = run_script("psy-crossref", "check-bidirectional-references.py")
        assert r.returncode == 0

    def test_extract_cross_character_events(self):
        r = run_script("psy-crossref", "extract-cross-character-events.py")
        assert r.returncode == 0

    def test_validate_profiles_against_schema(self):
        r = run_script("psy-crossref", "validate-all-profiles-against-schema.py")
        assert r.returncode == 0


class TestPropagation:
    def test_detect_propagation_targets(self):
        r = run_script("psy-propagate", "detect-propagation-targets-from-profile-diff.py",
                       ["--character", "character-a", "--section", "psychology/formulation.md"])
        assert r.returncode == 0


class TestHealthCheck:
    def test_score_profile_completeness(self):
        r = run_script("psy-health-check", "score-profile-completeness.py", ["--character", "character-a"])
        assert r.returncode == 0


class TestArcTracker:
    def test_extract_growth_indicators(self):
        r = run_script("psy-arc-tracker", "extract-growth-indicators-from-profile.py", ["--character", "character-a"])
        assert r.returncode == 0


class TestRefTools:
    def test_build_reference_index(self):
        r = run_script("psy-ref-audit", "build-reference-index.py")
        assert r.returncode == 0

    def test_scan_profile_clinical_terms(self):
        r = run_script("psy-ref-audit", "scan-profile-files-for-clinical-terms.py", ["--character", "character-a"])
        assert r.returncode == 0

    def test_generate_reference_template(self):
        r = run_script("psy-ref-create", "generate-reference-file-template.py", ["test-theory"])
        assert r.returncode == 0

    def test_audit_reference_library_health(self):
        r = run_script("psy-ref-maintain", "audit-reference-library-health.py")
        assert r.returncode == 0
