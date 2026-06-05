#!/usr/bin/env python3
"""Golden-case eval runner for the deterministic framework skills.

Runs each case in `evals.json` against the synthetic fixture (PMC_PROJECT_ROOT) and asserts the extracted
value equals the frozen golden. Deterministic only — a mismatch means a real behavior change (regenerate the
golden on purpose, or it's a regression). Wired into CI. Exit 0 = all pass, 1 = any mismatch.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = str(REPO / ".claude" / "skills" / ".venv" / "bin" / "python3")
PY = PY if Path(PY).exists() else sys.executable


def _extract(data, spec):
    if "len" in spec:
        path = spec["len"]
        node = data if path == "." else _dig(data, path)
        return len(node)
    node = _dig(data, spec["value"])
    return node


def _dig(data, dotted):
    for part in dotted.split("."):
        data = data[part]
    return data


def main():
    spec = json.loads((REPO / "eval" / "evals.json").read_text(encoding="utf-8"))
    fixture = REPO / spec["fixture"]
    env = dict(os.environ)
    env["PMC_PROJECT_ROOT"] = str(fixture)
    env["PYTHONPATH"] = str(REPO / ".claude" / "scripts")
    env["CK_CACHE_DIR"] = "/tmp/ck-eval-cache"

    failures = []
    for case in spec["cases"]:
        cmd = [PY, str(REPO / case["script"])] + case["args"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, env=env)
        try:
            data = json.loads(r.stdout)
            actual = _extract(data, case["extract"])
        except Exception as e:  # noqa: BLE001
            failures.append(f"{case['id']}: could not extract ({e}); stderr={r.stderr[:200]}")
            print(f"[ERROR] {case['id']}")
            continue
        if actual == case["expected"]:
            print(f"[PASS]  {case['id']} ({case['skill']}) = {actual}")
        else:
            failures.append(f"{case['id']}: expected {case['expected']}, got {actual}")
            print(f"[FAIL]  {case['id']} ({case['skill']}): expected {case['expected']}, got {actual}")

    print(f"\n{len(spec['cases']) - len(failures)}/{len(spec['cases'])} golden cases pass")
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
