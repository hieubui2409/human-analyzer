"""S2 — Skill + platform_lib infrastructure health (deterministic static scan).

GOLDEN RULE #4: deterministic gather only. Verifies every PROJECT-OWNED framework
skill is structurally sound (SKILL.md parseable, scripts syntactically valid) and
reports platform_lib module weight (importer count). It NEVER decides whether a
skill is "good" — it flags BROKEN (syntax error) / WARN (missing pieces) for the
LLM to adjudicate. READ-ONLY. Scope = 6 framework prefixes, not ck skills.

Usage:
  check-skill-and-lib-health.py [--json] [--format md|json] [--perf]
                                [--framework psy|orc|cre|gro|mat|com] [--verbose]
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.markdown_parser import extract_frontmatter  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

SKILLS_DIR = paths.ROOT / ".claude" / "skills"
PLATFORM_LIB = paths.ROOT / ".claude" / "scripts" / "platform_lib"
TELEMETRY = paths.ROOT / ".claude" / "telemetry"
FRAMEWORKS = ["mat", "psy", "cre", "gro", "orc", "com"]


def _py_syntax_ok(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except (SyntaxError, OSError, UnicodeDecodeError):
        return False


def _sh_syntax_ok(path: Path) -> bool:
    try:
        return subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0
    except OSError:
        return False


def framework_skill_dirs(only: str | None = None):
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        prefix = d.name.split("-", 1)[0]
        if prefix not in FRAMEWORKS:
            continue
        if only and prefix != only:
            continue
        yield prefix, d


def check_skill(d: Path) -> dict:
    """Return {status, issues[]} for one skill dir. status in OK|WARN|BROKEN."""
    issues: list[str] = []
    skill_md = d / "SKILL.md"
    if not skill_md.exists():
        return {"status": "BROKEN", "issues": ["no SKILL.md"], "type": "?"}
    fm = extract_frontmatter(skill_md)
    if not fm.get("name") or not fm.get("description"):
        issues.append("frontmatter missing name/description")
    scripts = sorted([*d.glob("scripts/*.py"), *d.glob("scripts/*.sh")])
    skill_type = "script-backed" if scripts else "prompt-only"
    broken = False
    for s in scripts:
        ok = _py_syntax_ok(s) if s.suffix == ".py" else _sh_syntax_ok(s)
        if not ok:
            issues.append(f"syntax error: scripts/{s.name}")
            broken = True
    if skill_type == "prompt-only" and skill_md.stat().st_size > 20_000:
        issues.append("prompt-only SKILL.md unusually large (>20KB)")
    status = "BROKEN" if broken else ("WARN" if issues else "OK")
    return {"status": status, "issues": issues, "type": skill_type}


def importer_counts() -> dict[str, int]:
    """Count framework scripts importing each platform_lib module."""
    counts: dict[str, int] = {m.stem: 0 for m in PLATFORM_LIB.glob("*.py") if m.stem != "__init__"}
    for _, d in framework_skill_dirs():
        for s in d.glob("scripts/*.py"):
            try:
                tree = ast.parse(s.read_text(encoding="utf-8"))
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                mod = None
                if isinstance(node, ast.ImportFrom) and node.module:
                    mod = node.module
                elif isinstance(node, ast.Import):
                    mod = node.names[0].name if node.names else None
                if mod and mod.startswith("platform_lib."):
                    name = mod.split(".", 2)[1]
                    if name in counts:
                        counts[name] += 1
    return counts


def perf_summary() -> dict[str, dict]:
    """p50/p95 ms per script from script-telemetry.jsonl (graceful if absent)."""
    f = TELEMETRY / "script-telemetry.jsonl"
    if not f.exists():
        return {}
    by_script: dict[str, list[int]] = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
            by_script.setdefault(rec.get("script", "?"), []).append(int(rec.get("ms", 0)))
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    out = {}
    for k, v in by_script.items():
        v.sort()
        out[k] = {"n": len(v), "p50": v[len(v) // 2], "p95": v[min(len(v) - 1, int(len(v) * 0.95))]}
    return out


def gather(only: str | None, perf: bool) -> dict:
    by_fw: dict[str, dict] = {}
    skills: list[dict] = []
    for prefix, d in framework_skill_dirs(only):
        res = check_skill(d)
        skills.append({"skill": d.name, "framework": prefix, **res})
        agg = by_fw.setdefault(prefix, {"skills": 0, "OK": 0, "WARN": 0, "BROKEN": 0})
        agg["skills"] += 1
        agg[res["status"]] += 1
    lib = importer_counts()
    out = {"frameworks": by_fw, "skills": skills, "platform_lib": lib}
    if perf:
        out["perf"] = perf_summary()
    return out


def render_md(data: dict) -> str:
    rows = [[fw.upper(), str(a["skills"]), str(a["OK"]), str(a["WARN"]), str(a["BROKEN"])]
            for fw, a in sorted(data["frameworks"].items())]
    out = ["# Skill Infrastructure Health\n",
           markdown_table(["Framework", "Skills", "OK", "Warn", "Broken"], rows)]
    lib_rows = [[m, str(c), "critical" if c >= 20 else ("unused" if c == 0 else "ok")]
                for m, c in sorted(data["platform_lib"].items(), key=lambda kv: -kv[1])]
    out += ["\n## platform_lib modules\n", markdown_table(["Module", "Importers", "Status"], lib_rows)]
    broken = [s for s in data["skills"] if s["status"] != "OK"]
    if broken:
        out.append("\n## Issues\n")
        for s in broken:
            out.append(f"- **{s['skill']}** [{s['status']}]: {'; '.join(s['issues'])}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill + platform_lib infrastructure health (S2)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--perf", action="store_true", help="include script perf (needs telemetry)")
    ap.add_argument("--framework", choices=FRAMEWORKS)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    data = gather(args.framework, args.perf)
    if args.json or args.format == "json":
        print(json_output(data))
    else:
        print(render_md(data))
    # exit 1 if any broken skill (CI signal)
    return 1 if any(s["status"] == "BROKEN" for s in data["skills"]) else 0


if __name__ == "__main__":
    sys.exit(main())
