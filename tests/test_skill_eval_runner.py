"""Unit tests for the structural skill-eval runner.

These tests cover:
- Each of the 6 checker predicates on synthetic (exit_code, stdout, fs_state) inputs
- Discovery: skills without evals.yaml are UNMAPPED (not FAIL)
- Tally: exit code logic (any FAIL → 1, all pass → 0)
- Pilot evals.yaml integration (runs green against synthetic fixture)

Design note: checkers here are boolean PREDICATES on (exit_code, stdout, fs_state),
not value-extractors. Keep this file distinct from tests/golden/run_evals.py logic.
"""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

# Ensure runner is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests" / "golden"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))

REPO = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO / "tests" / "golden" / "run_skill_evals.py"
PILOT_EVALS = REPO / ".claude" / "skills" / "evl-validate" / "evals.yaml"
SYNTHETIC = REPO / "e2e" / "synthetic-project"
PY = str(REPO / ".claude" / "skills" / ".venv" / "bin" / "python3")


def _fake_run(returncode=0, stdout="", stderr=""):
    """Produce a subprocess.CompletedProcess-like namespace for checker tests."""
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


# ---------------------------------------------------------------------------
# Import the runner module under test
# ---------------------------------------------------------------------------

def _import_runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_skill_evals", RUNNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def runner():
    return _import_runner()


# ---------------------------------------------------------------------------
# Checker: file_exists
# ---------------------------------------------------------------------------

def test_file_exists_pass(runner, tmp_path):
    f = tmp_path / "output.txt"
    f.write_text("ok")
    verdict, _ = runner.CHECKERS["file_exists"]({"path": str(f)}, None, {})
    assert verdict == "PASS"


def test_file_exists_fail(runner, tmp_path):
    missing = tmp_path / "nonexistent.txt"
    verdict, detail = runner.CHECKERS["file_exists"]({"path": str(missing)}, None, {})
    assert verdict == "FAIL"
    assert "missing" in detail.lower() or str(missing) in detail


# ---------------------------------------------------------------------------
# Checker: file_absent
# ---------------------------------------------------------------------------

def test_file_absent_pass(runner, tmp_path):
    missing = tmp_path / "should_not_exist.txt"
    verdict, _ = runner.CHECKERS["file_absent"]({"path": str(missing)}, None, {})
    assert verdict == "PASS"


def test_file_absent_fail(runner, tmp_path):
    f = tmp_path / "present.txt"
    f.write_text("oops")
    verdict, _ = runner.CHECKERS["file_absent"]({"path": str(f)}, None, {})
    assert verdict == "FAIL"


# ---------------------------------------------------------------------------
# Checker: exit_zero
# ---------------------------------------------------------------------------

def test_exit_zero_pass(runner):
    run = _fake_run(returncode=0)
    verdict, _ = runner.CHECKERS["exit_zero"]({}, run, {})
    assert verdict == "PASS"


def test_exit_zero_fail(runner):
    run = _fake_run(returncode=1, stderr="something went wrong")
    verdict, detail = runner.CHECKERS["exit_zero"]({}, run, {})
    assert verdict == "FAIL"
    assert "1" in detail


def test_exit_zero_no_run(runner):
    verdict, _ = runner.CHECKERS["exit_zero"]({}, None, {})
    assert verdict == "FAIL"


# ---------------------------------------------------------------------------
# Checker: stdout_contains
# ---------------------------------------------------------------------------

def test_stdout_contains_pass(runner):
    run = _fake_run(stdout='{"verdict": "PASS"}')
    verdict, _ = runner.CHECKERS["stdout_contains"]({"substr": "PASS"}, run, {})
    assert verdict == "PASS"


def test_stdout_contains_fail(runner):
    run = _fake_run(stdout='{"verdict": "FAIL"}')
    verdict, _ = runner.CHECKERS["stdout_contains"]({"substr": "PASS"}, run, {})
    assert verdict == "FAIL"


def test_stdout_contains_checks_stderr_too(runner):
    """stdout_contains should also scan stderr (matches sibling behavior)."""
    run = _fake_run(stdout="", stderr="PASS in stderr")
    verdict, _ = runner.CHECKERS["stdout_contains"]({"substr": "PASS"}, run, {})
    assert verdict == "PASS"


def test_stdout_contains_no_run(runner):
    verdict, _ = runner.CHECKERS["stdout_contains"]({"substr": "x"}, None, {})
    assert verdict == "FAIL"


# ---------------------------------------------------------------------------
# Checker: stdout_absent
# ---------------------------------------------------------------------------

def test_stdout_absent_pass(runner):
    run = _fake_run(stdout="clean output")
    verdict, _ = runner.CHECKERS["stdout_absent"]({"substr": "ERROR"}, run, {})
    assert verdict == "PASS"


def test_stdout_absent_fail(runner):
    run = _fake_run(stdout="ERROR: something bad")
    verdict, _ = runner.CHECKERS["stdout_absent"]({"substr": "ERROR"}, run, {})
    assert verdict == "FAIL"


# ---------------------------------------------------------------------------
# Checker: stdout_json
# ---------------------------------------------------------------------------

def test_stdout_json_key_present(runner):
    run = _fake_run(stdout='{"verdict": "PASS", "rubrics": []}')
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "verdict"}, run, {})
    assert verdict == "PASS"


def test_stdout_json_nested_key(runner):
    run = _fake_run(stdout='{"outer": {"inner": "value"}}')
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "outer.inner"}, run, {})
    assert verdict == "PASS"


def test_stdout_json_key_absent(runner):
    run = _fake_run(stdout='{"other": "stuff"}')
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "verdict"}, run, {})
    assert verdict == "FAIL"


