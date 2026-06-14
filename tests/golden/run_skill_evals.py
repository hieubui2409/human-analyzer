#!/usr/bin/env python3
"""Structural skill-eval runner — boolean-predicate checks (file_exists, exit_zero,
stdout_contains, …) against the synthetic fixture. Discovers evals.yaml under
.claude/skills/ (opt-in per skill). Exits 0 = all PASS, 1 = any FAIL.

Distinct from run_evals.py (frozen value-equality goldens). Schema + catalog:
.claude/skills/_framework-shared/references/skill-eval-contract.md

Usage:
  python run_skill_evals.py                   # discover all evals.yaml
  python run_skill_evals.py --evals <path>    # run one specific evals.yaml
  python run_skill_evals.py --strict          # UNMAPPED → FAIL exit
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

REPO = Path(__file__).resolve().parents[2]
PY = str(REPO / ".claude" / "skills" / ".venv" / "bin" / "python3")
PY = PY if Path(PY).exists() else sys.executable
PASS, FAIL, SKIP, UNMAPPED = "PASS", "FAIL", "SKIP", "UNMAPPED"


def _load_doc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return _yaml.safe_load(text) if _yaml else json.loads(text)


def _scenarios(doc: dict) -> list[dict]:
    return doc.get("scenarios") or doc.get("evals") or []


def _subst(value, ctx: dict):
    if isinstance(value, str):
        for k, v in ctx.items():
            value = value.replace("{" + k + "}", str(v))
        return value
    return [_subst(v, ctx) for v in value] if isinstance(value, list) else value


# Checkers: boolean predicates on (assertion_dict, completed_run | None, ctx)
def _c_file_exists(a, run, ctx):
    p = Path(_subst(a["path"], ctx))
    return (PASS, str(p)) if p.is_file() else (FAIL, f"missing file {p}")

def _c_file_absent(a, run, ctx):
    p = Path(_subst(a["path"], ctx))
    return (FAIL, f"unexpected file {p}") if p.exists() else (PASS, f"absent {p}")

def _c_exit_zero(a, run, ctx):
    if run is None:
        return (FAIL, "no exec run for exit_zero check")
    return (PASS, "exit 0") if run.returncode == 0 else (FAIL, f"exit {run.returncode}: {run.stderr[:160]}")

def _c_stdout_contains(a, run, ctx):
    if run is None:
        return (FAIL, "no exec run")
    needle = _subst(a["substr"], ctx)
    combined = (run.stdout or "") + (run.stderr or "")
    return (PASS, f"found {needle!r}") if needle in combined else (FAIL, f"missing {needle!r}")

def _c_stdout_absent(a, run, ctx):
    if run is None:
        return (FAIL, "no exec run")
    needle = _subst(a["substr"], ctx)
    combined = (run.stdout or "") + (run.stderr or "")
    return (FAIL, f"leaked {needle!r}") if needle in combined else (PASS, f"absent {needle!r}")

def _c_stdout_json(a, run, ctx):
    if run is None:
        return (FAIL, "no exec run")
    try:
        data = json.loads(run.stdout)
    except Exception as e:  # noqa: BLE001
        return (FAIL, f"stdout not valid JSON: {e}")
    cur = data
    for key in a["path"].split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return (FAIL, f"path {a['path']!r} absent in JSON output")
    if "equals" in a:
        exp = _subst(str(a["equals"]), ctx)
        return (PASS, f"{a['path']}=={cur!r}") if str(cur) == exp else (FAIL, f"{cur!r} != {exp!r}")
    return (PASS, f"{a['path']}=={cur!r}") if cur not in (None, "", []) else (FAIL, f"{a['path']} empty/null")


CHECKERS: dict = {
    "file_exists": _c_file_exists,
    "file_absent": _c_file_absent,
    "exit_zero": _c_exit_zero,
    "stdout_contains": _c_stdout_contains,
    "stdout_absent": _c_stdout_absent,
    "stdout_json": _c_stdout_json,
}


def _eval_assertion(a, run, ctx: dict, strict: bool):
    if not isinstance(a, dict):
        return (UNMAPPED, "bare-string assertion — no machine mapping")
    check = a.get("check")
    if not check:
        return (UNMAPPED, "structural assertion with no `check` mapping")
    fn = CHECKERS.get(check)
    if fn is None:
        return (FAIL, f"unknown checker {check!r} — misconfiguration is loud, never a skip")
    try:
        return fn(a, run, ctx)
    except Exception as e:  # noqa: BLE001
        return (FAIL, f"checker {check} raised {type(e).__name__}: {e}")


def run_skill(evals_path: Path, skill_dir: Path, strict: bool = False) -> tuple[list, dict]:
    """Run all scenarios in evals_path; return (rows, tally).

    rows: list of (scenario_id, assertion_id, verdict, detail)
    tally: dict keyed by PASS/FAIL/SKIP/UNMAPPED
    """
    doc = _load_doc(evals_path)
    rows: list = []
    tally: dict = {PASS: 0, FAIL: 0, SKIP: 0, UNMAPPED: 0}
    fixture_env = os.environ.get("PMC_PROJECT_ROOT")
    fixture = Path(fixture_env).resolve() if fixture_env else REPO / "e2e" / "synthetic-project"
    env = {**os.environ,
           "PMC_PROJECT_ROOT": str(fixture),
           "PYTHONPATH": str(REPO / ".claude" / "scripts"),
           "CK_CACHE_DIR": "/tmp/ck-eval-runner-cache"}
    ctx = {"repo": str(REPO), "fixture": str(fixture), "py": PY}

    for sc in _scenarios(doc):
        sid = sc.get("id", "unknown")
        run = None
        if sc.get("exec"):
            argv = [PY if a == "{py}" else a for a in _subst(sc["exec"], ctx)]
            run = subprocess.run(argv, capture_output=True, text=True, timeout=90,
                                 env=env, cwd=str(skill_dir))
        for a in sc.get("assertions", []):
            verdict, detail = _eval_assertion(a, run, ctx, strict)
            tally[verdict] = tally.get(verdict, 0) + 1
            aid = a.get("id") if isinstance(a, dict) else str(a)[:40]
            rows.append((sid, aid, verdict, detail))

    return rows, tally


def discover_evals(skills_root: Path):
    """Yield evals.yaml paths found directly inside each skill subdirectory."""
    if not skills_root.is_dir():
        return
    for skill_dir in sorted(skills_root.iterdir()):
        evals = skill_dir / "evals.yaml"
        if evals.is_file():
            yield evals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run structural evals.yaml checks for skills.")
    ap.add_argument("--evals", type=Path, help="Specific evals.yaml (skips discovery)")
    ap.add_argument("--skills-root", type=Path, default=REPO / ".claude" / "skills")
    ap.add_argument("--strict", action="store_true", help="UNMAPPED → FAIL exit")
    args = ap.parse_args(argv)

    evals_paths = [args.evals] if args.evals else list(discover_evals(args.skills_root))
    if not evals_paths:
        print("[run_skill_evals] No evals.yaml found — nothing to check.")
        return 0

    total: dict = {PASS: 0, FAIL: 0, SKIP: 0, UNMAPPED: 0}
    for evals_path in evals_paths:
        skill_dir = evals_path.parent
        rows, tally = run_skill(evals_path, skill_dir, strict=args.strict)
        for k, v in tally.items():
            total[k] = total.get(k, 0) + v
        width = max((len(str(r[1])) for r in rows), default=8)
        skill_name = skill_dir.name
        for sid, aid, verdict, detail in rows:
            print(f"  [{verdict:<8}] {skill_name}/{str(aid):<{width}}  {detail}")
        print(f"  {skill_name}: {tally[PASS]} pass · {tally[FAIL]} fail "
              f"· {tally[SKIP]} skip · {tally[UNMAPPED]} unmapped")

    print(f"\nTotal: {total[PASS]} pass · {total[FAIL]} fail "
          f"· {total[SKIP]} skip · {total[UNMAPPED]} unmapped")
    failed = total[FAIL] > 0 or (args.strict and total[UNMAPPED] > 0)
    if failed:
        print("EVAL GATE: FAIL", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
