#!/usr/bin/env python3
"""Scan .claude/agent-memory/ and show stats per agent: entry count, last updated."""
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.formatters import print_table, print_json
try:
    from platform_lib.instinct_store import load_instincts, AGENT_CATEGORY_MAP
    _HAS_INSTINCTS = True
except ImportError:
    _HAS_INSTINCTS = False

AGENT_MEMORY_DIR = ROOT / ".claude" / "agent-memory"


def main():
    if not AGENT_MEMORY_DIR.exists():
        print_json({
            "agent_memory_dir": str(AGENT_MEMORY_DIR),
            "exists": False,
            "note": "No agent-memory directory found.",
        })
        sys.exit(0)

    agent_stats: dict[str, dict] = {}

    for f in AGENT_MEMORY_DIR.rglob("*.md"):
        if f.name.startswith(".") or f.name.startswith("_"):
            continue
        agent_name = f.stem

        if agent_name not in agent_stats:
            agent_stats[agent_name] = {"files": [], "total_lines": 0, "last_updated": 0.0}

        content = f.read_text(encoding="utf-8", errors="replace")
        lines = len(content.splitlines())
        mtime = f.stat().st_mtime
        agent_stats[agent_name]["files"].append(f.name)
        agent_stats[agent_name]["total_lines"] += lines
        if mtime > agent_stats[agent_name]["last_updated"]:
            agent_stats[agent_name]["last_updated"] = mtime

    if not agent_stats:
        print(f"No agent memory files found in {AGENT_MEMORY_DIR}")
        return

    instincts_by_cat = {}
    if _HAS_INSTINCTS:
        try:
            active = load_instincts(status="active")
            for inst in active:
                cat = inst.get("category", "")
                instincts_by_cat.setdefault(cat, []).append(inst)
        except (OSError, ValueError):
            pass  # advisory stats: missing/corrupt instinct store degrades to empty, not a crash

    rows = []
    for agent, stats in sorted(agent_stats.items()):
        last_dt = datetime.datetime.fromtimestamp(stats["last_updated"]).strftime("%Y-%m-%d %H:%M")
        relevant = 0
        if _HAS_INSTINCTS:
            categories = AGENT_CATEGORY_MAP.get(agent, [])
            for cat in categories:
                relevant += len(instincts_by_cat.get(cat, []))
        rows.append([
            agent,
            str(len(stats["files"])),
            str(stats["total_lines"]),
            str(relevant),
            last_dt,
        ])

    print(f"## Agent Memory Stats — {AGENT_MEMORY_DIR}\n")
    print_table(["Agent", "Files", "Lines", "Instincts", "Last Updated"], rows)


if __name__ == "__main__":
    main()
