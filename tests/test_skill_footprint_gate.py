"""Static assertions: SIZE baseline-compare gate + GATE co-presence gate.

SIZE gate: --baseline writes per-skill line counts; --gate fails if a skill
exceeds baseline beyond tolerance.  CO-PRESENCE gate: every GATE-<UPPER> token
referenced in skill SKILL.md / rules must have a full-prose <GATE-X>…</GATE-X>
definition somewhere reachable (gates-and-anti-rationalization.md is always-on).

This is a STATIC authored-doc size + gate-ref integrity check — distinct from the
runtime context-budget-gauge.cjs (live session tokens).  Both are deterministic,
no network, stdlib-only.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts"))

PLATFORM_LIB = PROJECT_ROOT / ".claude" / "scripts" / "platform_lib"
AUDIT_SCRIPT = (
    PROJECT_ROOT / ".claude" / "skills" / "orc-skill-stocktake" / "scripts"
    / "audit-skill-progressive-disclosure.py"
)
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"
GATES_FILE = (
    SKILLS_DIR / "_framework-shared" / "references" / "gates-and-anti-rationalization.md"
)
BASELINE_JSON = SKILLS_DIR / "_framework-shared" / "skill-footprint-baseline.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def copresence():
    return _load_module(PLATFORM_LIB / "gate_copresence.py", "gate_copresence")


@pytest.fixture(scope="session")
def audit():
    return _load_module(AUDIT_SCRIPT, "pd_audit")


# ── GATE_RE contract ─────────────────────────────────────────────────────────

class TestGateRegex:
    def test_matches_uppercase_token(self, copresence):
        m = copresence.GATE_RE.search("see GATE-SCOUT-FIRST for details")
        assert m is not None
        assert m.group("suffix") == "SCOUT-FIRST"

    def test_matches_single_char_suffix(self, copresence):
        m = copresence.GATE_RE.search("GATE-X is here")
        assert m is not None
        assert m.group("suffix") == "X"

    def test_does_not_match_mid_word(self, copresence):
        # MITIGATE-X should not match since GATE is mid-word
        assert copresence.GATE_RE.search("MITIGATE-XYZ") is None

    def test_does_not_match_lowercase(self, copresence):
        assert copresence.GATE_RE.search("gate-foo") is None

    def test_does_not_match_trailing_dash(self, copresence):
        # GATE-FOO- should match GATE-FOO, not GATE-FOO-
        m = copresence.GATE_RE.search("GATE-FOO-")
        assert m is not None
        assert m.group("suffix") == "FOO"

    def test_does_not_match_hard_gate_prefix(self, copresence):
        # HARD-GATE-X: the dash before GATE is a compound separator.
        # Lookbehind excludes preceding dash, so HARD-GATE-X does not match.
        assert copresence.GATE_RE.search("HARD-GATE-SCOUT-FIRST") is None


# ── CO-PRESENCE gate ─────────────────────────────────────────────────────────

class TestCopresenceGate:
    def _make_skill(self, tmp_path: Path, name: str, body: str) -> Path:
        d = tmp_path / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(body, encoding="utf-8")
        return d

    def test_orphan_gate_ref_fails(self, copresence, tmp_path):
        """A SKILL.md referencing GATE-NONEXISTENT with no definition fails."""
        sk = self._make_skill(
            tmp_path, "orc-test",
            "See GATE-NONEXISTENT for the policy.\n"
        )
        always_on = ""  # no definitions in always-on layer
        failures = copresence.check_copresence([sk], always_on)
        assert any("GATE-NONEXISTENT" in f for f in failures), (
            f"Expected GATE-NONEXISTENT to be flagged; got: {failures}"
        )

    def test_gate_defined_in_always_on_passes(self, copresence, tmp_path):
        """GATE referenced in skill but defined in always-on layer passes."""
        sk = self._make_skill(
            tmp_path, "orc-test",
            "See GATE-VERIFIED-STICKY for the policy.\n"
        )
        always_on = "<GATE-VERIFIED-STICKY>\nFull prose here.\n</GATE-VERIFIED-STICKY>\n"
        failures = copresence.check_copresence([sk], always_on)
        assert not failures, f"Expected no failures; got: {failures}"

    def test_gate_defined_in_same_skill_passes(self, copresence, tmp_path):
        """A GATE both referenced and defined (full-prose tag) in the same SKILL.md passes."""
        sk = self._make_skill(
            tmp_path, "orc-test",
            "<GATE-LOCAL>\nFull prose definition here.\n</GATE-LOCAL>\n\nSee GATE-LOCAL.\n"
        )
        always_on = ""
        failures = copresence.check_copresence([sk], always_on)
        assert not failures, f"Expected no failures; got: {failures}"

    def test_prose_mention_without_definition_fails(self, copresence, tmp_path):
        """Bare GATE mention in prose (no XML tag definition) with no always-on home fails."""
        sk = self._make_skill(
            tmp_path, "orc-test",
            "This follows GATE-FOO convention.\n"
        )
        always_on = ""
        failures = copresence.check_copresence([sk], always_on)
        assert any("GATE-FOO" in f for f in failures)

    def test_real_repo_passes_copresence(self, copresence):
        """All project-owned skill SKILL.md files in the real repo pass CO-PRESENCE.

        The always-on layer is gates-and-anti-rationalization.md.
        """
        assert GATES_FILE.exists(), f"gates file not found: {GATES_FILE}"
        always_on = GATES_FILE.read_text(encoding="utf-8")
        skill_dirs = [
            d for d in sorted(SKILLS_DIR.iterdir())
            if d.is_dir() and not d.name.startswith((".", "_"))
            and (d / "SKILL.md").exists()
        ]
        failures = copresence.check_copresence(skill_dirs, always_on)
        assert not failures, (
            "Real repo CO-PRESENCE failures (fix the orphan GATE refs):\n"
            + "\n".join(failures)
        )


# ── SIZE gate ────────────────────────────────────────────────────────────────

class TestSizeGate:
    def test_above_baseline_fails(self, audit, tmp_path):
        """A skill whose SKILL.md exceeds baseline by more than tolerance fails."""
        # Baseline says 1 line; tolerance = max(40, 20% of 1) = 40.
        # Current must be > 1 + 40 = 41 lines to trigger.
        current_lines = 50
        baseline = {"orc-test": {"skill_md_lines": 1, "total_lines": 1}}
        ok, regressions = audit.size_gate(
            {"orc-test": {"skill_md_lines": current_lines, "total_lines": current_lines}},
            baseline,
        )
        assert not ok, "Expected size gate to fail on bloated skill"
        assert any("orc-test" in r for r in regressions)

    def test_within_tolerance_passes(self, audit, tmp_path):
        """A skill slightly above baseline (within tolerance) passes."""
        baseline = {"orc-test": {"skill_md_lines": 100, "total_lines": 100}}
        current = {"orc-test": {"skill_md_lines": 110, "total_lines": 110}}
        ok, regressions = audit.size_gate(current, baseline)
        assert ok, f"Expected pass within tolerance; regressions: {regressions}"

    def test_new_skill_absent_from_baseline_fails(self, audit):
        """A skill absent from baseline is treated as growth (gate fails until re-baselined)."""
        baseline = {}
        current = {"orc-newskill": {"skill_md_lines": 50, "total_lines": 50}}
        ok, regressions = audit.size_gate(current, baseline)
        assert not ok
        assert any("orc-newskill" in r for r in regressions)

    def test_real_repo_passes_size_gate(self, audit):
        """Current repo line counts pass against the committed baseline JSON."""
        assert BASELINE_JSON.exists(), (
            f"Baseline JSON not found: {BASELINE_JSON}\n"
            "Run: python audit-skill-progressive-disclosure.py --baseline to generate it."
        )
        baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
        measured = audit.measure_all_skills(SKILLS_DIR)
        ok, regressions = audit.size_gate(measured, baseline)
        assert ok, "Real repo SIZE gate failures:\n" + "\n".join(regressions)
