"""C6 — pytest wrapper over the project script test matrix (Batch 10 Phase 3).

Asserts run-project-script-tests.py finds every project script green, and that a deliberately
broken fixture is caught (no fake-pass). Scope = project scripts only; the runner never touches
.claude/hooks/* (asserted by grep gate below).
"""
import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / ".claude" / "scripts" / "run-project-script-tests.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner = _load(RUNNER, "project_script_runner")


def test_all_project_scripts_green():
    m = runner.run_matrix()
    assert m["failed"] == 0, f"broken project scripts: {[f['script'] for f in m['failures']]}"
    assert m["total"] >= 100, "matrix should cover the full project script corpus"


def test_matrix_covers_all_six_frameworks():
    scripts = [s.as_posix() for s in runner.discover()]
    for fw in ("mat-", "psy-", "cre-", "gro-", "orc-", "com-"):
        assert any(f"/{fw}" in s for s in scripts), f"no scripts discovered for framework {fw}"
    assert any("platform_lib/" in s for s in scripts)


def test_broken_fixture_is_caught(tmp_path):
    bad = tmp_path / "broken.py"
    bad.write_text("def oops(:\n    pass\n", encoding="utf-8")  # syntax error
    result = runner.check(bad)
    assert result["ok"] is False
    assert result["stage"] == "syntax"


def test_runner_does_not_discover_hooks():
    # OQ-10b A: the matrix exercises project scripts only, never ck/project hooks.
    discovered = [s.as_posix() for s in runner.discover()]
    assert not any("/.claude/hooks/" in s or "/hooks/" in s for s in discovered)
