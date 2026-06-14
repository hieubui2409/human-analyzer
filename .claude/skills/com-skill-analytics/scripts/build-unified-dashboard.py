"""M1 — Unified project health dashboard (deterministic orchestration).

GOLDEN RULE #4: deterministic gather only. Runs the sibling analytics lenses (S2,
S1, S4, M5, M6) plus the external psy:health-check + mat:rescore scripts via
subprocess --json (timeout-guarded), then folds each into a traffic-light row.
It aggregates raw signals; the LLM decides what to act on. READ-ONLY.

Each check runs with a per-call timeout; a slow/failing check degrades to a single
row (timeout/error) and never hangs the dashboard. Three output formats: md
(default), json, html (self-contained, no server).

Usage:
  build-unified-dashboard.py [--by-framework] [--skip key,key]
                             [--verbose] [--format md|json|html] [--json]

Env: CK_DASHBOARD_TIMEOUT overrides per-check timeout seconds (default 30).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

PY = sys.executable
SCRIPTS_DIR = Path(__file__).resolve().parent
PSY_HC = paths.SKILLS / "psy-health-check" / "scripts" / "score-profile-completeness.py"
MAT_RS = paths.SKILLS / "mat-rescore" / "scripts" / "identify-materials-needing-rescore.py"

# source key -> (script path, args). One subprocess per source; rows reuse sources.
SOURCES = {
    "s2": (SCRIPTS_DIR / "check-skill-and-lib-health.py", ["--json"]),
    "s1": (SCRIPTS_DIR / "scan-skill-usage-and-tokens.py", ["--json", "--days", "7"]),
    "s4": (SCRIPTS_DIR / "analyze-skill-coverage-and-budget.py", ["--json"]),
    "m5": (SCRIPTS_DIR / "scan-content-pipeline-health.py", ["--json"]),
    "m6": (SCRIPTS_DIR / "check-memory-system-health.py", ["--json"]),
    "psy": (PSY_HC, ["--all", "--json"]),
    "mat": (MAT_RS, ["--json"]),
}

RANK = {"GREEN": 0, "YELLOW": 1, "RED": 2, "TIMEOUT": 1, "ERROR": 1}
EMOJI = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "TIMEOUT": "⚪", "ERROR": "⚪"}


def _timeout() -> int:
    try:
        return int(os.environ.get("CK_DASHBOARD_TIMEOUT", "30"))
    except ValueError:
        return 30


def _run_json(script: Path, args: list[str]):
    """Run a check script and parse its JSON. Returns (data, error_token).

    error_token in {None, 'timeout', 'error'}. Single subprocess boundary —
    tests monkeypatch this to inject fixture outputs without spawning processes.
    """
    if not script.exists():
        return None, "error"
    try:
        proc = subprocess.run([PY, str(script), *args], capture_output=True,
                              text=True, timeout=_timeout())
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except OSError:
        return None, "error"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError:
        return None, "error"


# --- per-domain interpreters: parsed json -> (status, summary) -----------------

def _interp_skills(j):
    skills = j.get("skills", [])
    broken = [s for s in skills if s.get("status") == "BROKEN"]
    warn = [s for s in skills if s.get("status") == "WARN"]
    ok = len(skills) - len(broken) - len(warn)
    status = "RED" if broken else ("YELLOW" if warn else "GREEN")
    return status, f"{ok} healthy, {len(warn)} warn, {len(broken)} broken"


def _interp_lib(j):
    lib = j.get("platform_lib", {})
    unused = [m for m, c in lib.items() if c == 0]
    return ("YELLOW" if unused else "GREEN",
            f"{len(unused)} unused: {', '.join(unused)}" if unused else "all modules used")


def _interp_usage(j):
    return "GREEN", f"{j.get('skills_used', 0)} skills used, {j.get('total_invocations', 0)} invocations"


def _interp_coverage(j):
    gaps, over = j.get("routing_gaps", []), j.get("over_budget", [])
    return ("YELLOW" if (gaps or over) else "GREEN",
            f"{len(gaps)} routing gap(s), {len(over)} over-budget")


def _interp_content(j):
    active, inactive = j.get("active_platforms", 0), j.get("inactive", [])
    status = "RED" if active == 0 else ("YELLOW" if inactive else "GREEN")
    return status, f"{active} active, {len(inactive)} inactive, {j.get('total_posts', 0)} posts"


def _interp_profiles(j):
    a = j.get("assessments", [])
    fca = j.get("file_count_assertion", {})
    if not a:
        return "YELLOW", "no profiles scored"
    overalls = [x.get("overall", 0) for x in a]
    avg = round(sum(overalls) / len(overalls))
    low = [o for o in overalls if o < 80]
    status = ("RED" if (fca.get("pass") is False or any(o < 50 for o in overalls))
              else ("YELLOW" if low else "GREEN"))
    return status, f"{len(a)} profiles, avg {avg}%, {len(low)} below 80%"


def _interp_materials(j):
    total = sum(len(v) for v in j.values() if isinstance(v, list))
    return ("YELLOW" if total else "GREEN",
            f"{total} need CRAAP re-eval" if total else "all materials current")


def _interp_memory(j):
    return j.get("status", "GREEN"), f"{j.get('count', 0)} memories, {j.get('issue_count', 0)} issues"


# row key -> (label, source key, interpreter). Ordered as displayed.
ROWS = [
    ("skills", "Skills", "s2", _interp_skills),
    ("platform_lib", "platform_lib", "s2", _interp_lib),
    ("profiles", "Profiles", "psy", _interp_profiles),
    ("materials", "Materials", "mat", _interp_materials),
    ("content", "Content", "m5", _interp_content),
    ("memory", "Memory", "m6", _interp_memory),
    ("usage", "Usage (7d)", "s1", _interp_usage),
    ("coverage", "Coverage", "s4", _interp_coverage),
]


def gather(skip: set[str] | None = None) -> dict:
    skip = skip or set()
    needed = {src for key, _, src, _ in ROWS if key not in skip}
    raw: dict[str, tuple] = {src: _run_json(*SOURCES[src]) for src in needed}
    rows = []
    for key, label, src, interp in ROWS:
        if key in skip:
            continue
        data, err = raw[src]
        if err:
            status, summary = err.upper(), f"check {err}"
        else:
            try:
                status, summary = interp(data)
            except (KeyError, TypeError, ValueError):
                status, summary = "ERROR", "unparseable output"
        rows.append({"key": key, "label": label, "status": status, "summary": summary})
    # Worst row wins; timeout/error count as YELLOW (degraded, not failed).
    if any(r["status"] == "RED" for r in rows):
        overall = "RED"
    elif any(RANK.get(r["status"], 0) >= 1 for r in rows):
        overall = "YELLOW"
    else:
        overall = "GREEN"
    return {"overall": overall, "rows": rows, "raw": {k: v[0] for k, v in raw.items()}}


def framework_view(raw: dict) -> list[dict]:
    """Per-framework scorecard from S2 (health) + S1 (usage) + S4 (tokens)."""
    fws = ["MAT", "PSY", "CRE", "GRO", "ORC", "COM", "EVL"]
    s2 = raw.get("s2") or {}
    s1 = raw.get("s1") or {}
    s4 = raw.get("s4") or {}
    health = {fw.upper(): a for fw, a in (s2.get("frameworks") or {}).items()}
    usage_ct: dict[str, int] = {}
    for r in s1.get("rows", []):
        usage_ct[r.get("framework", "")] = usage_ct.get(r.get("framework", ""), 0) + r.get("count", 0)
    tok: dict[str, int] = {}
    for s in s4.get("skills", []):
        tok[s.get("framework", "")] = tok.get(s.get("framework", ""), 0) + s.get("tokens", 0)
    out = []
    for fw in fws:
        h = health.get(fw, {})
        out.append({
            "framework": fw,
            "skills": h.get("skills", 0),
            "broken": h.get("BROKEN", 0),
            "warn": h.get("WARN", 0),
            "invocations": usage_ct.get(fw, 0),
            "skill_md_tokens": tok.get(fw, 0),
        })
    return out


def render_md(data: dict, by_framework: bool, verbose: bool) -> str:
    head = f"# Project Health Dashboard — {EMOJI[data['overall']]} {data['overall']}\n"
    rows = [[EMOJI.get(r["status"], "⚪"), r["label"], r["summary"]] for r in data["rows"]]
    out = [head, markdown_table(["", "Domain", "Summary"], rows)]
    if by_framework:
        fv = framework_view(data["raw"])
        frows = [[f["framework"], str(f["skills"]), str(f["broken"]), str(f["warn"]),
                  str(f["invocations"]), f"{f['skill_md_tokens'] // 1000}K"] for f in fv]
        out += ["\n## By Framework\n",
                markdown_table(["FW", "Skills", "Broken", "Warn", "Inv(7d)", "SKILL.md"], frows)]
    if verbose:
        out.append("\n## Raw\n```json\n" + json_output(data["raw"]) + "\n```")
    return "\n".join(out)


def render_html(data: dict, by_framework: bool) -> str:
    color = {"GREEN": "#1a7f37", "YELLOW": "#9a6700", "RED": "#cf222e",
             "TIMEOUT": "#6e7781", "ERROR": "#6e7781"}
    trs = "".join(
        f'<tr><td style="text-align:center">{EMOJI.get(r["status"], "⚪")}</td>'
        f'<td><b>{r["label"]}</b></td>'
        f'<td style="color:{color.get(r["status"], "#6e7781")}">{r["summary"]}</td></tr>'
        for r in data["rows"])
    fw_html = ""
    if by_framework:
        fv = framework_view(data["raw"])
        fw_rows = "".join(
            f'<tr><td>{f["framework"]}</td><td>{f["skills"]}</td><td>{f["broken"]}</td>'
            f'<td>{f["warn"]}</td><td>{f["invocations"]}</td><td>{f["skill_md_tokens"] // 1000}K</td></tr>'
            for f in fv)
        fw_html = (
            '<h2>By Framework</h2><table><thead><tr><th>FW</th><th>Skills</th>'
            '<th>Broken</th><th>Warn</th><th>Inv(7d)</th><th>SKILL.md</th></tr></thead>'
            f'<tbody>{fw_rows}</tbody></table>')
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Project Health Dashboard</title>
<style>
 body{{font:15px/1.5 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#1f2328}}
 h1{{font-size:1.5rem}} table{{border-collapse:collapse;width:100%;margin:1rem 0}}
 th,td{{border:1px solid #d0d7de;padding:.5rem .75rem;text-align:left}}
 th{{background:#f6f8fa}}
</style></head><body>
<h1>Project Health Dashboard — {EMOJI[data['overall']]} {data['overall']}</h1>
<table><thead><tr><th></th><th>Domain</th><th>Summary</th></tr></thead>
<tbody>{trs}</tbody></table>
{fw_html}
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified project health dashboard (M1)")
    ap.add_argument("--by-framework", action="store_true")
    ap.add_argument("--skip", help="comma-separated row keys to skip "
                                    "(skills,platform_lib,profiles,materials,content,memory,usage,coverage)")
    ap.add_argument("--verbose", action="store_true", help="append raw JSON of each check")
    ap.add_argument("--format", choices=["md", "json", "html"], default="md")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    skip = {s.strip() for s in args.skip.split(",")} if args.skip else set()
    data = gather(skip)
    if args.json or args.format == "json":
        print(json_output({"overall": data["overall"], "rows": data["rows"]}))
    elif args.format == "html":
        print(render_html(data, args.by_framework))
    else:
        print(render_md(data, args.by_framework, args.verbose))
    return 1 if data["overall"] == "RED" else 0


if __name__ == "__main__":
    sys.exit(main())
