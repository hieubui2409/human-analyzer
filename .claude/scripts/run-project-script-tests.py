"""Project script test runner (C6) — subprocess-exercise every PROJECT script as a matrix.

GOLDEN RULE #4: deterministic gather only. Enumerates project-owned Python scripts
(`platform_lib/*` modules + framework skill `scripts/*.py` across all 7 frameworks) and runs
each through two cheap subprocess smokes: py_compile (syntax) + `--help`/import (entry sanity).
Reports a pass/fail matrix and exits non-zero on any failure.

Scope is PROJECT scripts only (OQ-10b A). It NEVER touches `.claude/hooks/*` — ck owns + tests
its own hooks; the project hooks (B3 observer, C5 digest) are exercised by their own pytest unit.
Complements the existing per-script import test (which omits orc/gro) with full-framework coverage.

Usage:
  run-project-script-tests.py [--json] [--quiet]
  exit 0 = all green; exit 1 = at least one script failed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".claude" / "skills"
PLATFORM_LIB = ROOT / ".claude" / "scripts" / "platform_lib"
PYTHON = Path.home() / ".claude" / "skills" / ".venv" / "bin" / "python3"
if not PYTHON.exists():
    PYTHON = ROOT / ".claude" / "skills" / ".venv" / "bin" / "python3"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)  # no project venv (e.g. CI): use the running interpreter
FRAMEWORKS = ("mat", "psy", "cre", "gro", "orc", "com", "evl")


def discover() -> list[Path]:
    scripts: list[Path] = []
    for mod in sorted(PLATFORM_LIB.glob("*.py")):
        if mod.name != "__init__.py":
            scripts.append(mod)
    for fw in FRAMEWORKS:
        for skill in sorted(SKILLS.glob(f"{fw}-*")):
            sdir = skill / "scripts"
            if sdir.is_dir():
                for py in sorted(sdir.glob("*.py")):
                    if py.name != "__init__.py":
                        scripts.append(py)
    return scripts


def _run(cmd: list[str]) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        return r.returncode == 0, (r.stderr or r.stdout)[-400:]
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def _import_check(script: Path) -> tuple[bool, str]:
    """Import sanity. platform_lib is a package (relative imports) — import it by package
    name with .claude/scripts on sys.path; standalone skill scripts load via spec loader."""
    scripts_dir = ROOT / ".claude" / "scripts"
    if script.parent == PLATFORM_LIB:
        code = (f"import sys; sys.path.insert(0, r'{scripts_dir}'); "
                f"import platform_lib.{script.stem}")
    else:
        code = (f"import importlib.util,sys; sys.path.insert(0, r'{scripts_dir}'); "
                f"s=importlib.util.spec_from_file_location('m',r'{script}'); "
                f"m=importlib.util.module_from_spec(s); s.loader.exec_module(m)")
    return _run([str(PYTHON), "-c", code])


def check(script: Path) -> dict:
    try:
        rel = script.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(script)  # script outside the repo (e.g. a test fixture)
    ok_syntax, err = _run([str(PYTHON), "-c",
                           f"import py_compile; py_compile.compile(r'{script}', doraise=True)"])
    if not ok_syntax:
        return {"script": rel, "ok": False, "stage": "syntax", "detail": err}
    # entry sanity: --help should exit 0 OR the module imports cleanly (libs have no CLI).
    ok_help, _ = _run([str(PYTHON), str(script), "--help"])
    if not ok_help:
        ok_import, err2 = _import_check(script)
        if not ok_import:
            return {"script": rel, "ok": False, "stage": "entry", "detail": err2}
    return {"script": rel, "ok": True, "stage": "ok", "detail": ""}


def run_matrix() -> dict:
    results = [check(s) for s in discover()]
    failed = [r for r in results if not r["ok"]]
    return {"total": len(results), "passed": len(results) - len(failed),
            "failed": len(failed), "failures": failed, "results": results}


def main() -> None:
    ap = argparse.ArgumentParser(description="Project script test matrix (C6, READ-ONLY).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    m = run_matrix()
    if args.json:
        print(json.dumps(m, indent=2, ensure_ascii=False))
    elif not args.quiet:
        print(f"\nProject script matrix — {m['passed']}/{m['total']} passed")
        for f in m["failures"]:
            print(f"  ✗ {f['script']} [{f['stage']}] {f['detail'][:120]}")
        if not m["failures"]:
            print("  ✓ all project scripts compile + entry-sane")

    raise SystemExit(1 if m["failed"] else 0)


if __name__ == "__main__":
    main()