def test_stdout_json_equals_pass(runner):
    run = _fake_run(stdout='{"verdict": "PASS"}')
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "verdict", "equals": "PASS"}, run, {})
    assert verdict == "PASS"


def test_stdout_json_equals_fail(runner):
    run = _fake_run(stdout='{"verdict": "FAIL"}')
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "verdict", "equals": "PASS"}, run, {})
    assert verdict == "FAIL"


def test_stdout_json_invalid_json(runner):
    run = _fake_run(stdout="not json at all")
    verdict, detail = runner.CHECKERS["stdout_json"]({"path": "verdict"}, run, {})
    assert verdict == "FAIL"
    assert "json" in detail.lower() or "JSON" in detail


def test_stdout_json_no_run(runner):
    verdict, _ = runner.CHECKERS["stdout_json"]({"path": "verdict"}, None, {})
    assert verdict == "FAIL"


# ---------------------------------------------------------------------------
# Unknown checker → hard FAIL (misconfiguration must be loud)
# ---------------------------------------------------------------------------

def test_unknown_checker_is_fail(runner, tmp_path):
    evals_yaml = tmp_path / "evals.yaml"
    evals_yaml.write_text(
        "scenarios:\n"
        "  - id: s1\n"
        "    exec: null\n"
        "    assertions:\n"
        "      - id: a1\n"
        "        check: nonexistent_checker_xyz\n"
    )
    rows, tally = runner.run_skill(evals_yaml, tmp_path, strict=False)
    assert tally["FAIL"] >= 1


# ---------------------------------------------------------------------------
# Discovery: skills with no evals.yaml → UNMAPPED (not FAIL)
# ---------------------------------------------------------------------------

def test_discovery_skips_skills_without_evals(runner, tmp_path):
    """run_skill_evals.discover_evals returns only skills that have evals.yaml."""
    # Create a fake skills root with one skill that has evals.yaml and one that does not
    skills_root = tmp_path / ".claude" / "skills"
    skill_with = skills_root / "fw-with-evals"
    skill_without = skills_root / "fw-without-evals"
    skill_with.mkdir(parents=True)
    skill_without.mkdir(parents=True)

    (skill_with / "evals.yaml").write_text(
        "scenarios:\n"
        "  - id: s1\n"
        "    exec: null\n"
        "    assertions: []\n"
    )

    found = list(runner.discover_evals(skills_root))
    assert any("fw-with-evals" in str(p) for p in found)
    assert not any("fw-without-evals" in str(p) for p in found)


# ---------------------------------------------------------------------------
# Tally: exit-code contract
# ---------------------------------------------------------------------------

def test_tally_exit_zero_on_all_pass(runner, tmp_path):
    evals_yaml = tmp_path / "evals.yaml"
    f = tmp_path / "out.txt"
    f.write_text("content")
    evals_yaml.write_text(
        f"scenarios:\n"
        f"  - id: s1\n"
        f"    exec: null\n"
        f"    assertions:\n"
        f"      - id: a1\n"
        f"        check: file_exists\n"
        f"        path: {str(f)}\n"
    )
    rows, tally = runner.run_skill(evals_yaml, tmp_path, strict=False)
    assert tally["FAIL"] == 0
    assert tally["PASS"] >= 1


def test_tally_exit_one_on_any_fail(runner, tmp_path):
    evals_yaml = tmp_path / "evals.yaml"
    missing = tmp_path / "does_not_exist.txt"
    evals_yaml.write_text(
        f"scenarios:\n"
        f"  - id: s1\n"
        f"    exec: null\n"
        f"    assertions:\n"
        f"      - id: a1\n"
        f"        check: file_exists\n"
        f"        path: {str(missing)}\n"
    )
    rows, tally = runner.run_skill(evals_yaml, tmp_path, strict=False)
    assert tally["FAIL"] >= 1


# ---------------------------------------------------------------------------
# Pilot integration: pilot evals.yaml runs green against synthetic fixture
# ---------------------------------------------------------------------------

def test_pilot_evals_yaml_exists():
    """Pilot evals.yaml must exist at the declared path."""
    assert PILOT_EVALS.is_file(), f"Pilot evals.yaml not found at {PILOT_EVALS}"


def test_pilot_evals_runs_green_via_subprocess():
    """run_skill_evals.py --evals ... exits 0 against synthetic fixture (PASS gate)."""
    result = subprocess.run(
        [PY, str(RUNNER_PATH), "--evals", str(PILOT_EVALS)],
        capture_output=True,
        text=True,
        timeout=60,
        env={
            **__import__("os").environ,
            "PMC_PROJECT_ROOT": str(SYNTHETIC),
            "PYTHONPATH": str(REPO / ".claude" / "scripts"),
            "CK_CACHE_DIR": "/tmp/ck-eval-test-cache",
        },
    )
    assert result.returncode == 0, (
        f"Pilot gate failed (exit {result.returncode}):\nstdout={result.stdout}\nstderr={result.stderr}"
    )


def test_pilot_gate_bites_when_output_removed(runner, tmp_path):
    """Gate must exit 1 when a file_exists check fails (gate actually bites)."""
    # Create a local evals.yaml that checks for a file we control
    evals_yaml = tmp_path / "evals.yaml"
    nonexistent = tmp_path / "not_there.txt"
    evals_yaml.write_text(
        f"scenarios:\n"
        f"  - id: gate_test\n"
        f"    exec: null\n"
        f"    assertions:\n"
        f"      - id: check_output\n"
        f"        check: file_exists\n"
        f"        path: {str(nonexistent)}\n"
    )
    import subprocess as sp
    result = sp.run(
        [PY, str(RUNNER_PATH), "--evals", str(evals_yaml)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0, "Gate should exit 1 when file_exists check fails"
