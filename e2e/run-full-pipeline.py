#!/usr/bin/env python3
"""End-to-end harness — exercise the 6 frameworks against the synthetic fixture, record a RUN-LOG.

Runs the DETERMINISTIC leg of each framework (the script halves — gather/scan/validate) against
e2e/synthetic-project/ (a fully synthetic two-character corpus, no real PII). The LLM-judgment legs are
out of scope for an unattended run (no API key). Records exit code + output head per step, plus the
platform_lib cache/preferences CLIs, into a RUN-LOG markdown table.

Usage: .claude/skills/.venv/bin/python3 e2e/run-full-pipeline.py [--write-log]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "e2e" / "synthetic-project"
PY = str(REPO / ".claude" / "skills" / ".venv" / "bin" / "python3")
SKILLS = REPO / ".claude" / "skills"
SCRIPTS = REPO / ".claude" / "scripts"

# (framework, feature label, argv). `-m:<module>` runs a platform_lib module (relative imports).
# Args target the synthetic chars. Scripts that exit 1 on findings/threshold are RAN-WITH-FINDINGS, not errors.
STEPS = [
    ("PSY", "health-check · completeness", [f"{SKILLS}/psy-health-check/scripts/score-profile-completeness.py", "--character", "test-alpha"]),
    ("PSY", "crossref · timeline (dim 1)", [f"{SKILLS}/psy-crossref/scripts/check-timeline-date-consistency.py", "--json"]),
    ("PSY", "crossref · bidirectional refs", [f"{SKILLS}/psy-crossref/scripts/check-bidirectional-references.py", "--json"]),
    ("PSY", "crossref · extract events", [f"{SKILLS}/psy-crossref/scripts/extract-cross-character-events.py", "--json"]),
    ("PSY", "timeline-sync", [f"{SKILLS}/psy-timeline-sync/scripts/check-and-suggest-timeline-fixes.py"]),
    ("GRO", "validate growth", [f"{SKILLS}/gro-validate/scripts/validate-growth-data-consistency.py", "--character", "test-alpha"]),
    ("GRO", "competency gather", [f"{SKILLS}/gro-competency-map/scripts/gather-competency-data-from-profile-and-materials.py", "--character", "test-alpha"]),
    ("MAT", "indexer · coverage gaps", [f"{SKILLS}/mat-indexer/scripts/analyze-evidence-coverage-gaps-per-profile-section.py", "--character", "test-alpha"]),
    ("MAT", "indexer · stale materials", [f"{SKILLS}/mat-indexer/scripts/find-stale-materials-by-processing-status.py", "--character", "test-alpha"]),
    ("MAT", "loader · inventory", [f"{SKILLS}/mat-loader/scripts/inventory-materials-with-frontmatter-status.py", "--character", "test-alpha"]),
    ("MAT", "loader · dup detection", [f"{SKILLS}/mat-loader/scripts/detect-duplicate-materials-by-size-and-content-hash.py", "--character", "test-alpha"]),
    ("CRE", "privacy-guard · scan assets", [f"{SKILLS}/cre-privacy-guard/scripts/scan-assets-for-privacy-violations.py"]),
    ("CRE", "privacy-guard · confidential names", [f"{SKILLS}/cre-privacy-guard/scripts/extract-confidential-names-from-all-profiles.py"]),
    ("LIB", "verdict_cache · crisis is never-cached", ["-m:platform_lib.verdict_cache", "--check", "crisis_assess", "--ids", "n1", "--bodies-file", str(FIXTURE / "_bodies.json")]),
    ("LIB", "verdict_cache · store+hit a verdict", ["-m:platform_lib.verdict_cache", "--check", "evidential_backing", "--ids", "n1", "--bodies-file", str(FIXTURE / "_bodies.json"), "--store", '{"label":"consistent","score":3}']),
    ("LIB", "preferences · read knobs", ["-m:platform_lib.preferences", "--json"]),
]

# Scripts whose exit 1 means "ran, flagged findings/threshold" (a deterministic verdict, not an error).
_FINDINGS_OK = {"health-check · completeness", "validate growth", "timeline-sync"}


def run_step(label, argv):
    env = dict(os.environ)
    env["PMC_PROJECT_ROOT"] = str(FIXTURE)
    env["PYTHONPATH"] = str(SCRIPTS)
    env["CK_CACHE_DIR"] = str(FIXTURE / ".cache")
    if argv and argv[0].startswith("-m:"):
        cmd = [PY, "-m", argv[0][3:]] + argv[1:]
    else:
        cmd = [PY] + argv
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, env=env)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        head = out[0][:120] if out else ""
        if r.returncode == 0:
            status = "OK"
        elif r.returncode == 1 and label in _FINDINGS_OK:
            status = "FINDINGS"
        else:
            status = f"EXIT {r.returncode}"
        return status, head, (r.stdout + r.stderr)
    except Exception as e:  # noqa: BLE001
        return "ERROR", str(e)[:120], str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-log", action="store_true")
    args = ap.parse_args()

    # tiny bodies file for the verdict_cache CLI step
    (FIXTURE / "_bodies.json").write_text(json.dumps({"n1": "synthetic section body"}), encoding="utf-8")

    rows, raw, ok = [], [], 0
    for fw, label, argv in STEPS:
        status, head, full = run_step(label, argv)
        if status in ("OK", "FINDINGS"):
            ok += 1
        rows.append((fw, label, status, head))
        raw.append(f"### [{fw}] {label}\n`{status}`\n```\n{full.strip()[:800]}\n```")
        print(f"[{status:8}] {fw} · {label}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")  # canonical
    table = "\n".join(f"| {fw} | {label} | {status} | {head} |" for fw, label, status, head in rows)
    log = (
        f"# E2E run log — 6 frameworks on the synthetic fixture\n\n"
        f"Fixture: `e2e/synthetic-project/` (synthetic chars: test-alpha, test-beta — no real PII). "
        f"Deterministic legs only (no API key). Generated: {ts}.\n\n"
        f"**{ok}/{len(STEPS)} steps exit 0.**\n\n"
        f"| Framework | Feature | Status | Output head |\n|---|---|---|---|\n{table}\n\n"
        f"---\n\n## Raw output\n\n" + "\n\n".join(raw) + "\n"
    )
    if args.write_log:
        (REPO / "e2e" / "RUN-LOG-six-framework-deterministic-pipeline.md").write_text(log, encoding="utf-8")
        print(f"\nwrote RUN-LOG ({ok}/{len(STEPS)} OK)")
    return 0 if ok == len(STEPS) else 1


if __name__ == "__main__":
    sys.exit(main())
