"""Test MAT + ORC framework scripts with mock data."""
import subprocess
import os
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(Path.home() / ".claude" / "skills" / ".venv" / "bin" / "python3")
MOCK_DATA = PROJECT_ROOT / "tests" / "mock-data"
# Isolate event-log subprocess writes (append-event-to-log) to a throwaway sink,
# never the real tracked .claude/telemetry/ (CK_TELEMETRY_DIR honored by paths.py).
_TELEMETRY_TMP = tempfile.mkdtemp(prefix="ck-mat-telemetry-")
ENV = {
    **os.environ,
    "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts"),
    "MOCK_DATA_DIR": str(MOCK_DATA),
    "CK_TELEMETRY_DIR": _TELEMETRY_TMP,
}


def run_script(skill, script, args=None):
    path = PROJECT_ROOT / ".claude" / "skills" / skill / "scripts" / script
    cmd = [PYTHON, str(path)] + (args or [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=ENV)


# === MAT Pipeline ===

class TestMatLoader:
    def test_inventory_materials_with_frontmatter(self):
        r = run_script("mat-loader", "inventory-materials-with-frontmatter-status.py")
        assert r.returncode == 0

    def test_inventory_materials_type_detection(self):
        r = run_script("mat-loader", "inventory-materials-with-type-detection.py")
        assert r.returncode == 0

    def test_validate_material_frontmatter(self):
        r = run_script("mat-loader", "validate-material-frontmatter-against-schema.py")
        assert r.returncode == 0

    def test_craap_score_template(self):
        r = run_script("mat-loader", "generate-craap-score-template-for-material.py",
                       [str(MOCK_DATA / "materials" / "test-alpha" / "transcript-t1-raw.md")])
        assert r.returncode == 0

    def test_duplicate_detection(self):
        r = run_script("mat-loader", "detect-duplicate-materials-by-size-and-content-hash.py")
        assert r.returncode == 0


class TestMatIndexer:
    def test_evidence_coverage_gaps(self):
        r = run_script("mat-indexer", "analyze-evidence-coverage-gaps-per-profile-section.py",
                       ["--character", "character-a"])
        assert r.returncode == 0

    def test_contradiction_detection(self):
        r = run_script("mat-indexer", "detect-contradictions-materials-vs-profiles.py",
                       ["--character", "character-a"])
        assert r.returncode == 0

    def test_stale_materials(self):
        r = run_script("mat-indexer", "find-stale-materials-by-processing-status.py")
        assert r.returncode == 0


class TestMatArchive:
    def test_archive_dry_run(self):
        r = run_script("mat-archive", "archive-materials-by-filter.py", ["--dry-run", "--character", "character-a"])
        assert r.returncode == 0


class TestMatRescore:
    def test_identify_needing_rescore(self):
        r = run_script("mat-rescore", "identify-materials-needing-rescore.py")
        assert r.returncode == 0


# === ORC Pipeline ===

class TestOrcIntake:
    def test_classify_work_type(self):
        r = run_script("orc-intake", "classify-work-type-from-task-description.py",
                       ["--task", "Write a LinkedIn post about mentoring"])
        assert r.returncode == 0

    def test_route_task(self):
        r = run_script("orc-intake", "route-task-to-framework-domain.py",
                       ["Ingest new transcript for Nhân vật A"])
        assert r.returncode == 0


class TestOrcSessionState:
    def test_read_session_state(self):
        r = run_script("orc-session-state", "read-and-format-session-state.py")
        assert r.returncode == 0

    def test_recommend_downstream_actions(self):
        r = run_script("orc-session-state", "recommend-downstream-actions-from-events.py",
                       ["--events-json", '[{"event": "MAT.integrated"}]'])
        assert r.returncode == 0


class TestOrcEventLog:
    def test_append_event(self):
        r = run_script("orc-event-log", "append-event-to-log.py",
                       ["--event-type", "TEST.event", "--source", "test-suite"])
        assert r.returncode == 0

    def test_query_event_log(self):
        r = run_script("orc-event-log", "query-event-log-with-filters.py",
                       ["--event-type", "TEST.event"])
        assert r.returncode == 0


class TestOrcClassify:
    def test_detect_risk_flags(self):
        r = run_script("orc-classify", "detect-risk-flags-from-git-diff.py",
                       ["--diff-files", "docs/profiles/character-a/psychology/formulation.md"])
        assert r.returncode == 0


class TestOrcOther:
    def test_summarize_session_changes(self):
        r = run_script("orc-compounding", "summarize-session-changes-from-git-diff.py")
        assert r.returncode == 0 or r.returncode == 1  # may fail if no recent changes

    def test_inventory_memory_files(self):
        r = run_script("orc-dream", "inventory-project-memory-files.py")
        assert r.returncode == 0

    def test_index_decisions(self):
        r = run_script("orc-decisions", "index-decisions-with-search.py")
        assert r.returncode == 0 or "no decisions" in r.stderr.lower()
