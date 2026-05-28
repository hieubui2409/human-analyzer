"""M6 — Memory system health (deterministic gather; dry-run fix).

GOLDEN RULE #4: deterministic gather only. Scans the project's persistent memory
dir (~/.claude/projects/{encoded-root}/memory/), validating each .md memory's
frontmatter, MEMORY.md index sync (orphans / dead entries), [[name]] cross-links,
and staleness. It surfaces issues; the LLM decides which memory is truly stale.
READ-ONLY by default — --fix previews a MEMORY.md repair diff, only --apply writes.

The memory dir lives under the GLOBAL runtime tree (~/.claude), so --apply is the
one mutating path and is gated behind an explicit flag; default never writes.

Usage:
  check-memory-system-health.py [--json] [--format md|json]
                                [--fix] [--apply]

Env: CK_MEMORY_DIR overrides memory-dir discovery (tests point it at a tmp dir).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.markdown_parser import extract_frontmatter  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

REQUIRED_FIELDS = ("name", "description")
VALID_TYPES = {"user", "feedback", "project", "reference"}
STALE_DAYS = 30          # any memory older than this is flagged potentially stale
PROJECT_STALE_DAYS = 14  # project-type context moves fast → tighter window
LINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9-]*)\]\]")
# MEMORY.md index line: - [Title](slug.md) — hook
INDEX_LINK_RE = re.compile(r"\]\(([^)]+\.md)\)")


def _memory_dir() -> Path:
    env = os.environ.get("CK_MEMORY_DIR")
    if env:
        return Path(env)
    enc = str(paths.ROOT).replace("/", "-")
    return Path.home() / ".claude" / "projects" / enc / "memory"


# Module-level, monkeypatchable in tests.
MEMORY_DIR = _memory_dir()


def _age_days(p: Path) -> int:
    mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - mtime).days


def scan_memories() -> list[dict]:
    """One record per memory .md file (excluding MEMORY.md index)."""
    out: list[dict] = []
    if not MEMORY_DIR.exists():
        return out
    for f in sorted(MEMORY_DIR.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        fm = extract_frontmatter(f)
        text = f.read_text(encoding="utf-8")
        missing = [k for k in REQUIRED_FIELDS if not fm.get(k)]
        mtype = fm.get("type", "")
        out.append({
            "file": f.name,
            "name": fm.get("name", ""),
            "type": mtype,
            "missing_fields": missing,
            "invalid_type": bool(mtype) and mtype not in VALID_TYPES,
            "age_days": _age_days(f),
            "links": sorted(set(LINK_RE.findall(text))),
        })
    return out


def parse_index() -> list[str]:
    """Memory filenames referenced in MEMORY.md (in listed order)."""
    idx = MEMORY_DIR / "MEMORY.md"
    if not idx.exists():
        return []
    return INDEX_LINK_RE.findall(idx.read_text(encoding="utf-8"))


def gather() -> dict:
    mems = scan_memories()
    files = {m["file"] for m in mems}
    names = {m["name"] for m in mems if m["name"]}
    name_to_files: dict[str, list[str]] = {}
    for m in mems:
        if m["name"]:
            name_to_files.setdefault(m["name"], []).append(m["file"])

    indexed = parse_index()
    indexed_set = set(indexed)
    orphans = sorted(files - indexed_set)              # file exists, not in MEMORY.md
    dead = [f for f in indexed if f not in files]      # in MEMORY.md, no file
    duplicates = {n: fs for n, fs in name_to_files.items() if len(fs) > 1}

    broken_links = []
    for m in mems:
        for link in m["links"]:
            if link not in names:
                broken_links.append({"from": m["file"], "to": link})

    stale = []
    for m in mems:
        limit = PROJECT_STALE_DAYS if m["type"] == "project" else STALE_DAYS
        if m["age_days"] > limit:
            stale.append({"file": m["file"], "type": m["type"], "age_days": m["age_days"]})

    type_dist: dict[str, int] = {}
    for m in mems:
        type_dist[m["type"] or "(none)"] = type_dist.get(m["type"] or "(none)", 0) + 1

    invalid_fm = [m for m in mems if m["missing_fields"] or m["invalid_type"]]
    issues = (len(orphans) + len(dead) + len(broken_links)
              + len(duplicates) + len(invalid_fm))
    return {
        "memory_dir": str(MEMORY_DIR),
        "count": len(mems),
        "orphans": orphans,
        "dead_entries": dead,
        "broken_links": broken_links,
        "duplicates": duplicates,
        "stale": stale,
        "invalid_frontmatter": [
            {"file": m["file"], "missing": m["missing_fields"],
             "invalid_type": m["invalid_type"]} for m in invalid_fm],
        "type_distribution": dict(sorted(type_dist.items())),
        "issue_count": issues,
        "status": "GREEN" if issues == 0 else ("YELLOW" if issues <= 3 else "RED"),
    }


def fix_diff(data: dict) -> list[str]:
    """MEMORY.md repair = drop dead index lines (orphans need author-written hooks)."""
    idx = MEMORY_DIR / "MEMORY.md"
    if not idx.exists() or not data["dead_entries"]:
        return []
    dead = set(data["dead_entries"])
    removed = []
    for line in idx.read_text(encoding="utf-8").splitlines():
        m = INDEX_LINK_RE.search(line)
        if m and m.group(1) in dead:
            removed.append(line)
    return removed


def apply_fix(data: dict) -> int:
    """Remove dead index lines from MEMORY.md. Returns lines removed. Mutates disk."""
    idx = MEMORY_DIR / "MEMORY.md"
    dead = set(data["dead_entries"])
    if not idx.exists() or not dead:
        return 0
    kept, removed = [], 0
    for line in idx.read_text(encoding="utf-8").splitlines():
        m = INDEX_LINK_RE.search(line)
        if m and m.group(1) in dead:
            removed += 1
            continue
        kept.append(line)
    if removed:
        idx.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return removed


def render_md(data: dict) -> str:
    out = [f"# Memory System Health — {data['status']} "
           f"({data['count']} memories, {data['issue_count']} issues)\n",
           f"`{data['memory_dir']}`\n"]
    td = ", ".join(f"{k}={v}" for k, v in data["type_distribution"].items()) or "(empty)"
    out.append(f"**Type distribution:** {td}\n")

    def _section(title: str, items: list[str]):
        out.append(f"**{title}:** {len(items)}")
        if items:
            out.append("- " + "\n- ".join(items))

    _section("Orphaned files (not in MEMORY.md)", data["orphans"])
    _section("Dead index entries (no file)", data["dead_entries"])
    _section("Broken [[links]]", [f"{b['from']} → [[{b['to']}]]" for b in data["broken_links"]])
    _section("Duplicate names", [f"{n}: {', '.join(fs)}" for n, fs in data["duplicates"].items()])
    _section("Invalid frontmatter",
             [f"{m['file']}: {'missing ' + ','.join(m['missing']) if m['missing'] else ''}"
              f"{' invalid-type' if m['invalid_type'] else ''}".strip()
              for m in data["invalid_frontmatter"]])
    if data["stale"]:
        rows = [[s["file"], s["type"] or "—", str(s["age_days"])] for s in data["stale"]]
        out += ["\n## Potentially stale\n",
                markdown_table(["File", "Type", "Age (days)"], rows)]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Memory system health (M6)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--fix", action="store_true",
                    help="preview MEMORY.md repair (drop dead entries); dry-run unless --apply")
    ap.add_argument("--apply", action="store_true",
                    help="with --fix, actually write MEMORY.md (mutates global runtime)")
    args = ap.parse_args()
    data = gather()

    if args.fix:
        if args.apply:
            n = apply_fix(data)
            print(f"applied: removed {n} dead MEMORY.md entr{'y' if n == 1 else 'ies'}")
        else:
            removed = fix_diff(data)
            if removed:
                print("dry-run — would remove from MEMORY.md (add --apply to write):")
                print("\n".join(f"  - {ln}" for ln in removed))
            else:
                print("dry-run — no dead MEMORY.md entries to remove")
        return 0

    if args.json or args.format == "json":
        print(json_output(data))
    else:
        print(render_md(data))
    return 1 if data["status"] == "RED" else 0


if __name__ == "__main__":
    sys.exit(main())
