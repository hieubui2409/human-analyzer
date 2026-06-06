"""Test CRE framework scripts with mock data."""
import subprocess
import os
from pathlib import Path

import pytest
from venv_python import VENV_PYTHON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(VENV_PYTHON)
MOCK_DATA = PROJECT_ROOT / "tests" / "mock-data"

from platform_lib.paths import ALL_CHARS  # roster sourced dynamically — no hardcoded slug

pytestmark = pytest.mark.skipif(not ALL_CHARS, reason="no character roster — toolkit-only pack")
_CHAR = ALL_CHARS[0] if ALL_CHARS else "x"  # exercise the first real character; name-free

ENV = {
    **os.environ,
    "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts"),
    "MOCK_DATA_DIR": str(MOCK_DATA),
}


def run_script(skill, script, args=None):
    path = PROJECT_ROOT / ".claude" / "skills" / skill / "scripts" / script
    cmd = [PYTHON, str(path)] + (args or [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=ENV)


class TestVoiceAudit:
    def test_extract_voice_profile(self):
        r = run_script("cre-voice-audit", "extract-voice-profile-from-writing-voice-md.py",
                       ["--character", _CHAR])
        assert r.returncode == 0

    def test_voice_consistency_check(self):
        r = run_script("cre-voice-audit", "check-voice-consistency-against-defense-profile.py",
                       ["--character", _CHAR,
                        str(MOCK_DATA / "assets" / "test-post")])
        assert r.returncode == 0

    def test_published_assets_stats(self):
        r = run_script("cre-voice-audit", "scan-published-assets-post-statistics.py")
        assert r.returncode == 0


class TestPrivacyGuard:
    def test_extract_confidential_names(self):
        r = run_script("cre-privacy-guard", "extract-confidential-names-from-all-profiles.py")
        assert r.returncode == 0

    def test_scan_assets_privacy(self):
        r = run_script("cre-privacy-guard", "scan-assets-for-privacy-violations.py", ["--dir", "assets/"])
        # returncode 2 = found violations (expected), 0 = clean
        assert (r.returncode in (0, 2) or r.stdout.strip()) and "Traceback" not in r.stderr


class TestPostWriter:
    def test_evidence_tier_compliance(self):
        # relocated to cre:evidence-scanner (Batch 6 B8) — post-writer now delegates
        r = run_script("cre-evidence-scanner", "map-claims-to-evidence-tiers.py",
                       [str(MOCK_DATA / "assets" / "test-post")])
        assert r.returncode == 0

    def test_psy_to_cre_translation(self):
        r = run_script("cre-post-writer", "extract-psy-to-cre-translation-context.py",
                       ["--character", _CHAR])
        assert r.returncode == 0


class TestPromptLeverage:
    def test_extract_factual_constraints(self):
        r = run_script("cre-prompt-leverage", "extract-factual-constraints-from-profile.py",
                       ["--character", _CHAR])
        assert r.returncode == 0


class TestExploring:
    def test_extract_context_decisions(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# CONTEXT\n\n## Decisions\n- Use mock data\n")
            tmp = f.name
        try:
            r = run_script("cre-exploring", "extract-context-decisions-from-context-md.py", ["--file", tmp])
            assert r.returncode == 0
        finally:
            Path(tmp).unlink(missing_ok=True)


class TestRepurpose:
    def test_list_platform_inventory(self):
        r = run_script("cre-repurpose", "list-platform-content-inventory.py")
        assert r.returncode == 0
